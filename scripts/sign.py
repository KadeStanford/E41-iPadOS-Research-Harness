"""Manual distribution using user-provided Apple credentials; never prints tool output.

Secrets and verbose signing logs stay in RUNNER_TEMP and are removed in finally
and in the workflow's always() cleanup. No provisioning updates or portal login.
"""
from pathlib import Path
import base64
import datetime as dt
import hashlib
import json
import os
import plistlib
import re
import secrets
import shutil
import subprocess
import sys
import zipfile

BUNDLE = 'com.kadestanford.E41ResearchHarness'
TMP = Path(os.environ['RUNNER_TEMP'])
PRIVATE = TMP/'E41-signing'
KEYCHAIN = TMP/'E41-signing.keychain-db'
PROFILE_DIRS = [Path.home()/'Library/MobileDevice/Provisioning Profiles',
                Path.home()/'Library/Developer/Xcode/UserData/Provisioning Profiles']
STAGE = 'credential preflight'

def run(*args):
    # Capture both streams: Xcode output can include profile names, team identity
    # and local signing paths. Do not expose it in public Actions logs/artifacts.
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError('Apple tool failed during '+STAGE+'; check valid matching signing assets')
    return p.stdout

def check_profile(raw, team):
    p = plistlib.loads(run('security','cms','-D','-i',str(raw)))
    assert p['ExpirationDate'] > dt.datetime.now(dt.timezone.utc).replace(tzinfo=None), 'Expired profile'
    assert p['TeamIdentifier'] == [team], 'Profile team mismatch'
    e = p['Entitlements']
    assert e['application-identifier'].split('.',1)[1] == BUNDLE, 'Explicit App ID mismatch'
    assert e.get('com.apple.developer.team-identifier') == team, 'Entitlement team mismatch'
    assert e.get('get-task-allow') is False, 'Distribution profile required'
    assert p.get('ProvisionedDevices') and not p.get('ProvisionsAllDevices'), 'Registered-device ad hoc profile required'
    assert 'iOS' in p['Platform'], 'iOS profile required'
    assert re.fullmatch(r'[A-Fa-f0-9-]{36}',p['UUID']), 'Invalid profile UUID'
    return p

try:
    names = ('APPLE_CERTIFICATE_P12_BASE64','APPLE_CERTIFICATE_PASSWORD',
             'APPLE_PROVISIONING_PROFILE_BASE64','APPLE_TEAM_ID')
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise ValueError('Missing repository secrets: '+', '.join(missing))
    team = os.environ['APPLE_TEAM_ID']
    assert re.fullmatch(r'[A-Z0-9]{10}',team), 'Invalid team ID format'
    PRIVATE.mkdir(mode=0o700)
    cert = PRIVATE/'certificate.p12'
    raw = PRIVATE/'profile.mobileprovision'
    cert.write_bytes(base64.b64decode(os.environ['APPLE_CERTIFICATE_P12_BASE64'],validate=True))
    raw.write_bytes(base64.b64decode(os.environ['APPLE_PROVISIONING_PROFILE_BASE64'],validate=True))
    profile = check_profile(raw,team)
    STAGE = 'temporary keychain import'
    password = secrets.token_urlsafe(32)
    run('security','create-keychain','-p',password,str(KEYCHAIN))
    run('security','set-keychain-settings','-lut','21600',str(KEYCHAIN))
    run('security','unlock-keychain','-p',password,str(KEYCHAIN))
    run('security','import',str(cert),'-P',os.environ['APPLE_CERTIFICATE_PASSWORD'],
        '-A','-t','cert','-f','pkcs12','-k',str(KEYCHAIN))
    run('security','set-key-partition-list','-S','apple-tool:,apple:,codesign:',
        '-s','-k',password,str(KEYCHAIN))
    # Isolated ephemeral hosted runner only; never a self-hosted login keychain.
    run('security','list-keychains','-d','user','-s',str(KEYCHAIN))
    identities = run('security','find-identity','-v','-p','codesigning',str(KEYCHAIN)).decode()
    usable = [hashlib.sha1(c).hexdigest().upper() for c in profile['DeveloperCertificates']
              if hashlib.sha1(c).hexdigest().upper() in identities
              and re.search(r'"Apple Distribution:',identities)]
    assert len(usable) == 1, 'Need one matching valid Apple Distribution certificate and private key'
    for directory in PROFILE_DIRS:
        directory.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(raw,directory/'E41-ci.mobileprovision')
    STAGE = 'signed Release archive'
    archive = PRIVATE/'E41.xcarchive'
    run('xcodebuild','-project','E41.xcodeproj','-scheme','E41','-configuration','Release',
        '-destination','generic/platform=iOS','-sdk','iphoneos','-archivePath',str(archive),
        'CODE_SIGN_STYLE=Manual','DEVELOPMENT_TEAM='+team,'CODE_SIGN_IDENTITY='+usable[0],
        'PROVISIONING_PROFILE_SPECIFIER='+profile['UUID'],
        'OTHER_CODE_SIGN_FLAGS=--keychain '+str(KEYCHAIN),'archive')
    options = PRIVATE/'ExportOptions.plist'
    options.write_bytes(plistlib.dumps({'method':'release-testing','destination':'export',
        'teamID':team,'signingStyle':'manual','signingCertificate':usable[0],
        'provisioningProfiles':{BUNDLE:profile['UUID']},'stripSwiftSymbols':True}))
    STAGE = 'ad hoc IPA export (release-testing)'
    run('xcodebuild','-exportArchive','-archivePath',str(archive),'-exportPath','build/export',
        '-exportOptionsPlist',str(options))
    ipa = Path('build/export/E41.ipa')
    assert ipa.is_file(), 'Expected E41.ipa absent'
    STAGE = 'exported IPA verification'
    extracted = PRIVATE/'verified'
    with zipfile.ZipFile(ipa) as z:
        for n in z.namelist():
            assert not n.startswith('/') and '..' not in Path(n).parts, 'Unsafe IPA member'
        z.extractall(extracted)
    apps = list((extracted/'Payload').glob('*.app'))
    assert len(apps)==1 and apps[0].name=='E41.app', 'Unexpected IPA application'
    app = apps[0]
    info = plistlib.loads((app/'Info.plist').read_bytes())
    assert info['CFBundleIdentifier']==BUNDLE and info['CFBundleSupportedPlatforms']==['iPhoneOS']
    run('lipo','-verify_arch','arm64',str(app/'E41'))
    run('codesign','--verify','--deep','--strict',str(app))
    embedded = check_profile(app/'embedded.mobileprovision',team)
    assert embedded['UUID']==profile['UUID'], 'Exported profile mismatch'
    ent = plistlib.loads(run('codesign','-d','--entitlements',':-',str(app)))
    assert ent['application-identifier']==profile['Entitlements']['application-identifier']
    assert ent['com.apple.developer.team-identifier']==team and not ent.get('get-task-allow',False)
    assert set(ent) <= {'application-identifier','com.apple.developer.team-identifier',
                        'keychain-access-groups','get-task-allow','beta-reports-active'}, 'Unexpected entitlement'
    for group in ent.get('keychain-access-groups',[]):
        assert group==ent['application-identifier'], 'Unexpected keychain group'
    prefix = str(PRIVATE/'signer-')
    run('codesign','-d','--extract-certificates',prefix,str(app))
    assert (PRIVATE/'signer-0').read_bytes() in profile['DeveloperCertificates'], 'Signer not in profile'
    Path('build/signed-verification.json').write_text(json.dumps({
        'bundle_identifier':BUNDLE,'distribution':'ad_hoc_release_testing',
        'arm64':True,'signature_verified':True,'profile_matches':True,
        'entitlements_checked':True,'sha256':hashlib.sha256(ipa.read_bytes()).hexdigest(),
        'physical_installation':'not performed','permission_tests':'not performed'},indent=2)+'\n')
    print('Signed IPA signature, bundle, architecture, profile and entitlements verified. Installation untested.')
except Exception as e:
    # Assertions/messages are ours; no subprocess output or secret values.
    print('Signing failed during '+STAGE+': '+str(e),file=sys.stderr)
    sys.exit(1)
finally:
    subprocess.run(['security','delete-keychain',str(KEYCHAIN)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for directory in PROFILE_DIRS:
        (directory/'E41-ci.mobileprovision').unlink(missing_ok=True)
    shutil.rmtree(PRIVATE,ignore_errors=True)
