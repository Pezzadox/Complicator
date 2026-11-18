# Release runbook: The Complicator

## Release

    git tag v1.0.0 && git push origin v1.0.0

That builds the Android bundle and the iOS build and uploads them to Play internal
testing and TestFlight. Both arrive as drafts; nothing reaches anyone until it is
promoted in the console. The workflow can also be started by hand from the Actions tab
(Release → Run workflow).

App id on both stores: `com.thecomplicator.app`

## Secrets (GitHub → Settings → Secrets and variables → Actions)

Android:

| Secret | Value |
| --- | --- |
| `ANDROID_KEYSTORE_BASE64` | the upload keystore, base64 |
| `ANDROID_KEYSTORE_PASSWORD` | its password |
| `ANDROID_KEY_ALIAS` | `complicator` |
| `ANDROID_KEY_PASSWORD` | the key password |
| `PLAY_SERVICE_ACCOUNT_JSON` | the Play service-account JSON, whole (the same one as World Mapper works) |
| `ADMOB_APP_ID` | optional: the AdMob app id; with `ADMOB_BANNER_ID` it switches the banner advert on |
| `ADMOB_BANNER_ID` | optional: the AdMob banner ad unit id |

Apple (all the same values as World Mapper, apart from nothing):

| Secret | Value |
| --- | --- |
| `APP_STORE_CONNECT_API_KEY` | the .p8 key, base64 |
| `APP_STORE_CONNECT_KEY_ID` | key id |
| `APP_STORE_CONNECT_ISSUER_ID` | issuer id |
| `IOS_TEAM_ID` | team id |
| `MATCH_GIT_URL` | the certificates repo; `world-mapper-certs` can hold this app's profile too |
| `MATCH_GIT_TOKEN` | a fine-grained PAT for that repo |
| `MATCH_PASSWORD` | the passphrase encrypting the stored certificate |

Either half is skipped, with a warning, when its secrets are absent.

## First Android release only

Google refuses API uploads until one build has gone in through the console. Download
the `.aab` from the workflow run's artifacts and upload it by hand once, under
Testing → Internal testing.

## Store pages

Listings, screenshots and the privacy policy are in `store/`. The privacy policy needs a
public web address for both stores: GitHub Pages or the website both work.

Store questionnaires, Apple: no data collected, no ads, no tracking, no account, 4+.
Category: Education. The iPhone app has no adverts and does not include the advert plugin
(`ios.includePlugins` in `capacitor.config.json`).

Store questionnaires, Google Play, now that the Android app carries a banner advert:

- **Ads:** "Yes, my app contains ads."
- **Data safety:** data is collected and shared by the advertising SDK: Device or other IDs
  (advertising ID), Approximate location (from IP address), App interactions (advert views and
  taps), Diagnostics. Purpose: Advertising or marketing; Analytics; Fraud prevention. Not
  optional. Data is encrypted in transit. Check this against Google's current AdMob data
  disclosure page before submitting.
- **Advertising ID:** "Yes", for Advertising or marketing.
- **Target audience:** 13 and over. Choosing a younger age group brings in the Families
  policy, which needs different advert settings.
- **Content rating:** still "Everyone"; answer "yes" to the question about adverts.
- The public privacy policy page must be replaced with the new `store/privacy-policy.md`.

## The banner advert (Android)

One adaptive banner under the keypad, hidden in Focus view. It only exists in a build that
was given an ad unit id; without the two secrets below the app has no adverts at all.

1. Create an AdMob account at admob.google.com and add the app (Android, package
   `com.thecomplicator.app`). That gives the **app id** (`ca-app-pub-…~…`).
2. Create one **Banner** ad unit. That gives the **ad unit id** (`ca-app-pub-…/…`).
3. In AdMob → Privacy & messaging, create and publish a **European regulations** message for
   the app, so the consent screen has something to show.
4. Add two GitHub secrets: `ADMOB_APP_ID` (the app id) and `ADMOB_BANNER_ID` (the ad unit id).
5. Once the app is live on Play, link it in AdMob and add the `app-ads.txt` line AdMob gives
   you to the root of the developer website named on the store page.

Never tap your own live adverts. To try the banner on your own phone first, build with
Google's test ad unit: `ADMOB_BANNER_ID=ca-app-pub-3940256099942544/9214589741 npm run sync`.
