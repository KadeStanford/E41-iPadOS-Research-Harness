# Manual Apple signing setup

Update 2026-10-23: the four secrets are configured and signed export/verification
has passed. See [signed build status](SIGNED_BUILD_STATUS.md). The initial-state
description below is preserved as setup history; actual installation is untested.

Status: no repository signing secrets were present at initial setup. Membership,
certificate possession and device registration are unknown. An Apple ID alone
does not establish paid Developer Program membership or ad hoc signing rights.
Unsigned compilation proceeds independently; signed CI has not been executed.

1. Sign in personally at [Apple Developer Account](https://developer.apple.com/account/).
   Confirm active Apple Developer Program membership and access to Certificates,
   Identifiers & Profiles. Distribution certificate creation requires the proper
   role (Account Holder/Admin). Do not send credentials to chat or put them in CI.
2. Register the explicit App ID `com.kadestanford.E41ResearchHarness`, with no
   extra capabilities. Record its team ID privately. If the ID is unavailable,
   update the project AND both scripts' expected identifiers before building.
3. Obtain an **Apple Distribution** signing identity including its private key.
   An existing matching identity can be exported from Xcode Settings > Accounts >
   Manage Certificates or Keychain Access as a password-protected `.p12`.
   A downloaded `.cer` alone is insufficient. For a new identity use Apple’s
   [CSR procedure](https://developer.apple.com/help/account/certificates/create-a-certificate-signing-request/),
   add Apple Distribution under Certificates in the portal, download/import the
   certificate on the computer that holds the CSR private key, then export both
   as `.p12`. Alternatively, generate the CSR/private key and package the issued
   certificate on Windows using OpenSSL: see [Windows signing](WINDOWS_SIGNING.md).
   A local Mac is not required for credential preparation; hosted Xcode still
   performs actual application signing.
4. Register the research iPad in the portal's Devices section using its identifier
   privately. Never post it to this repository, issue, chat or build log.
5. Profiles > + > Distribution > **Ad Hoc**: choose the exact App ID, matching
   Apple Distribution certificate and registered iPad. Generate/download the
   `.mobileprovision`. Do not use App Store, development or enterprise profiles.
6. Open repository Settings > Secrets and variables > Actions > Repository
   secrets. Add exactly:

   | Secret | Value |
   | --- | --- |
   | `APPLE_CERTIFICATE_P12_BASE64` | Single-line base64 of password-protected P12 |
   | `APPLE_CERTIFICATE_PASSWORD` | Its export password |
   | `APPLE_PROVISIONING_PROFILE_BASE64` | Single-line base64 of downloaded profile |
   | `APPLE_TEAM_ID` | Matching ten-character team ID |

   Encode locally into a clipboard or private temporary file; never print in a
   shared terminal or commit. For example on Windows, use the following locally
   with your own paths, then paste only in the GitHub secret input:

   ```powershell
   Set-Clipboard ([Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\private\distribution.p12')))
   # After saving that secret, repeat for the .mobileprovision file.
   Set-Clipboard ''
   ```

   This does not configure a secret until saved in GitHub. No Apple ID password,
   App Store Connect API key, or device identifier CI secret is needed.
7. Actions > Build E41 iPadOS harness > Run workflow > branch main > mode signed.
   Missing secrets fail explicitly by name only. CI checks profile team, explicit
   App ID, expiration, iOS platform, registered-device distribution, matching
   imported identity/private key, and exported signature/profile/entitlements.
   Download `E41-SIGNED-ADHOC` only after success; inspect the sanitized
   `signed-verification.json`. It does not claim installation success.

Xcode calls use manual signing without `-allowProvisioningUpdates`. Temporary
keychain/profile files are deleted in Python finally and workflow always cleanup;
hosted runners are ephemeral. No secrets or raw profiles are separate artifacts.
Only the IPA and sanitized verification are uploaded by the signed step. An ad hoc
IPA necessarily embeds its provisioning profile, including registered device
identifiers and certificate metadata. **Artifacts of this public repository are
downloadable by repository readers**; a three-day retention is not access
control. If that disclosure is unacceptable, use private artifact delivery before
running signed mode. Never publish raw signing credentials.

The signed path is implemented but cannot be end-to-end verified without valid
assets. Signature/profile validation does not prove the target iPad is in the
profile (CI deliberately accepts no UDID), certificate non-revocation at install
time, device trust, Developer Mode or installation policy. Verify intended device
selection privately in the portal and then observe installation separately.

Sources: [Apple signing identity export](https://developer.apple.com/documentation/xcode/sharing-your-teams-signing-certificates),
[Apple ad hoc profiles](https://developer.apple.com/help/account/provisioning-profiles/create-an-ad-hoc-provisioning-profile/),
[certificate roles](https://developer.apple.com/help/account/certificates/certificates-overview/),
[GitHub temporary keychain workflow](https://docs.github.com/en/actions/how-tos/deploy/deploy-to-third-party-platforms/sign-xcode-applications).
