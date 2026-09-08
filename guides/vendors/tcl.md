---
title: TCL (Google TV, Roku TV, or other)
platform: other
# TCL badges three different operating systems. See the decision table in the body.
brands: [TCL]
generations: "Current and recent TCL televisions in all markets"
dns_field: varies
dev_mode: varies
adb: varies
package_disable: varies
root: none
max_tier: 3
updated: 2026-09-08
---

# TCL (Google TV, Roku TV, or other)

TCL puts its badge on three different operating systems depending on the model and the market you bought
it in [6]. Work out which one you have before you read anything else, because the answers diverge
completely. A TCL running Roku OS has no DNS field and no static IP form anywhere in its menus, so the
router is your only option. A TCL running Google TV has a DNS field, ADB access and package disabling.

**Covers:** TCL televisions on Google TV, Android TV and Roku OS
**Also sold as:** TCL sells the same panel on different software in different regions, so two sets with
similar model numbers can need different guides
**How far you can get:** Tier 3 on Google TV and Android TV models. Tier 1 on Roku TV models.

## Which TCL do you have

Check Settings > About, or watch the splash screen while the TV boots. Both methods are
⚠️ needs-confirmation because neither comes from TCL documentation.

| What you see | Platform | Read this |
| --- | --- | --- |
| "Google TV" or "Android TV" in Settings > About, or a Google TV home screen with a Google account | Google TV or Android TV | [google-android-tv](google-android-tv.md), then Tier 3 below for the TCL packages |
| A Roku home screen with a channel grid, and Roku branding in the interface and on the remote | Roku OS | [roku](roku.md). No DNS field exists, so go straight to the router |
| Neither, and you bought the set in the EU | Not yet documented. See Open questions. | Open a [guide request](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=guide_request.yml) |

Our notes record only that "some EU variants" exist on other stacks [6], with no detail on what they
run. If you have one, telling us what Settings > About says is a genuinely useful contribution.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Screen advertising, from the `com.tcl.screenadservice` package | Not yet documented. No TCL hostname has been attributed. See Open questions. | Not yet documented | [1][8] |
| Content recognition, ad tracking and viewing data, from `tv.samba.ssm`, which the package data scopes to both TCL and Sony | `*.samba.tv` and `*.flingo.tv` | Not yet documented | [7][8] |
| On Roku TV models, content recognition from TV inputs | `acr.roku.com` is the single most on-target hostname on Roku | Not yet documented | [5] |
| On Google TV models, launcher and recommendation telemetry | `androidtvchannels-pa.googleapis.com`, `androidtvlauncherxfe-pa.googleapis.com`, `androidtvwatsonfe-pa.googleapis.com` | Not yet documented | [5] |

Samba TV is the one recognition endpoint we can name on a TCL, and it is shared with Sony and Toshiba
[7][8]. For TCL's own packages we hold no hostnames, so we can name `com.tcl.screenadservice` and not the
traffic it generates. That gap is the first entry under Open questions.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

**What this breaks:** nothing we have documented. Recommendations get less personal.

### Turn off content recognition

| Platform | Path | Status |
| --- | --- | --- |
| Roku TV | Settings > Privacy > Smart TV Experience, uncheck Use info from TV inputs | ⚠️ needs-confirmation |
| Google TV, Android TV | Not yet documented for the `tv.samba.ssm` consent. See [sony](sony.md), which has the same package and the same gap | Open question |

The Roku setting only exists on Roku TVs, which is exactly what a Roku TCL is, so it applies here [5].
Roku's privacy policy page is rendered client-side and the support sitemap contains no privacy article,
which is why the path is unconfirmed [5].

### Turn off ad tracking and personalisation

| Platform | Path | Status |
| --- | --- | --- |
| Roku TV | Settings > Privacy > Advertising, then Limit ad tracking, or Personalize ads on newer builds, plus Reset advertising identifier | ⚠️ needs-confirmation |
| Google TV | Settings > Privacy > Ads | ⚠️ needs-confirmation |
| Android TV | Settings > Device Preferences, then Usage & diagnostics | ⚠️ needs-confirmation |

### Other settings worth changing

On Roku TV models, Settings > Privacy > Microphone > Channel microphone access
(⚠️ needs-confirmation), and turn off "Control by mobile apps" if you do not use a phone remote. That
same interface lets anything on your LAN read the TV's model, serial number and device ID over port 8060
[5]. Details in [roku](roku.md).

Nothing TCL-specific is documented for Google TV models. See
[google-android-tv](google-android-tv.md).

**What this does not fix:** the `com.tcl.screenadservice` package keeps running regardless. Opting out
has been measured as genuinely effective on Samsung and LG sets [2], never on a TCL.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

### On the device

| Platform | Path | Status |
| --- | --- | --- |
| Google TV, Android TV | Settings > Network & Internet > *your network* > IP settings > Static, then `DNS 1:` and `DNS 2:` | ✅ verified in AOSP source [3], not confirmed on TCL firmware |
| Roku TV | **There is no DNS setting on this platform.** No DNS field, no static IP form, in any version of Roku OS including Roku TVs | [5] |

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: on a Roku TCL the
router is the only enforcement point that exists, so hand your resolver out with DHCP option 6, redirect
outbound TCP and UDP port 53 to it, reject port 853, and mirror all of it on IPv6 [5]. Roku is reported
to fall back to 8.8.8.8 since Roku OS 5.4, which is **UNVERIFIED** and comes from a forum post we could
not fetch directly [5], but the redirect makes the question moot.

### What to block

The endpoint sets live in [`data/endpoints/roku.yml`](../../data/endpoints/roku.yml),
[`data/endpoints/google.yml`](../../data/endpoints/google.yml) and, for Samba TV,
[`data/endpoints/sony.yml`](../../data/endpoints/sony.yml). There is no TCL file, because we have no TCL
hostnames.

Generated lists: [`blocklists/fightback-tv-google.txt`](../../blocklists/) on Google TV models,
[`blocklists/fightback-tv-roku.txt`](../../blocklists/) on Roku models.

### What never to block

The full sets are on the platform pages. Two entries decide whether a Roku TCL keeps working:

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `api.sr.roku.com` | Everything. PETS 2021 classified it and `youtube.com` as the only required destinations on Roku | [4] |
| `roku.com` as a wildcard | Do not wildcard it. `cloudservices.roku.com` appears in some lists with no breakage note, which is how people lock themselves out | [4][5] |

On Google TV models, leave `*.googleapis.com`, `play.google.com`, `*.gvt1.com`, the connectivity-check
hosts and `time.google.com` alone [5]. Full table in [google-android-tv](google-android-tv.md).

### Hardcoded addresses

None documented for TCL on either platform. LG sets are known to dial bare IP addresses that DNS
filtering cannot reach [5], so the same WAN-side capture is worth running here.

## Tier 2: developer mode and sideloading

Covered on the platform pages. Google TV and Android TV models use ADB, described in
[google-android-tv](google-android-tv.md). Roku models have a developer mode that installs exactly one
sideloaded app at a time and gives you no packet, DNS or cross-app visibility, described in
[roku](roku.md). Nothing about either is TCL-specific.

## Tier 3: disable preinstalled advertising and metrics apps

**Time:** 1 hour. **Risk:** medium. A wrong package can stop the TV booting.
**Reversible:** yes, by re-enabling or factory reset.

Google TV and Android TV models only. On a Roku TCL this tier does not exist, because Roku exposes no
ADB and no package manager [5].

> ☠️ **Never run `pm uninstall --user 0 com.android.vpndialogs`.** It is the system VPN consent dialog.
> Remove it and `VpnService.prepare()` can never be granted again on that television, so no network
> monitoring or filtering app will ever work on it [5]. ADB debloat scripts that circulate for Android
> televisions contain that command, so read any script before you paste it.

### Safe to disable

Scoped to TCL Google TV models, from
[`data/packages/android-tv.yml`](../../data/packages/android-tv.yml) [1][8]:

| Package | What it is |
| --- | --- |
| `com.tcl.screenadservice` | The TCL ad service. Start here |
| `tv.samba.ssm` | Samba TV. Content recognition, ad tracking and viewing data collection |
| `com.tcl.browser` | TCL's browser |
| `com.tcl.tv.appstore` | TCL's own app store, separate from Play |
| `com.tcl.usercenter` | TCL account services |
| `com.tcl.screensaver` | TCL screensaver, a delivery surface for promotional content |
| `com.google.android.tv.bugreportsender` | Generic Android TV bug report sender |
| `com.google.android.feedback` | Generic Google feedback |
| `com.google.android.partnersetup` | Generic Google partner setup |

### Do not disable

| Package | What breaks | Source |
| --- | --- | --- |
| `com.android.vpndialogs` | ☠️ VPN consent can never be granted again | [8] |
| `com.google.android.webview` | ☠️ The entire interface breaks on Sony. Untested on TCL | [8] |
| `com.google.android.katniss` | ☠️ Essential to the launcher on Sony. Untested on TCL | [8] |
| `com.android.captiveportallogin` | The TV cannot join networks that use a captive portal | [8] |
| `com.google.android.tvrecommendations` | Contradictory. Read the paragraph below before you touch it | [1][8] |

`com.google.android.tvrecommendations` is the primary safe-debloat target in the
[TCL-Google-TV-Debloat-Optimizer](https://github.com/livvaa/TCL-Google-TV-Debloat-Optimizer) [1], and it
is listed under "will cause a boot loop if removed" in the community Sony guide [5]. Both are probably
correct for their own hardware, and that one package is why this project keeps package data in per-model
files instead of publishing a single Android TV list. A list written for a TCL can brick a Sony and the
reverse is just as plausible. Run the list written for your model, and if there isn't one, disable
packages one at a time with a reboot in between. Our own package data marks this entry `safe: unknown`
with an empty `tested_on` list, and the generator refuses to emit a command for it until somebody reports
a specific model and firmware [8]. The same caution applies to the two Google packages above, whose
boot-loop status is documented on Sony hardware and untested on TCL.

### Undoing it

```
adb shell pm enable com.tcl.screenadservice
```

If the TV will not boot, a factory reset restores every package.

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

No path exists on either platform. TCL Google TV sets have locked bootloaders and no OEM unlock, and no
root project exists for them [5]. Roku has no root and no community attempt was found at all, which
makes it the most locked-down platform in our research [5].

**What root gets you:** nothing available today on TCL hardware.
**What it costs you:** not applicable, there is no path.
**Where to go:** nowhere. See [LEGAL.md](../../LEGAL.md).

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Personalised recommendations and ads get less relevant | Turn the toggles back on |
| 1 | The Roku channel store or the Play store, if you block anything in the never-block table | Remove the entry and reboot the TV |
| 2 | See the platform page | |
| 3 | TCL's own app store and account features. Boot failure if you disable the wrong package | `adb shell pm enable <package>`, or factory reset |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most depends on which
TCL you have. On a Roku TCL, watch your resolver's query log for `acr.roku.com`, which is the single most
on-target hostname on Roku and gives you a clean before-and-after signal [5]. On a Google TV TCL, watch
for `samba.tv` and `flingo.tv` [7], which should fall to zero once `tv.samba.ssm` is disabled. We have no
hostname for `com.tcl.screenadservice`, so for that one confirm the disable command returned without
error and fall back to the checks in [google-android-tv](google-android-tv.md).

Start the capture before the TV boots. Most DNS requests fire in the first seconds after activation [5].

## Open questions

Answer any of these with a TCL in front of you and it is a direct contribution. Use the
[device report form](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=device_report.yml).

- **Which hostnames does `com.tcl.screenadservice` contact?** We have zero TCL-specific domains. One
  packet capture closes the biggest gap on this page.
- Which hostnames does `tv.samba.ssm` contact on a TCL? Same gap as on [sony](sony.md).
- What do the EU TCL variants actually run? Our notes say only "some EU variants" [6].
- Is `com.google.android.tvrecommendations` genuinely safe to disable on TCL hardware, and on which model
  numbers? The contradiction with Sony is documented and unresolved [1][5].
- Do `com.google.android.webview` and `com.google.android.katniss` boot-loop a TCL the way they do a Sony?
- Do TCL sets dial hardcoded IP addresses that DNS filtering cannot see?

## Sources

1. [TCL-Google-TV-Debloat-Optimizer](https://github.com/livvaa/TCL-Google-TV-Debloat-Optimizer). Source
   of the TCL package list and of the `com.google.android.tvrecommendations` recommendation that
   contradicts the Sony guide.
2. Anselmi et al., IMC 2024, [Watching TV with the Second-Party: A First Look at Automatic Content
   Recognition Tracking in Smart TVs](https://arxiv.org/html/2409.06203v1).
3. [AOSP TvSettings](https://android.googlesource.com/platform/packages/apps/TvSettings/+/refs/heads/main/Settings/).
4. Mandalari et al., PETS 2021, [Blocking Without Breaking: Identification and Mitigation of
   Non-Essential IoT Traffic](https://arxiv.org/abs/2105.05162). Required versus non-required
   destinations for Roku.
5. [Project research notes](../../RESEARCH-NOTES.md), Roku, Google Android TV and cross-cutting sections,
   gathered 8 September 2026.
6. [Project research notes](../../RESEARCH-NOTES.md), "Which OS is it" table.
7. Perflyst, [PiHoleBlocklist SmartTV.txt](https://github.com/Perflyst/PiHoleBlocklist/blob/master/SmartTV.txt).
   MIT, stale since 13 July 2023. Source of the Samba TV hostnames.
8. Project endpoint and package data, [`data/endpoints/`](../../data/endpoints/) and
   [`data/packages/android-tv.yml`](../../data/packages/android-tv.yml), where every entry carries its own
   upstream source and per-model scope.
