"""Dependency-free project consistency checks; Swift compilation is a separate CI step."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

r = Path(__file__).resolve().parents[1]
p = (r/'E41.xcodeproj/project.pbxproj').read_text()
defined = set(re.findall(r'^\s*([A-F0-9]{24}) =', p, re.M))
referenced = set(re.findall(r'\b[A-F0-9]{24}\b', p))
assert defined == referenced, 'Unresolved project object references'
scheme = ET.parse(r/'E41.xcodeproj/xcshareddata/xcschemes/E41.xcscheme')
for ref in scheme.findall('.//BuildableReference'):
    assert ref.attrib['BlueprintIdentifier'] in defined
    assert ref.attrib['BuildableName'] == 'E41.app'
for name in ('ContentView.swift', 'E41App.swift'):
    assert (r/'E41'/name).is_file() and name in p
assert 'com.kadestanford.E41ResearchHarness' in p
assert 'CODE_SIGN_ENTITLEMENTS' not in p
assert 'SWIFT_OPTIMIZATION_LEVEL = "-O"' in p
for pattern in ('*.p12','*.mobileprovision','*.key','*.pem','*.ipa'):
    assert not list((r/'E41').rglob(pattern))
print('Project references, shared scheme, sources, Release optimization and no custom entitlements verified')
