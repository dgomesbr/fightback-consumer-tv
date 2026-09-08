---
title: Google TV and Android TV
platform: google-tv
brands: [Sony, TCL, Hisense, Philips, Sharp, Toshiba, Nvidia, Google, onn]
generations: "Not yet documented. See Open questions."
dns_field: static-ip-required # pre-Google-TV Chromecast has no DNS field at all
dev_mode: yes
adb: yes
package_disable: yes
root: available # Nvidia Shield only. None for Chromecast with Google TV, Google TV Streamer or OEM TVs.
max_tier: 4
updated: 2026-09-08
---

# Google TV and Android TV

This page covers more hardware than any other guide in the project. Sony, TCL, Hisense, Philips,
Sharp, Toshiba, Nvidia Shield, Chromecast with Google TV, the Google TV Streamer and onn boxes all run
the same Google base with a different OEM layer on top. Tier 0 and Tier 1 are close to
identical across all of them. Tier 3 is not, which is why the per-OEM sections matter.
`com.google.android.tvrecommendations` is the first recommended removal in a TCL toolkit and is listed
as a boot loop in a Sony guide. Find your brand's section and stay in it.

**Covers:** Sony Bravia (Google TV or Android TV on all current models), TCL Google TV, Hisense Google
TV SKUs, Philips Android TV sets, Sharp Android or Google TV, Toshiba Google TV on newer sets, Nvidia
Shield, Chromecast with Google TV, Google TV Streamer, onn.
**Also sold as:** several of these brands ship other platforms too. Sharp and Hisense also sell Roku TV,
Toshiba also sells Fire TV Edition and VIDAA, and many current EU Philips sets run Titan OS. Confirm the
platform before following this page.
**How far you can get:** Tier 4 on an Nvidia Shield, Tier 3 wherever you can reach ADB, Tier 1 only on a
pre-Google-TV Chromecast, which has no DNS field and hardcodes Google's resolvers.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Launcher and channel-row metadata | `androidtvchannels-pa.googleapis.com`, `androidtvlauncherxfe-pa.googleapis.com`, `androidtvwatsonfe-pa.googleapis.com` | Not yet documented | Community endpoint lists. No primary capture. |
| Ad requests from the home screen and apps | `googleads.g.doubleclick.net`, `partnerad.l.doubleclick.net`, `2mdn.net` | Not yet documented | A Blokada log from a Sony Android TV shows it blocking `googleads.g.doubleclick.net` and `securepubads.g.doubleclick.net` on-device [6] |
| Content recognition and viewing data, Sony sets | Samba TV, shipped as the package `tv.samba.ssm` | Not yet documented | Sony debloat guide, which describes it as ad tracking and viewing data collection [4] |
| Screen advertising, TCL sets | `com.tcl.screenadservice` | Not yet documented | TCL debloat toolkit [5] |
| Bug reports, crash logs and support telemetry, Sony sets | `com.sony.dtv.sonybugreportsys`, `com.sony.dtv.system.crashlog`, `com.sony.dtv.da.service` | Not yet documented | Sony debloat guide [4] |
| DNS queries, pre-Google-TV Chromecast | 8.8.8.8 and 8.8.4.4, hardcoded | Every lookup | Project research notes. A 200-home measurement found 68% of smart TVs reach Google Public DNS directly [2] |

Nobody has published a packet capture of a Google TV or Android TV device in the peer-reviewed
literature we cite. The 2024 IMC study covered Samsung and LG [11] and the 2021 PETS per-device study
covered Fire TV and Roku, so what backs the table above is community lists plus one bug report. The 2020
PETS study of blocklists found they protect better against third-party tracking than against
first-party platform telemetry [10], and this platform is the clearest example of that in the project.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

**What breaks:** home screen recommendations get less personal and ads get less relevant. Nothing stops
working. The 2024 IMC study found opting out on Samsung and LG stopped all traffic to the content
recognition domains the researchers had identified [11], so do the menus before anything harder.

The menus moved when Google renamed the platform. Android TV keeps privacy items under **Device
Preferences**, Google TV has a top-level **Privacy** menu. Look for that Privacy entry in Settings to
work out which one you have.

### Turn off content recognition

| Generation | Path | Status |
| --- | --- | --- |
| Sony, Samba TV consent | Not yet documented. See [Open questions](#open-questions). | ⚠️ needs-confirmation |
| Stock Google TV and Android TV | No content recognition toggle is documented in our notes | Not yet documented |

On a Sony set, Samba TV is the highest-value item on this page. It ships as `tv.samba.ssm` and the Sony
debloat guide describes it as ad tracking and viewing data collection [4]. If your set shows a Samba TV
or Samba Interactive TV consent screen, decline it. We have no confirmed menu path to switch it off
afterwards, so the route we can document is removing the package in
[Tier 3](#tier-3-disable-preinstalled-advertising-and-metrics-apps). It also appears in TCL Google TV
package lists [5], so TCL owners should check whether it is installed.

### Turn off ad tracking and personalisation

| Generation | Path | Status |
| --- | --- | --- |
| Google TV (Chromecast with Google TV, Google TV Streamer, TCL, Hisense, current Sony) | Settings > Privacy > Ads | ⚠️ needs-confirmation |
| Android TV, Sony | Settings > Device Preferences > About > Ads > Reset advertising ID | ⚠️ needs-confirmation |

### Turn off usage and diagnostics

| Generation | Path | Status |
| --- | --- | --- |
| Android TV | Settings > Device Preferences, then Usage & diagnostics | ⚠️ needs-confirmation |
| Google TV | Settings > Privacy, then Usage & diagnostics | ⚠️ needs-confirmation |

Every Tier 0 path here is marked needs-confirmation because we could not locate Google's own
documentation for any of them. Correcting one against real hardware is the most useful contribution you
can make to this page.

### Other settings worth changing

Microphone, voice and local network settings are not yet documented. See
[Open questions](#open-questions).

**What this does not fix:** no toggle stops the launcher talking to the three `-pa.googleapis.com`
endpoints or stops apps requesting ads from `googleads.g.doubleclick.net`, and on a Sony set
`tv.samba.ssm` keeps running until you disable it. A 2020 measurement of 200-plus homes found 68% of
smart TVs bypassed the DNS server their router handed them and queried Google Public DNS directly [2],
which is why Tier 1 belongs at the router. A pre-Google-TV Chromecast hardcodes 8.8.8.8 and 8.8.4.4 and
has no DNS field, so for those owners Tier 1 is router-only.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

**What breaks:** nothing, as long as you keep [the never-block set](#what-never-to-block). Over-block
`*.googleapis.com` and you take out the Play Store, updates and the launcher at once. This platform
punishes wildcards harder than any other here.

### On the device

| Generation | Path | Status |
| --- | --- | --- |
| Android TV and Google TV | Settings > Network & Internet > *your network* > IP settings > Static, then the sequential screens labelled `DNS 1:` and `DNS 2:` | ✅ verified (AOSP source) |
| Pre-Google-TV Chromecast | No DNS field exists, and the device hardcodes 8.8.8.8 and 8.8.4.4 | n/a |

That path is confirmed in the AOSP TvSettings source, in `AdvancedWifiOptionsFlow.java` and
`res/values/strings.xml` [1]. The DNS fields carry the placeholder text "Enter a valid IP address or
leave empty. Example: 8.8.8.8".

**Static IP is required.** There is no way to set DNS on its own here. Choosing Static replaces the
whole DHCP lease, so you have to supply a fixed address for the TV as well. Read
[Router enforcement](../router-enforcement.md) first, because picking that address badly is how people
end up with two devices on one IP.

### Private DNS (DNS-over-TLS)

Stock TvSettings has no Private DNS screen. We checked the source rather than the menus, and
`res/xml/network.xml` in AOSP TvSettings contains no private DNS preference [1]. The Android framework
has supported DNS-over-TLS since Android 9, so the capability is there with no UI attached to it.

The workaround is two ADB commands, which need [Tier 2](#tier-2-developer-mode-and-sideloading):

```
adb shell settings put global private_dns_mode hostname
adb shell settings put global private_dns_specifier dns.example
```

Whether individual OEMs expose a Private DNS screen of their own, and whether these commands stick
across reboots on each OEM build, is **UNVERIFIED**.

If you do set Private DNS, do not also reject port 853 at the router. DNS-over-TLS runs on 853 and is
trivial to reject, which is what the OpenWrt hardening in
[Router enforcement](../router-enforcement.md) does. Set both and the TV loses name resolution. A local
DoT endpoint is the pairing that works. Technitium is a DoH, DoT and DoQ server as well as a resolver,
so you can hand the TV a private encrypted endpoint inside your own network.

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: hand out your
resolver with DHCP option 6, redirect TCP and UDP port 53 to it with the self-exclusion rule, and build
the IPv6 twin at the same time. A pre-Google-TV Chromecast ignores option 6 and dials 8.8.8.8, so on
those the redirect is the only thing that does anything. Router Advertisements can hand any device a
resolver through the RFC 8106 RDNSS option with no DHCPv6 involved, so every rule needs an IPv6
version. See [IPv6 leaks](../ipv6-leaks.md).

### What to block

This is the weakest data in the project and you should know that before you start.

| Platform | HaGeZi native list | Entries |
| --- | --- | --- |
| Amazon Fire OS | `native.amazon` | 369 |
| LG webOS | `native.lgwebos` | 341 |
| Samsung Tizen | `native.samsung` | 199 |
| Apple tvOS | `native.apple` | 108 |
| **Google TV and Android TV** | **none exists** | **0** |

There is no HaGeZi native list for Google or Android TV [8], and the community has isolated exactly
three platform hostnames: `androidtvchannels-pa.googleapis.com`,
`androidtvlauncherxfe-pa.googleapis.com` and `androidtvwatsonfe-pa.googleapis.com`. Everything else
Google's platform telemetry uses is co-mingled with load-bearing `*.googleapis.com` hosts that the Play
Store, app updates and the launcher all depend on.

That changes the strategy compared with LG or Samsung. On an LG set you can point a resolver at 341
vendor-specific entries backed by per-domain breakage notes and expect the TV to keep working. Here you
have three hostnames plus the general ad networks, and the aggressive move (wildcarding
`googleapis.com`) breaks the device. Block the three `-pa` hosts plus `googleads.g.doubleclick.net`,
`partnerad.l.doubleclick.net` and `2mdn.net`, keep [the never-block set](#what-never-to-block) intact,
and treat anything broader as an experiment you run knowingly. The Blokada log from a Sony Android
TV [6] shows a device-side blocker catching those doubleclick hosts in practice.

Generated lists: [`blocklists/fightback-tv-google.txt`](../../blocklists/)

### What never to block

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `play.google.com` | Play Store, so app installs and updates | Project never-block set |
| `*.gvt1.com` | Google content and update delivery | Project never-block set |
| `android.apis.google.com` | Platform API calls | Project never-block set |
| `*.googleapis.com` | Play Store, updates and the launcher. Platform telemetry is co-mingled here, which is what makes this platform hard | Project never-block set |
| `connectivitycheck.android.com`, `connectivitycheck.gstatic.com` | Captive-portal check. The device decides it has no internet and retries | Project never-block set |
| `time.google.com` | Time sync | Project never-block set |
| `ota.googlezip.net` | Firmware updates | Project never-block set |
| `applicast.ga.sony.net`, `portal.store.sonyentertainmentnetwork.com`, `update.biv.sony.tv` | Sony apps, store and firmware updates | Project never-block set, Sony |

*The breakage column names the service each host serves. Unlike our LG and Samsung sets, this one
carries no per-domain test notes, so treat the specific symptom as unconfirmed. Perflyst is the only
list in this space with per-domain breakage annotations and it has been stale since 13 July 2023 [9].*

When you do block something, answer with NXDOMAIN rather than SERVFAIL, and REJECT rather than DROP.
Some firmware reads a silent drop as no internet and retries aggressively.

### Hardcoded addresses

Pre-Google-TV Chromecast hardcodes 8.8.8.8 and 8.8.4.4 with no DNS UI. A port 53 redirect catches
those, because they are DNS queries to a known port.

No hardcoded telemetry IP addresses are documented for this platform, which is an absence of evidence
rather than evidence of absence. For LG we know about an OTA fallback at `156.147.69.32:8080` and a
telemetry dial to `54.186.247.229:443` only because somebody ran a WAN-side capture on a rooted set.
Nobody has done that here.

## Tier 2: developer mode and sideloading

**Time:** 1 hour. **Risk:** low. **Reversible:** yes. **Warranty:** unaffected, ADB is an official
Android feature.

**What breaks:** nothing by enabling it. Network debugging leaves a listening port on your LAN, so
turn it off when you are finished.

**The path to enable Developer options and ADB debugging on Android TV and Google TV is not yet
documented in our notes.** The seven-click path our notes record is the Fire OS one and does not apply
here. This gap blocks Tier 3 for readers, so it is our highest-priority correction. See
[Open questions](#open-questions).

Once ADB is reachable, these are the commands this page uses:

```
adb connect <ip>:5555
adb install app.apk
adb shell pm disable-user --user 0 <package>
adb shell pm enable <package>
```

Prefer `pm disable-user` over `pm uninstall`. Both take the package out of service for the current user,
and `disable-user` has a documented one-command reversal. The circulated Sony debloat one-liner uses
`pm uninstall --user 0` [4], and our notes record no restore command for that short of a factory reset.

ADB is not root, so you cannot edit a hosts file or add firewall rules with it. What it gives you is
package disabling, the Private DNS settings above, sideloading a third-party launcher such as
FLauncher [3], and headless control of a capture app. See
[Running a network observer](#running-a-network-observer).

## Tier 3: disable preinstalled advertising and metrics apps

**Time:** 1 hour. **Risk:** medium. A wrong package can stop the TV booting.
**Reversible:** yes, by re-enabling or factory reset.

> ### Do not remove `com.android.vpndialogs`
>
> A widely shared Sony debloat one-liner includes `pm uninstall --user 0 com.android.vpndialogs` [4].
> That package is the system VPN consent dialog, and it is the only thing that can grant
> `VpnService.prepare()`. Remove it and no network monitoring app can ever be given permission on that
> device again, because there is no dialog left to approve it. Re-enabling does not bring back a
> permission you can no longer be asked for.
>
> This one package decides whether you can ever watch what your TV sends. Read any one-liner in full
> before you paste it.

### Package safety is per model

| Source | Verdict on `com.google.android.tvrecommendations` |
| --- | --- |
| TCL-Google-TV-Debloat-Optimizer [5] | The primary safe-debloat target |
| Sony Google TV debloat guide [4] | Listed under "will cause a boot loop if removed" |

Both are probably right about their own hardware. That contradiction is why our package data lives in
[`data/packages/android-tv.yml`](../../data/packages/android-tv.yml) scoped to the models each package
was tested on, and why this page will never carry one combined list.

**Never run a cross-OEM one-liner.** A command written for a TCL set, pasted into a Sony set, is how
people end up at a factory reset. If a guide hands you one line that removes forty packages, it was
written for one device and yours is not it.

### Safe to disable, Sony

| Package | What it is | Tested on | Source |
| --- | --- | --- | --- |
| `tv.samba.ssm` | Samba TV. Ad tracking and viewing data collection. The highest-value removal on a Sony set. | Sony Google TV | [4], also present in TCL lists [5] |
| `com.sony.dtv.sonybugreportsys` | Bug report system | Sony Google TV | [4] |
| `com.sony.dtv.system.crashlog` | Crash log collection | Sony Google TV | [4] |
| `com.sony.dtv.customersupport`, `com.sony.dtv.da.service` | Sony diagnostics group. Individual functions not documented in our notes. | Sony Google TV | [4] |
| `com.sony.dtv.promos`, `com.sony.dtv.sonyselect` | Promotional and content-promotion packages | Sony Google TV | [4] |
| `com.sony.dtv.demomode` | Retail demo mode | Sony Google TV | [4] |

### Safe to disable, TCL

| Package | What it is | Tested on | Source |
| --- | --- | --- | --- |
| `com.tcl.screenadservice` | The TCL ad service | TCL Google TV | [5] |
| `com.tcl.browser`, `com.tcl.tv.appstore`, `com.tcl.usercenter`, `com.tcl.screensaver` | Listed in the TCL toolkit. Functions not documented in our notes, so check what you lose before disabling each one. | TCL Google TV | [5] |

We have no package data for Hisense, Philips, Sharp, Toshiba, onn or Nvidia Shield. Do not borrow the
Sony or TCL tables for them. See [Open questions](#open-questions).

### The setupwraith correction

Plenty of debloat lists put `com.google.android.tungsten.setupwraith` in the telemetry column. It does
not belong there. It is the Android TV Setup Wizard and the fallback launcher [3], and it only needs
disabling in one situation: you have already disabled `com.google.android.apps.tv.launcherx`, you want a
third-party launcher such as FLauncher to stick, and setupwraith keeps re-enabling the default one.
Outside that sequence, disabling it buys you no privacy at all. That sequence also has a known side
effect on Chromecast with Google TV, where disabling the default launcher stops the YouTube button on
the remote working [3].

### Do not disable

| Package | What breaks | Source |
| --- | --- | --- |
| `com.google.android.webview` | The entire UI | [4] |
| `com.google.android.katniss` | Essential to the launcher | [4] |
| `com.sony.dtv.tvx` | Kills the boot process | [4] |
| `com.google.android.tts` | Documented boot loop on Sony Google TV | [4] |
| `com.android.location.fused` | Documented boot loop on Sony Google TV | [4] |
| `com.android.vpndialogs` | Permanently prevents any network monitoring app from being granted VPN permission | [4], Android `VpnService` documentation |
| `com.google.android.tvrecommendations` | Boot loop on Sony, safe on TCL. Model-gated, check your model first | [4] [5] |

### Undoing it

```
adb shell pm enable <package>
```

If the TV will not boot, or you used `pm uninstall --user 0` and want the package back, a factory reset
restores the stock package set. Find the factory reset option on your model before you start Tier 3.

## Running a network observer

This is one of only three platforms in the project where a third-party app can watch the traffic other
apps generate. Samsung's Network API reference says Tizen "does not provide traffic monitoring or packet
inspection capabilities", and on Roku the scripting layer cannot see other apps at all. Here it works. A
Blokada issue thread carries output from a Sony Android TV blocking `googleads.g.doubleclick.net` and
`securepubads.g.doubleclick.net` on-device [6].

**How it works.** Android's `VpnService` documentation states that "if you don't create allowed or
disallowed lists, the system sends all network traffic through the VPN". A local tunnel with no upstream
server therefore sees every app's traffic by default, with no root and no certificate trickery. Per-app
attribution uses `ConnectivityManager.getConnectionOwnerUid` on Android 10 and later and falls back to
`/proc/net/tcp` and `/proc/net/udp` below that. DNS tracking is clean on Android 12 and later,
heuristic below it.

**Do not fork a capture app, drive one.** PCAPdroid declares `android.software.leanback`, a
`LEANBACK_LAUNCHER` intent, a banner and `touchscreen` as not required, added Android TV support in
1.3.0 on 5 March 2021, and extracts hostnames from DNS, TLS and HTTP. It takes headless ADB commands:

```
adb shell am start -e action start -e api_key <KEY> \
  -n com.emanuelef.remote_capture/.activities.CaptureCtrl
```

Actions are `start`, `stop` and `get_status`, with `pcap_dump_mode`, `app_filter`, `collector_host` and
`collector_port`. An Android TV fork of RethinkDNS also exists, with a `tv` Gradle flavour and Compose
for TV navigation, proposed upstream at celzero/rethink-app#2664 [7]. Talk to that maintainer before
writing Android code of your own.

**Start the capture before the TV boots.** The 2024 IMC team found most DNS requests fire in the first
seconds after activation [11], so a late start loses the hostname-to-address mapping for the session.

**The five things that will bite you.**

| Problem | Detail |
| --- | --- |
| Always-on VPN often has no UI | Nvidia Shield "does not have that option". The ADB fallback writes `always_on_vpn_app` and `always_on_vpn_lockdown` with `settings put secure`, but whether that arms it without device-owner privileges is **UNVERIFIED** and is the first thing to test on hardware |
| D-pad navigation | Third-party VPN app interfaces are frequently not navigable with a TV remote, so expect to fight the UI |
| One VPN at a time | Android allows a single active VPN, so an observer conflicts with a commercial VPN on the same device. You cannot run both |
| Boot loops | A VPN service caused boot loops on some older Sony firmware. Have your factory reset path ready before you install one, and do not turn on always-on lockdown until the app has survived several reboots |
| `com.android.vpndialogs` | If a debloat script already removed it, none of this works. See [the warning in Tier 3](#tier-3-disable-preinstalled-advertising-and-metrics-apps) |

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.** The answer depends entirely on
which device you have.

| Device | Unlock status |
| --- | --- |
| Nvidia Shield | Officially supported by LineageOS as `foster`, and NVIDIA publishes stock recovery images. The lowest-risk unlock in this category. |
| Chromecast with Google TV | No bootloader unlock or root project exists. **UNVERIFIED negative**, we could not find one. |
| Google TV Streamer | No bootloader unlock or root project exists. **UNVERIFIED negative**. |
| Sony, TCL, Hisense, Philips, Sharp, Toshiba, onn TVs | Locked bootloaders. |

**What root gets you:** on a Shield, replacing the OS rather than negotiating with it. You end up on a
community Android build instead of a vendor one, which is a different proposition from rooting a TV.

**What it costs you:** the warranty and the vendor's update path. Everything in Tier 0 through Tier 3
is reversible from the TV's own menus. This is not.

**Where to go:** the LineageOS device page for `foster`, and NVIDIA's own developer downloads for stock
recovery images. Our notes record neither URL, so we are not printing guesses. Legal context for the
category is [37 CFR 201.40(b)(10)](https://www.ecfr.gov/current/title-37/section-201.40), the DMCA
exemption covering smart TVs and streaming devices.

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Personalised recommendations and personalised ads. Nothing else documented. | Turn the toggle back on |
| 1 | Nothing, if you keep the never-block set. Over-blocking `*.googleapis.com` takes out the Play Store, updates and the launcher together | Remove the entry, restart the resolver |
| 2 | Nothing. A debugging port stays open until you disable it | Turn off Developer options |
| 3 | Depends on the package. The wrong one is a boot loop | `adb shell pm enable <package>`, or factory reset |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is a router-side
or WAN-side packet capture on port 53 filtered to the TV's address, because 68% of smart TVs in a
200-home study ignored the resolver their router handed them [2], and a static DNS entry in the TV's own
menu proves nothing about what the TV queries.

1. On a pre-Google-TV Chromecast, confirm the port 53 redirect is catching traffic aimed at 8.8.8.8. If
   it is not, nothing you configured is in effect.
2. Repeat every check over IPv6. See [IPv6 leaks](../ipv6-leaks.md).
3. Start the capture before you power on the TV, not after.

## Open questions

Each of these is something a reader with the hardware can settle and we cannot.

1. **The Developer options and ADB enable path**, per OEM. Blocks Tier 2 and Tier 3 for readers, so it
   is the highest-priority correction on the page.
2. **The Samba TV menu path on Sony**, if one exists. Removing `tv.samba.ssm` is currently the only
   route we can document for the highest-value item here.
3. **Microphone, voice and local network settings paths**, for both Android TV and Google TV.
4. **Which OS versions the Tier 0 paths apply to.** We have no generation range at all.
5. **Private DNS per OEM.** Whether any OEM ships the screen, and whether the ADB settings survive a
   reboot.
6. **Whether `settings put secure always_on_vpn_app` arms always-on VPN without device-owner
   privileges.** First thing to test on real hardware.
7. **The endpoint list.** Three `-pa.googleapis.com` hostnames is not a platform inventory. A capture
   from any device in the covers list is the most valuable contribution anyone can make here.
8. **Package data for Hisense, Philips, Sharp, Toshiba, onn and Nvidia Shield.** We have Sony and TCL.
9. **Hardcoded IP dials.** No WAN-side capture exists, so we cannot say whether this platform has
   LG-style hardcoded addresses that DNS filtering cannot touch.
10. **Root for Chromecast with Google TV and the Google TV Streamer** is an UNVERIFIED negative.
11. **Upstream URLs** for the LineageOS `foster` device page and NVIDIA's recovery images.
12. **Whether a firmware update re-enables the Tier 0 toggles.** Undocumented and measurable.
13. **Whether PCAPdroid runs on each OEM build** in the covers list.

## Sources

1. [AOSP TvSettings](https://android.googlesource.com/platform/packages/apps/TvSettings/+/refs/heads/main/Settings/),
   for the DNS screens and the absent Private DNS preference.
2. [Mazhar and Shafiq, IoTDI 2020](https://arxiv.org/abs/2001.08288) §IV-C, for the 68% figure. The
   repeated 72% figure mis-cites this paper.
3. [FLauncher](https://github.com/osrosal/flauncher), for the `setupwraith` correction.
4. [sony-google-tv-debloat](https://github.com/ironshadow786786-boop/sony-google-tv-debloat), for Sony
   packages, the boot loop set, and the `com.android.vpndialogs` one-liner.
5. [TCL-Google-TV-Debloat-Optimizer](https://github.com/livvaa/TCL-Google-TV-Debloat-Optimizer), for TCL
   packages and the opposite verdict on `com.google.android.tvrecommendations`.
6. [Blokada issue 134](https://github.com/blokadaorg/blokada/issues/134), a log from a Sony Android TV.
7. [ezelab/rethink-tv](https://github.com/ezelab/rethink-tv) and
   [celzero/rethink-app#2664](https://github.com/celzero/rethink-app/issues/2664).
8. [HaGeZi DNS blocklists](https://github.com/hagezi/dns-blocklists), for native list counts.
9. [Perflyst PiHoleBlocklist](https://github.com/Perflyst/PiHoleBlocklist), stale since 13 July 2023.
10. [Varmarken et al., PETS 2020](https://arxiv.org/abs/1911.03447), on first-party telemetry coverage.
11. [Anselmi et al., IMC 2024](https://arxiv.org/html/2409.06203v1), on opt-out working and on DNS
    requests firing seconds after activation.
12. [OpenWrt: intercept DNS](https://openwrt.org/docs/guide-user/firewall/fw3_configurations/intercept_dns).
13. [37 CFR 201.40(b)(10)](https://www.ecfr.gov/current/title-37/section-201.40), the DMCA exemption.
