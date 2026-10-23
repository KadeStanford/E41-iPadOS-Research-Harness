# Signed IPA verified — 2026-10-23

Apple Distribution signing assets were prepared on Windows with OpenSSL,
then used by the hosted Xcode runner. A local Mac was not required. All four
required repository secret names are configured; no values are published here.
The explicit E41 App ID and a separate ad hoc profile were created, selecting
only the research iPad. Existing certificates and profiles were left unchanged.

[Successful signed run 39940637430](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/actions/runs/39940637430)
built commit `8e9f92e511f526967739d807eb949900adb3a156` using the workflow's
macos-15 / Xcode 26.2 selection. Unsigned compilation, manual signed archive,
ad hoc export, final signature/profile verification, artifact upload and cleanup
all passed.

[Download E41-SIGNED-ADHOC](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/actions/runs/39940637430/artifacts/12495742818).
The artifact contains `export/E41.ipa` and `signed-verification.json`, retained
three days. GitHub sign-in may be required. Public repository artifact visibility
applies: an ad hoc IPA necessarily embeds its device-registration profile.

IPA SHA-256:

```text
99897427619ab6b386ff54e5f1b1091bbe7a562d911a715953ede9e96f6dcff2
```

The macOS runner verified the strict code signature, expected bundle identifier,
arm64 architecture, profile/team match, allowed entitlements and signing
certificate membership in the profile. Independent Windows inspection confirmed
the downloaded hash equals the runner's record, expected iPhoneOS app/arm64
executable, embedded Mach-O signature structure, and exact byte match of the
embedded profile to the privately selected profile. Windows structure checks
complement, rather than replace, Apple's macOS signature verification.

[Earlier signed run 39940367935](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/actions/runs/39940367935)
reached final exported-IPA verification but failed there; it published no signed
artifact. The verifier was corrected to extract with Apple's ditto (preserving
bundle file modes/symlinks) and use `--extract-certificates=PREFIX` so the optional
argument is not interpreted as another code object. The first verifier reported
only a generic stage error, so these two compatibility corrections were applied
together; the failed subcommand was not independently isolated. The next full
signed run passed. No signing requirement was bypassed or verification disabled.

**Physical installation, app launch and document-permission tests remain
unperformed.** A signed artifact is not proof that the iPad accepts or runs it.
Follow [installation handoff](INSTALLATION.md), stopping before any new Developer
Mode/trust/security change. No device settings or firmware were changed during
signing preparation. This is an ordinary sandboxed public-API research app.

For future builds: push relevant code/project/script changes for unsigned CI;
manually dispatch main with mode signed for another signed artifact. Certificate
and profile expiry/revocation still apply. See [Windows signing](WINDOWS_SIGNING.md)
and [asset setup](SIGNING.md) for renewal. Never commit/export raw credentials in
documentation or build artifacts.
