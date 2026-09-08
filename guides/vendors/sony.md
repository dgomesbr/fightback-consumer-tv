---
title: Sony Bravia (Google TV / Android TV)
platform: google-tv
brands: [Sony Bravia]
generations: "All current Sony Bravia models. Google TV on newer sets, Android TV on older ones."
dns_field: static-ip-required
dev_mode: yes
adb: yes
package_disable: yes
root: none
max_tier: 3
updated: 2026-09-08
---

# Sony Bravia (Google TV / Android TV)

Every current Sony Bravia runs Google TV or Android TV [8], so the platform work lives in
[google-android-tv](google-android-tv.md). Read that page for the DNS path, ADB setup, the VpnService
approach and the Google endpoint set. This page covers what changes on a Sony.

Two things matter more than the rest. `tv.samba.ssm` is Samba TV, the genuine content recognition
package on a Sony set, described in the community Sony debloat work as ad tracking and viewing data
collection [1][7]. Disabling it is the highest-value single action available on this hardware.

And the widely shared Sony debloat one-liner removes `com.android.vpndialogs`, which permanently
destroys your ability to run any network monitoring app on that television [1][7]. Read the Tier 3
warning before you paste anything from the internet into a shell.

**Covers:** Sony Bravia televisions running Google TV or Android TV
**Also sold as:** nothing. Other Google TV brands are in
[google-android-tv](google-android-tv.md) and [tcl](tcl.md).
**How far you can get:** Tier 3. ADB package disabling works. Root does not exist for Sony TV hardware.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Content recognition, ad tracking and viewing data, from the `tv.samba.ssm` package | `*.samba.tv`, covering `api.cid`, `preferences.cid`, `platform.cid`, `events.cid`, `mtrcs` and `pixel.mtrcs`, plus `*.flingo.tv` | Not yet documented. See Open questions. | [2][9] |
| Device telemetry | `*.ndmdhs.com`, covering `api-mf1.meta`, `b02.black`, `bdcore-apr-lb.bda` and the `bravia-cfgdst` hosts | Not yet documented | [2][9] |
| Per-device telemetry, with a 32-character hexadecimal device identifier in the hostname | `ssm<N>.internet.sony.tv`, matched by `^([0-9a-f]{32}\.)?ssm[0-9]\.internet\.sony\.tv$` | Not yet documented | [2][9] |
| Registration, social and diagnostic telemetry | `reg.biv.sony.tv`, `social.biv.sony.tv`, `call.me.sel.sony.com`, `facemap.foldlife.net` | Not yet documented | [2][9] |
| Launcher, channel and recommendation telemetry | `androidtvchannels-pa.googleapis.com`, `androidtvlauncherxfe-pa.googleapis.com`, `androidtvwatsonfe-pa.googleapis.com` | Not yet documented | [7] |
| Ad requests, observed on real Sony hardware | `googleads.g.doubleclick.net`, `securepubads.g.doubleclick.net` | Not yet documented | [3] |

Samba TV also supplies recognition on Toshiba sets and, through `flingo.tv`, on some Philips sets [2][9],
so one blocklist entry covers three brands.

The `ssm<N>.internet.sony.tv` hosts carry a 32-character hexadecimal prefix per device [2]. A hostname
that identifies the individual television is the pattern this project's collector redacts to `{id}`
before anything is published. See [PRIVACY.md](../../PRIVACY.md).

The one piece of direct evidence from a Sony television rather than from a package list is a bug report
filed against Blokada, which carries a log from a Sony Android TV blocking `googleads.g.doubleclick.net`
and `securepubads.g.doubleclick.net` [3]. It confirms the traffic on this hardware, and it shows that a
VpnService-based tool runs on an Android television.

Google's platform telemetry is a research gap. It is co-mingled with load-bearing `*.googleapis.com`
hosts, the community has isolated only the three `-pa` hostnames above, and HaGeZi publishes no list for
Google or Android TV [10][7]. Do not wildcard `googleapis.com`.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

**What this breaks:** nothing we have documented. Recommendations on the home row get less personal.

### Turn off content recognition

Sony's settings-level equivalent of disabling `tv.samba.ssm` is the Samba TV consent, usually presented
during setup and commonly labelled Samba Interactive TV. We have no verified menu path for it on any
Sony firmware. Not yet documented. See Open questions.

| Generation | Path | Status |
| --- | --- | --- |
| Google TV, Android TV | Not yet documented | Open question |

If you cannot find the toggle, Tier 3 removes the package outright, which is a stronger result anyway.

### Turn off ad tracking and personalisation

| Generation | Path | Status |
| --- | --- | --- |
| Android TV, Sony-specific wording | Device Preferences > About > Ads > Reset advertising ID | ⚠️ needs-confirmation |
| Google TV | Settings > Privacy > Ads, and Settings > Privacy > Usage & diagnostics | ⚠️ needs-confirmation |

Google's own documentation page for these settings could not be located during research, which is why
both rows are unconfirmed [7]. The rest of the platform settings are in
[google-android-tv](google-android-tv.md).

### Other settings worth changing

Not yet documented for Sony specifically. See Open questions for the microphone and voice paths we lack.

**What this does not fix:** the Samba TV package keeps running whether or not you found its consent
toggle, unless you disable it in Tier 3. Opting out has been measured as genuinely effective on Samsung
and LG [4], never on a Sony.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

### On the device

Android TV has DNS fields, bundled with a full static IP.

| Path | Status |
| --- | --- |
| Settings > Network & Internet > *your network* > IP settings > Static, then the sequential screens labelled `DNS 1:` and `DNS 2:` | ✅ verified in AOSP source [5], not confirmed on Sony firmware |

The screens carry the placeholder text "Enter a valid IP address or leave empty. Example: 8.8.8.8",
which is how you know you are in the right flow [5]. Sony ships its own settings skin over AOSP, so the
wording may differ on your set and that is worth a bug report.

Stock Android TV has no Private DNS preference in its settings XML, even though the framework has
supported it since Android 9 [5][7]. The ADB workaround is in
[google-android-tv](google-android-tv.md). Whether Sony exposes it is **UNVERIFIED**.

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: hand your resolver
out with DHCP option 6, redirect outbound TCP and UDP port 53, reject port 853, and mirror all of it on
IPv6 [7]. 68% of the smart TVs in a 200-plus-home study reached Google Public DNS directly instead of
the resolver they were handed [6], and Chromecast before Google TV hardcodes 8.8.8.8 and 8.8.4.4 in the
same code lineage [7], so do not trust the field on the TV.

### What to block

The endpoint sets live in [`data/endpoints/sony.yml`](../../data/endpoints/sony.yml) and
[`data/endpoints/google.yml`](../../data/endpoints/google.yml), with a breakage flag per entry, rather
than being duplicated here. If you block one thing on a Sony, block `*.samba.tv`.

Generated lists: [`blocklists/fightback-tv-sony.txt`](../../blocklists/)

### What never to block

Four entries are Sony's own. The platform set, which includes `*.googleapis.com`, `play.google.com`,
`*.gvt1.com`, the connectivity-check hosts and `time.google.com`, is in
[google-android-tv](google-android-tv.md). Do not wildcard `googleapis.com`.

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `applicast.ga.sony.net` | Applications stop working and the TV reports no internet connection | [2][9] |
| `portal.store.sonyentertainmentnetwork.com` | Applications stop working and the TV reports no internet connection | [2][9] |
| `update.biv.sony.tv` | Firmware updates fail | [2][9] |
| `service.biv.sony.tv` | Consequence unknown, held on the never-block list as a precaution | [2][9] |

Note that `update.biv.sony.tv` and `service.biv.sony.tv` sit under the same `biv.sony.tv` domain as the
telemetry hosts `reg.biv.sony.tv` and `social.biv.sony.tv`. Do not wildcard `biv.sony.tv`, or you trade
your ad blocking for firmware updates.

### Hardcoded addresses

None documented for Sony. LG sets are known to dial bare IP addresses that DNS filtering cannot touch
[7], so the same WAN-side capture is worth running here. Findings belong in `data/hardcoded/sony.yml`.

## Tier 2: developer mode and sideloading

Covered in [google-android-tv](google-android-tv.md). There is nothing Sony-specific to add, and
duplicating it here would give us two copies to keep correct.

## Tier 3: disable preinstalled advertising and metrics apps

**Time:** 1 hour. **Risk:** medium. A wrong package can stop the TV booting.
**Reversible:** yes, by re-enabling or factory reset.

**Read this before anything else in this section.**

> ☠️ **Never run `pm uninstall --user 0 com.android.vpndialogs`.** That package is the system VPN
> consent dialog. Remove it and `VpnService.prepare()` can never be granted again on that television, so
> no network monitoring or DNS filtering app will ever work on it [1][7]. The most widely shared Sony
> debloat one-liner contains exactly that command [1]. If you have already run it, a factory reset is
> the only documented recovery.
>
> ☠️ A VPN service caused boot loops on some older Sony firmware [7]. If you are planning to run a
> VpnService-based tool, know that before you start rather than after.

Prefer `pm disable-user` over `uninstall`. It is reversible with one command and it survives less
awkwardly.

```
adb connect <ip>:5555
adb shell pm disable-user --user 0 tv.samba.ssm
```

### Safe to disable

Package safety is per model. These come from
[`data/packages/android-tv.yml`](../../data/packages/android-tv.yml), which records the models each entry
was tested on and refuses to emit a command for an untested one [9]:

| Package | What it is | Removing it breaks |
| --- | --- | --- |
| `tv.samba.ssm` | Samba TV. Content recognition, ad tracking and viewing data collection. Start here [1] | Nothing recorded |
| `com.sony.dtv.sonybugreportsys` | Bug report upload | Nothing recorded |
| `com.sony.dtv.system.crashlog` | Crash log upload | Nothing recorded |
| `com.sony.dtv.customersupport` | Customer support telemetry | Nothing recorded |
| `com.sony.dtv.da.service` | Sony diagnostics service | Nothing recorded |
| `com.sony.dtv.promos` | Promotional content | Nothing recorded |
| `com.sony.dtv.sonyselect` | Sony Select recommendations | The Sony Select recommendation rows disappear |
| `com.sony.dtv.demomode` | In-store demo mode | Nothing recorded |
| `com.google.android.tv.bugreportsender` | Android TV bug report sender | Nothing recorded |
| `com.google.android.feedback` | Google feedback | Nothing recorded |
| `com.google.android.partnersetup` | Google partner setup | Nothing recorded |

The last three are generic Android TV rather than Sony, and the same entries apply on TCL, Hisense and
Philips Android TV sets [9].

Leave `com.google.android.tungsten.setupwraith` alone. It is widely recommended as a telemetry removal
and it is the Android TV Setup Wizard and fallback launcher [7]. See
[google-android-tv](google-android-tv.md).

### Do not disable

| Package | What breaks | Source |
| --- | --- | --- |
| `com.android.vpndialogs` | ☠️ VPN consent can never be granted again. No monitoring or filtering app will work | [1][9] |
| `com.sony.dtv.tvx` | ☠️ The boot process fails. The TV does not start | [1][9] |
| `com.google.android.webview` | ☠️ The entire interface breaks | [1][9] |
| `com.google.android.katniss` | ☠️ Google search and assistant for TV. Essential to the launcher | [1][9] |
| `com.google.android.tvrecommendations` | ☠️ Documented boot loop on Sony | [1][9] |
| `com.google.android.tts` | ☠️ Documented boot loop on Sony Google TV | [1][9] |
| `com.android.location.fused` | ☠️ Documented boot loop on Sony Google TV | [1][9] |
| `com.android.captiveportallogin` | The TV cannot join networks that use a captive portal. Removed by the same one-liner | [1][9] |

`com.google.android.tvrecommendations` is the primary safe-debloat target in a TCL toolkit and a
documented boot loop in the Sony guide [7]. Both are probably correct for their own hardware, which is
why this project gates package data per model and why you should not run a list written for another
brand. See [tcl](tcl.md) for the other side of that contradiction.

### Undoing it

```
adb shell pm enable tv.samba.ssm
```

If the TV will not boot, a factory reset restores every package. Recovering a set that boot-loops before
the network comes up needs the physical recovery procedure for your model, which we do not document.

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

Sony television hardware has a locked bootloader, and no root or custom firmware project exists for it
[7], so there is nothing to link. The one device in this category with a supported unlock is the Nvidia
Shield, which LineageOS supports as `foster` and for which NVIDIA publishes stock recovery images [7].
That is a streaming box, not a Sony television.

**What root gets you:** on a Sony TV, nothing available today.
**What it costs you:** not applicable, there is no path.
**Where to go:** nowhere. See [LEGAL.md](../../LEGAL.md) for our policy if that changes.

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Personalised recommendations get less personal | Turn the toggles back on |
| 1 | Store, updates or clock, if you block anything in the never-block table | Remove the entry and reboot the TV |
| 2 | See [google-android-tv](google-android-tv.md) | |
| 3 | Sony Select rows and support diagnostics. Boot failure if you disable a package in the do-not-disable table | `adb shell pm enable <package>`, or factory reset |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is watching your
resolver's query log for `samba.tv` and `flingo.tv`. Those are the Samba TV endpoints [2], so a query
count that drops to zero after you disable `tv.samba.ssm` is direct proof, and a count that stays up
means the package is still running or something else on the TV is doing the asking.

`googleads.g.doubleclick.net` gives you a second signal, and it has been observed on real Sony
hardware [3].

Start the capture before the TV boots. Most DNS requests fire in the first seconds after activation [7].

## Open questions

Answer any of these with a Sony in front of you and it is a direct contribution. Use the
[device report form](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=device_report.yml).

- **How often does `tv.samba.ssm` contact `samba.tv`?** We have the hostnames from Perflyst [2] and no
  cadence at all. Samsung and LG cadences were measured to the millisecond [4]. Nobody has done that for
  Samba TV on a Sony, and it is the highest-value measurement available on this hardware.
- Where is the Samba TV consent toggle in Sony's menus, what is it called, and on which firmware?
- Does that toggle stop traffic to `samba.tv`, or only change what Samba does with the data? Opt-out was
  measured as effective on Samsung and LG [4], never here.
- Does content recognition keep running when a Sony is used as a plain HDMI display? Confirmed on Samsung
  and LG [4].
- Does Sony's settings skin expose a Private DNS preference, and does the AOSP static-IP wording match
  it? Both **UNVERIFIED** [5][7].
- Which older Sony firmware versions boot-loop with a VpnService app active, and which are fine? [7]
- Is `com.google.android.tvrecommendations` a boot loop on every Sony model, or only some? [7]

## Sources

1. [sony-google-tv-debloat](https://github.com/ironshadow786786-boop/sony-google-tv-debloat). The
   `tv.samba.ssm` identification, the diagnostics package list, the boot-loop warnings, and the
   `com.android.vpndialogs` trap.
2. Perflyst, [PiHoleBlocklist SmartTV.txt](https://github.com/Perflyst/PiHoleBlocklist/blob/master/SmartTV.txt).
   MIT, stale since 13 July 2023. Source of the Samba TV, `ndmdhs.com`, `internet.sony.tv` and
   `biv.sony.tv` hostnames and of every never-block consequence in the table above.
3. [Blokada issue 134](https://github.com/blokadaorg/blokada/issues/134). Log from a Sony Android TV
   blocking `googleads.g.doubleclick.net` and `securepubads.g.doubleclick.net`.
4. Anselmi et al., IMC 2024, [Watching TV with the Second-Party](https://arxiv.org/html/2409.06203v1).
5. [AOSP TvSettings](https://android.googlesource.com/platform/packages/apps/TvSettings/+/refs/heads/main/Settings/).
   `AdvancedWifiOptionsFlow.java` and `strings.xml` for the DNS flow, `network.xml` for the absent
   Private DNS preference.
6. Mazhar and Shafiq, IoTDI 2020, [Characterizing Smart Home IoT Traffic in the
   Wild](https://arxiv.org/abs/2001.08288) §IV-C.
7. [Project research notes](../../RESEARCH-NOTES.md), Google Android TV section and cross-cutting facts.
8. [Project research notes](../../RESEARCH-NOTES.md), "Which OS is it" table.
9. Project endpoint and package data, [`data/endpoints/sony.yml`](../../data/endpoints/sony.yml) and
   [`data/packages/android-tv.yml`](../../data/packages/android-tv.yml), where every entry carries its own
   upstream source and per-model scope.
10. HaGeZi, [dns-blocklists](https://github.com/hagezi/dns-blocklists). GPL-3.0. No Google or Android TV
    list.
