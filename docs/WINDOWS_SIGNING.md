# Windows credential preparation

A local Mac is not required to prepare manual signing assets. With active paid
Apple Developer Program membership and the required role, use Windows OpenSSL
to generate an encrypted RSA-2048 private key and PKCS#10 CSR, upload only the
CSR to Apple, download the Apple Distribution certificate and package it with
the matching private key into a password-protected PKCS#12 file. Actual Xcode
compilation/signing still runs on the GitHub-hosted Mac.

The previously documented Mac Keychain export is an alternative for an existing
identity, not a prerequisite for making a new identity on Windows. A certificate
download alone contains no private key and cannot replace the original key.

Keep assets in a private directory outside the research and public repositories.
Generate strong random passwords; use protected local storage such as Windows
DPAPI for unattended preparation, never a plaintext command/log or source file.
DPAPI storage is tied to the Windows user/machine context and is not a portable
credential backup by itself. Never put an Apple account password or 2FA code in CI.

Use OpenSSL's encrypted key/CSR tooling and `pkcs12 -export`. Verify the issued
certificate's public key matches the CSR key before packaging. Apple keychain
interoperability may require explicit P12 encryption/MAC options; the setup uses
`-keypbe PBE-SHA1-3DES -certpbe PBE-SHA1-3DES -macalg sha1`, with a strong random
password. That compatibility choice does not replace encryption of the local
key or protection of the P12 in GitHub secrets.

When automating from PowerShell, avoid passing a password through a native pipe
unless its exact encoding/newline behavior is controlled. MSYS OpenSSL can retain
a carriage return from PowerShell stdin. Use transient process environment
variables for OpenSSL's `env:` password source and remove them in finally; upload
secret values through process stdin without appending line endings. Do not use
literal passwords as process command arguments. Never print secret values.

Register only the intended research iPad in Apple's portal, create the explicit
App ID and an Ad Hoc profile with the matching certificate/device, then configure
the four secrets in [SIGNING.md](SIGNING.md). UDIDs belong in the portal and the
profile required for provisioning, not research logs or public source control.
Sideloadly's device copy button can copy the selected device's UDID locally for
direct portal entry; no sideload operation or account login is necessary merely
to use that button.

Sideloadly is not needed for CSR/P12 generation or the hosted build. Its default
Apple ID signing is a separate provisioning context, not a substitute for this
workflow's Apple Distribution identity. A later physical installation and launch
must be observed separately. No Developer Mode/trust/security changes are part
of asset preparation.

Before signed execution, review public artifact visibility in SIGNING.md. An
ad hoc IPA necessarily contains its embedded provisioning metadata.

References: [OpenSSL CSR](https://docs.openssl.org/3.5/man1/openssl-req/),
[OpenSSL PKCS#12](https://docs.openssl.org/3.5/man1/openssl-pkcs12/),
[Apple ad hoc profiles](https://developer.apple.com/help/account/provisioning-profiles/create-an-ad-hoc-provisioning-profile/),
[Sideloadly device copy button](https://sideloadly.io/changelog).
