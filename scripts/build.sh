#!/bin/bash
set -euo pipefail
mkdir -p build
test "$(xcrun --sdk iphoneos --show-sdk-version | cut -d. -f1)" -ge 26 || { echo 'iOS SDK 26 or newer required'; exit 1; }
xcodebuild -version | tee build/toolchain.txt
xcrun --sdk iphoneos --show-sdk-version | tee -a build/toolchain.txt
python3 scripts/validate.py
xcodebuild -list -project E41.xcodeproj
xcodebuild -project E41.xcodeproj -scheme E41 -configuration Release \
  -destination 'generic/platform=iOS' -sdk iphoneos -derivedDataPath build/DerivedData \
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO build | tee build/unsigned-build.log
APP=build/DerivedData/Build/Products/Release-iphoneos/E41.app
test -d "$APP"
file "$APP/E41" | tee build/binary.txt
lipo "$APP/E41" -verify_arch arm64
python3 - "$APP/Info.plist" <<'PY'
import plistlib,sys
p=plistlib.load(open(sys.argv[1],'rb'))
assert p['CFBundleIdentifier']=='com.kadestanford.E41ResearchHarness'
assert p['CFBundleSupportedPlatforms']==['iPhoneOS']
assert p['DTPlatformName']=='iphoneos'
print('Physical-device platform and bundle verified; unsigned app is not installable')
PY
ditto -c -k --keepParent "$APP" build/E41-UNSIGNED-NOT-INSTALLABLE.app.zip
shasum -a 256 build/E41-UNSIGNED-NOT-INSTALLABLE.app.zip > build/unsigned-sha256.txt
