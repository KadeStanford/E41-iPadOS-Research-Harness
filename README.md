# E41 iPadOS Research Harness

Ordinary sandboxed SwiftUI app using documented document-picker APIs and a
25-byte synthetic fixture. No private APIs, custom entitlements, networking,
vulnerability probes or security-setting changes. Copied from the preserved E41
harness; only standalone project settings differ.

Bundle ID: `com.kadestanford.E41ResearchHarness`. Deployment target: iOS/iPadOS
16.0. CI: `macos-15`, explicitly selected Xcode 26.2. The workflow checks the
installed iphoneos SDK is at least 26 and records actual versions. Hosted images
change: reproducible commands do not imply byte-identical compiler output.

## Build

Actions > Build E41 iPadOS harness > Run workflow > unsigned (default).
Relevant application, project, script and workflow pushes/PRs also build;
documentation-only changes do not. Workflow: `.github/workflows/build-ios.yml`.
Official Actions are pinned to verified commit SHAs; token permission is
`contents: read`. On a compatible Mac:

```bash
DEVELOPER_DIR=/Applications/Xcode_26.2.app/Contents/Developer bash scripts/build.sh
```

Download artifact `E41-UNSIGNED-NOT-INSTALLABLE`: a physical-device Release
`.app.zip`, toolchain metadata and SHA-256. **It is not an installable IPA.**
CI checks project references/scheme, compiles Swift with the iphoneos SDK, and
checks arm64, bundle ID and physical platform. Unsigned diagnostics are separate.
Compilation is not app launch, installation or permission testing.

Recorded unsigned runs: [build status](docs/BUILD_STATUS.md).
Signed IPA export and verification also passed: [signed build and download](docs/SIGNED_BUILD_STATUS.md).

## Signing and installation

See [Signing](docs/SIGNING.md) and [Installation](docs/INSTALLATION.md).
Manual signed mode also performs unsigned validation, then requires four secrets,
archives/exports ad hoc (`release-testing`), and verifies signature, profile,
bundle, architecture and entitlements. No automatic portal login or provisioning
updates. Signed export has passed; physical installation and permission testing
remain unperformed.

## Synthetic-only procedure

Run own-container baseline twice. Export the generated E41-fixture.txt into a
dedicated test folder. Open only that fixture twice; cancel the picker twice.
Save only displayed sanitized JSON. Cancellation means no selected resource,
not proof of sandbox denial. False security-scope start prevents a read in this
harness and does not prove an unauthorized read would fail.

Events contain sequence, operation, outcome, scope boolean and optional error
domain/code; the display adds runtime and system version. Paths, contents,
bookmarks, identifiers and error userInfo are not logged. Physical permission
execution remains unperformed. No exploit or kernel-mechanism conclusion follows.
