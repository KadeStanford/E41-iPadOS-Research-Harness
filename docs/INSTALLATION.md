# Windows installation handoff

No IPA has been installed or launched by this project setup. A successful build
is not a permission-test result. USB metadata access/trust does not prove app
installation authority. Do not use the unsigned artifact for installation.

An ad hoc IPA needs an unexpired matching distribution identity/profile with
this iPad registered, the expected bundle ID and the device's normal platform
requirements satisfied. Apple documents installation with Xcode or Apple
Configurator on **Mac** in its [registered-device distribution guide](https://developer.apple.com/documentation/xcode/distributing-your-app-to-registered-devices).
Those are not Windows applications; the Apple Devices Windows app is not assumed
to provide arbitrary IPA deployment.

The user reports an existing Sideloadly installation. Its publisher lists Normal
Install separately from Apple ID Sideload and ad hoc signing. With a properly
signed ad hoc IPA, inspect Advanced Options > Signing Mode > Normal Install
(no re-signing) if the installed version provides it. Select only the intended
research device and verified IPA; disable injection, bundle changes, tweaks and
other modifications. An unsigned/ad-hoc-local signature is not an Apple
distribution identity. Default Apple ID Sideload re-signs with a different
provisioning context and may change expiry, bundle and entitlements: it would be
a different experimental artifact and must not be silently substituted.

Sideloadly compatibility with this installation and iPadOS build was not tested.
No third-party application was launched or credentials supplied during CI setup.
If installation asks for Developer Mode, new trust, a profile, a security change
or driver replacement, stop for separate approval; do not change it automatically.
If existing policy rejects installation, record the sanitized error and stop.
No restore/update/recovery action is part of this procedure.

After an authorized installation, verify actual launch on the physical iPad and
only then run the README's synthetic procedure. Record CI run/commit, IPA hash,
actual signing/distribution mode, runtime and sanitized outcomes separately.
Never export unrelated documents or identifiers.

Publisher references: [Sideloadly supported modes](https://sideloadly.io/),
[FAQ and provisioning differences](https://sideloadly.io/faq).
