# Recorded CI validation — 2026-10-23

Repository: [KadeStanford/E41-iPadOS-Research-Harness](https://github.com/KadeStanford/E41-iPadOS-Research-Harness).
Workflow: [build-ios.yml](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/blob/main/.github/workflows/build-ios.yml).

| Run | Event / source commit | Result |
| --- | --- | --- |
| [39937846029](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/actions/runs/39937846029) | push / 5ca5a99 | Swift build succeeded; post-build lipo arguments were reversed, job failed |
| [39938020143](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/actions/runs/39938020143) | push / 0aa6900 | Unsigned build and artifact verification passed |
| [39938021005](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/actions/runs/39938021005) | manual unsigned / 0aa6900 | Unsigned build and artifact verification passed |

Observed runner: macos-15; Xcode 26.2 (17C52); iphoneos SDK 26.2. Release,
generic physical iOS destination, arm64, minimum OS 16.0. The intended device's
26.0 OS is above the deployment target; building against SDK 26.2 is not a
physical compatibility or launch observation.

[Unsigned artifact](https://github.com/KadeStanford/E41-iPadOS-Research-Harness/actions/runs/39938021005/artifacts/12494563060)
(`E41-UNSIGNED-NOT-INSTALLABLE`, retention 14 days; GitHub sign-in may be required).
The app ZIP inside the Actions artifact has SHA-256:

```text
2ee4d401fb5182873355d06878de174355eee203eeff3d855aca9d1f90d0f8a5
```

The downloaded app ZIP matched the runner's hash. Independent host inspection
confirmed expected bundle ID/platform, arm64 Mach-O executable, LC_BUILD_VERSION
iOS / minimum 16.0 / SDK 26.2, absent LC_CODE_SIGNATURE and absent embedded
provisioning profile. This validates an **unsigned application**, not an
installable IPA. Artifact expiry does not invalidate preserved hashes/logs.

Nonfatal Xcode warnings: AppIntents metadata skipped (no AppIntents dependency),
and all interface orientations should be supported unless full-screen is
required. Native UI behavior has not been tested. Official upload-artifact v4
also emits Node deprecation warnings; uploads succeeded. No Swift error was
observed. No source changes were needed; the lipo check alone was corrected.

No repository signing secrets were present at setup. Signed archive/export,
target device inclusion, installation, launch and actual permission testing are
unverified. Follow [signing setup](SIGNING.md) before manual signed mode.
An Apple Developer account is user-reported; paid membership/assets are unknown.
No device operations occurred during this pipeline work.
