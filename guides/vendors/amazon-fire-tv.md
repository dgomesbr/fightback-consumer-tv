---
title: Amazon Fire TV (Fire OS)
platform: fire-os
brands: [Amazon, Insignia, Toshiba, Panasonic]
generations: "Fire OS 5.2.x through 7.x. Every breakage below is scoped to the build it was seen on."
dns_field: static-ip-required
dev_mode: yes
adb: yes
package_disable: yes
root: available
max_tier: 4
updated: 2026-09-08
---

# Amazon Fire TV (Fire OS)

Fire OS is Android with Amazon's launcher and services on top, and that inheritance is the most useful fact
about it. Android's `VpnService` API lets a third-party app route and inspect the whole device's traffic, so
on a Fire TV you can watch what every other app contacts, from the box itself, with no router changes and no
root. Only three platforms in this project support that at all: Fire OS, Android TV and Google TV, and tvOS
17, which sees the whole device but cannot attribute traffic to an app. Fire OS also has ADB, package
disabling, and on two sticks a bootrom root, making it one of the best-supported devices here.

**Covers:** Fire TV Stick, Stick Lite, Cube, Fire TV Edition sets and Fire TV built-in televisions, Fire OS
5.2.x through 7.x
**Also sold as:** Insignia and Toshiba Fire TV Edition sets in the US. Panasonic ships Fire TV built into
several current flagships; older Panasonic sets run My Home Screen, for which no path is known.
**How far you can get:** Tier 4, but Tier 3 is where the value is. Package disabling over ADB kills the
metrics stack on the device. Tier 4 root covers two SKUs on old firmware and is destructive.

## What this device sends home

The IMC 2024 study that measured frame sampling rates covered Samsung and LG only, so "not documented"
below means nobody published the number, not that the number is zero.

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Device and usage metrics | `device-metrics-us.amazon.com` plus its `-us-2` and `-us-ud` siblings, `mobileanalytics.us-east-1.amazonaws.com`, `minerva.devices.a2z.com`, `forester.a2z.com`, `federatedanalytics.amazon.com`, `fls-na` / `fls-eu` / `fls-fe` `.amazon.<tld>`, `device-messaging-na.amazon.com`, `mas-sdk.amazon.com`, `d3p8zr0ffa9t17.cloudfront.net` | Not documented | HaGeZi `native.amazon`, 369 entries [5]. PETS 2021 saw `device-metrics-us.amazon.com` and `mas-sdk.amazon.com` and classified both non-required [1] |
| First-party advertising | `aax-ott.amazon-adsystem.com`, `aax-eu.amazon-adsystem.com` and roughly 189 `*.amazon-adsystem.com` hosts, `mads.amazon.com`, `mads-eu.amazon.com` | Not documented | HaGeZi `native.amazon` [5]. PETS 2021 classified `aax-eu.amazon-adsystem.com` non-required [1] |
| Message and shopping surfaces | `msh.amazon.com` | Not documented | PETS 2021, non-required [1] |
| Third-party tracking inside channels | `amazon-adsystem.com` reached by 687 of the top 1,000 Fire TV channels | Per channel session | CCS 2019 [2] |
| Wi-Fi network name | SSIDs observed leaving toward trackers | Not documented | CCS 2019 [2] |
| Content recognition | Not yet documented. See [Open questions](#open-questions). | Not documented | No source |

PETS 2021 [1] split every destination a device contacted into required and non-required. Fire TV needed
three: `api.amazon.com`, `unagi-eu.amazon.com` and `youtube.com`. It contacted **11 non-required
destinations, the highest count of any device the study tested.** Three required against eleven optional is
what makes DNS filtering effective here rather than marginal. One trap sits inside that result:
`api.amazon.com` appears on **both** lists, because it multiplexes several services down one hostname. Some
of what goes there is telemetry and some is the device functioning, and DNS cannot separate them, so
`api.amazon.com` goes on the never-block list and stays there. PETS 2020 [3] adds that blocklists defend
better against third-party trackers than against a platform's own first-party telemetry, which is why the
Amazon list in Tier 1 goes on top of a general list rather than instead of one.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

Nothing here stops video playing. Turning off Featured Content stops the home screen auto-playing trailers
at you, which most people want anyway. Both paths below are ⚠️ **needs-confirmation**: Amazon's own help
page for privacy settings returned HTTP 503 during research, so no vendor document backs them. They come
from secondary sources and from the October 2018 release that added the screen.

### Turn off content recognition

| Generation | Path | Status |
| --- | --- | --- |
| All | Not yet documented. See [Open questions](#open-questions). No content recognition toggle, endpoint or cadence for Fire OS appears in our research corpus. | No source |

### Turn off ad tracking and personalisation

| Generation | Path | Status |
| --- | --- | --- |
| Fire OS 6 and later, shipped October 2018 | Settings > Preferences > **Privacy Settings**, then turn off **Device Usage Data**, **Collect App Usage Data** and **Interest-based Ads** | ⚠️ needs-confirmation |
| Fire OS 6 and later | Same screen, **Your Advertising ID**, reset it | ⚠️ needs-confirmation |

Turn the toggles off first, then reset the advertising ID. The toggles stop new linkage; the reset breaks
the key on the existing profile.

### Other settings worth changing

**Autoplay on the home screen.** Settings > Preferences > **Featured Content**, where both video and audio
autoplay live. ⚠️ needs-confirmation.

**What this does not fix:** every hostname in the table above still resolves and still connects. This screen
changes what Amazon says it does with the data, not whether the device talks to
`device-metrics-us.amazon.com`. And Sticks are widely reported to reach 8.8.8.8 whatever DNS server your
router hands them [**UNVERIFIED**, anecdotal], which lines up with IoTDI 2020 measuring 68% of smart TVs
across 200-plus homes reaching Google Public DNS directly [4]. If that holds for your stick, only a router
rule works.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

**Read this before you touch anything.** Fire OS will not let you set DNS on its own. The DNS fields sit
inside the static IP form, so you also have to assign the device a fixed address, gateway and prefix
length. On many builds that form is not reachable from a network you have already joined: you have to
**forget the network and rejoin it**, because the DNS fields only appear on the Advanced path during a
fresh join. The flow drops your Fire TV off Wi-Fi halfway through, and without the password to hand you
will be typing it with a D-pad. Get the password and your router's address range in front of you first,
and read [Router enforcement](../router-enforcement.md) for picking a safe address. Second warning: some
builds have silently ignored custom Wi-Fi DNS [7], accepting the value and asking somewhere else anyway,
so never treat the field as done until you have watched queries arrive in your resolver log.

### On the device

**Wi-Fi.** Settings > **Network**, highlight your network, forget it, then rejoin and choose
**Advanced** rather than **Connect**. Enter IP address, gateway, network prefix length, **DNS 1** and
**DNS 2**. ⚠️ needs-confirmation, secondary source [7].

**Wired.** Settings > **Network** > **Configure Network**. ⚠️ needs-confirmation [7].

**Private DNS over ADB.** Android's encrypted DNS setting has no Fire OS interface, but the framework keys
are writable over ADB once you have finished Tier 2. Community-documented, Fire OS specifics **UNVERIFIED**.
It sidesteps DHCP, and a router-side port 53 redirect cannot see it, since DNS-over-TLS on port 853 gets
rejected rather than redirected. Point it at your own resolver or leave it alone.

```
adb shell settings put global private_dns_mode hostname
adb shell settings put global private_dns_specifier dns.example
```

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: set the on-device
DNS fields because you can, then assume they do not work and enforce it at the router anyway.

- **DHCP option 6**, defined in [RFC 2132](https://www.rfc-editor.org/rfc/rfc2132.html) §3.8 [17]. Set it
  first, since it gives clean per-client attribution in the query log.
- **Redirect TCP and UDP port 53** to your resolver, excluding the resolver itself. That is the
  `src_ip="!<resolver>"` line in OpenWrt's documented recipe [16]. Omitting it causes a redirect loop and
  is the step people forget. Reject port 853 in the same pass.
- **Build the IPv6 twin of every rule.** RFC 8106 [18] lets a Router Advertisement hand a device a
  resolver through the RDNSS option, type 25, with no DHCPv6 involved. See [IPv6 leaks](../ipv6-leaks.md).
- **Answer with NXDOMAIN, not SERVFAIL, and REJECT rather than DROP.** Some firmware reads a SERVFAIL or
  a silent drop as no internet and retries hard. Carrier-grade NAT is irrelevant here, whatever the
  forum thread says.

### What to block

The endpoint list lives in `data/endpoints/amazon.yml`, with a flag on each entry for what it breaks.
Take hostnames from there rather than from this page, because the YAML is the copy that gets corrected.
Generated lists: [`blocklists/fightback-tv-amazon.txt`](../../blocklists/)

HaGeZi's `native.amazon` carries 369 entries, is GPL-3.0 and updates several times daily [5]. Their own
guidance: Light and Normal include only native trackers that do not break things, and Ultimate blocks
everything and does break things. Pro plus `native.amazon` suits a household with a Fire TV.

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.amazon-onlydomains.txt
```

Two hostnames one word apart, going opposite ways. **`mas-sdk.amazon.com` is safe to block** and PETS
2021 classified it non-required [1]. **`mas-ext.amazon.com` breaks app installs** [5].

### What never to block

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `api.amazon.com` | The device. PETS 2021 lists it as required. It also appears on the non-required list because it multiplexes services, so DNS filtering cannot separate the two. Leave it. | [1] |
| `unagi-eu.amazon.com` | The device. Required per PETS 2021. | [1] |
| `youtube.com` | YouTube. Required per PETS 2021. | [1] |
| `mas-ext.amazon.com` | App installs | [5] |
| `amazonadsi-a.akamaihd.net` | App installs and updates | [5] |
| `softwareupdates.amazon.com` and its CloudFront hosts | System updates | [5] |
| `ftv-smp.ntp-fireos.com` | Time sync. Blocking a time source produces no error message. It produces a device whose clock drifts, and certificate validation then starts failing a few days later in ways that look nothing like a DNS problem. | [5] |
| `2.android.pool.ntp.org` | Time sync, same consequence | [5] |
| Alexa endpoints | Voice control | [5] |

### Hardcoded addresses

No IP:port pair that Fire OS dials without a DNS lookup has been documented. That is a research gap rather
than a clean result; the only platform where such addresses have been captured is LG, and that took a rooted
set. The 8.8.8.8 report above is a hardcoded *resolver* rather than a destination, and the port 53 redirect
catches it. Finding a hardcoded destination needs a WAN-side capture.

## Tier 2: developer mode, sideloading and traffic observation

**Time:** 1 hour. **Risk:** low. **Reversible:** yes. **Warranty:** unaffected, this is an official
vendor feature.

Enabling ADB breaks nothing by itself. It does open a network service on your Fire TV that accepts
commands without a password, so do it on a network you control and turn it off when you are finished.

### Enable it

Settings > **Device** or **My Fire TV** > **Developer Options**, then enable **ADB Debugging** and
**Apps from Unknown Sources**. On some builds Developer Options stays hidden until you go to Settings >
My Fire TV > **About** > **Your TV** and click the D-pad seven times. ⚠️ needs-confirmation.

```
adb connect <ip>:5555
adb install app.apk
```

### What this actually buys you

Whole-device traffic observation, which is rare in this category. Android's documentation states that "if
you don't create allowed or disallowed lists, the system sends all network traffic through the VPN" [10], so
a local `VpnService` app sees every app's connections. Per-app attribution comes from
`ConnectivityManager.getConnectionOwnerUid` on Android 10 and later, or from `/proc/net/tcp` and
`/proc/net/udp` below that. DNS tracking is clean on Android 12 and later, heuristic below it.

The tool to reach for is **PCAPdroid** [12]. Its manifest already declares `android.software.leanback`, a
`LEANBACK_LAUNCHER` intent, a TV banner and `touchscreen` as not required, and its changelog records "Add
Android TV support" in 1.3.0 on 5 March 2021. It extracts hostnames from DNS, TLS and HTTP, so you get the
names without decrypting anything, and it runs headlessly with actions `start`, `stop` and `get_status`:

```
adb shell am start -e action start -e api_key <KEY> \
  -n com.emanuelef.remote_capture/.activities.CaptureCtrl
```

**PCAPdroid on Fire OS is UNVERIFIED** and is an explicit test item for this project, so if you run it,
report whether it worked and on which build. `VpnService` blocking has been proven on a TV, though not on a
Fire TV: a [Blokada log from a Sony Android TV](https://github.com/blokadaorg/blokada/issues/134) shows it
blocking `googleads.g.doubleclick.net` and `securepubads.g.doubleclick.net` [11].

Three gotchas nobody mentions until you hit them. Only one VPN can be active at a time, so a local observer
conflicts with a commercial VPN client. Always-on VPN often has no interface on TV platforms, and the ADB
fallback writes `always_on_vpn_app` and `always_on_vpn_lockdown` under `settings put secure`, but whether
that arms it without device-owner privileges is **UNVERIFIED and is the first thing to test on hardware**;
without always-on the observer stops at reboot and loses the window that matters, since most DNS requests
fire in the first seconds after activation [20]. And third-party VPN interfaces are frequently not D-pad
navigable.

### Publishing to the Amazon Appstore

Amazon's store is the least hostile in this project, which matters because a phase-2 companion app could
plausibly ship there. No developer registration fee is documented, and the publish cycle runs every 30 to 90
minutes rather than in days. The Developer Services Agreement prohibits interference and malware but has no
`VpnService` clause on record [15], though several Amazon content policy pages returned 404 during research
so a clause may exist and simply be unreadable. Google Play by comparison bans "apps that block or interfere
with another app displaying ads", and Apple's guideline 5.4(a) requires a VPN app come from a VPN provider.
Working judgment: a logger can go to the store, a blocker ships as a sideload.

## Tier 3: disable preinstalled advertising and metrics apps

**Time:** 1 hour. **Risk:** medium, a wrong package can break the Settings UI or stop the device
booting. **Reversible:** yes, by re-enabling or factory reset.

This is the strongest tier on this platform and the one most likely to go wrong. Read all four warnings
before you run a single command.

**1. Use `pm disable-user`, never `uninstall`.** On Fire OS, `pm uninstall --user 0` removes the package for
the current user and takes the easy recovery path with it. `pm disable-user` leaves it in place, switched off.

**2. Have the re-enable command open in another window before you start.** The documented failure mode is a
broken **Settings UI**, and if Settings will not open you cannot reach the factory reset menu with the
remote. Your ADB connection is the only way back in, so do not close it.

```
adb shell pm disable-user --user 0 <package>
adb shell pm enable <package>
```

**3. Version-gate everything.** Every breakage below was observed on a named Fire OS build, and the ones
that were not are marked. Check your build in Settings > My Fire TV > About first, and treat a package as
unknown if your build is not the one in the source. Across platforms,
`com.google.android.tvrecommendations` is the primary safe removal in one community guide and a documented
boot loop in another, and both are probably right for their own hardware.

**4. The metrics packages are both the most valuable to disable and the most likely to break Settings.**
Amazon's metrics stack is what feeds `device-metrics-us.amazon.com`, and adjacent packages with almost
identical names are load-bearing for the Settings app on 5.2.6.3. Disable one, confirm Settings still
opens, then do the next. Batching them is how people end up with a device they can only fix over ADB.

### Safe to disable

Both clusters come from two community debloat scripts, `firestick-loader` [8] and `Fire-Tools` [9], which
list packages without per-package descriptions, so this page invents none. The canonical, model-scoped
copy is [`data/packages/fire-os.yml`](../../data/packages/fire-os.yml). Do the metrics group one package at
a time. The advertising group carries lower risk to Settings and makes a more visible change to the
interface.

```
# metrics and diagnostics
com.amazon.device.metrics
com.amazon.device.logmanager
com.amazon.device.crashmanager
com.amazon.tv.fw.metrics
com.amazon.wirelessmetrics.service
com.amazon.dp.logger
com.amazon.minerva.client.api
com.fireos.usagestats.proxy
com.amazon.connectivitydiag
com.amazon.android.service.networkmonitor

# advertising and home screen
com.amazon.videoads.app
com.amazon.hedwig
com.amazon.firehomestarter
com.amazon.ftv.glorialist
com.amazon.firespotlight
com.amazon.kindle.kso
com.amazon.advertisingidsettings
com.amazon.hybridadidservice
com.amazon.tv.launcher
```

One caveat on `com.amazon.tv.launcher`. It sits in the advertising and home screen cluster in both source
scripts, and its name indicates it is the home screen itself. Our corpus records no observation of what
happens after disabling it and no replacement launcher path for Fire OS, so leave it until last and expect
to re-enable it.

### Do not disable

| Package | What breaks | Fire OS build observed | Source |
| --- | --- | --- | --- |
| `com.amazon.client.metrics`, `com.amazon.client.metrics.api`, `com.amazon.metrics.api` | Settings UI | 5.2.6.3 | [8] [9] |
| `com.amazon.device.settings.sdk.internal.library` | Device settings and Application settings | Not recorded | [8] [9] |
| `amazon.jackson19` | Display settings and Applications settings | 5.2.7.2 | [8] [9] |
| `com.amazon.application.compatibility.enforcer` | Must stay enabled on this build | 5.2.7.2 | [8] [9] |
| `com.amazon.identity.auth.device.authorization` | Amazon account logins, and Netflix | Not recorded | [8] [9] |
| `com.amazon.imp`, `com.amazon.tv.oobe` | Applications and sign-in | 5.2.6.3 | [8] [9] |
| `com.android.vpndialogs` | ☠️ The system VPN consent dialog. Remove it and `VpnService.prepare()` can never be granted again, so no traffic observer will ever run on that device. Documented in a Sony Google TV debloat one-liner, and Fire OS is Android-derived, so treat it as forbidden here. **Presence and behaviour on Fire OS is UNVERIFIED.** | Not observed on Fire OS | [14] |

Read the first three rows against the safe list. `com.amazon.device.metrics` is safe to disable and
`com.amazon.client.metrics` breaks Settings. The names differ by one word.

### Undoing it

`adb shell pm enable <package>` re-enables one package. Disabling with `pm disable-user` modifies no
firmware, and a factory reset undoes it; see [LEGAL.md](../../LEGAL.md). The factory reset menu path on Fire
OS is not documented in our corpus, so it sits in the open questions. If Settings is broken and you cannot
navigate there, re-enable over ADB first and reset from a working Settings app afterwards.

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

Root on Fire OS exists for exactly two SKUs. The **Fire TV Stick 3rd generation**, codename `sheldonp`, and
the **Fire TV Stick Lite**, codename `sheldon`, can be rooted through the MediaTek bootrom exploit known as
`kamakiri`, and only on Fire OS builds **below 7.2.7.3**. It needs a USB cable and a Linux host. Every
other Fire TV generation is **UNVERIFIED**, in both directions.

There is a scheduling trap in it. During setup you must block three Amazon hosts,
`amzdigitaldownloads.edgesuite.net`, `softwareupdates.amazon.com` and `updates.amazon.com`, or the device
updates itself past the vulnerable build while you are still working and the window closes permanently. Two
of those three are on the never-block list in Tier 1 for good reason, so it is a temporary state you undo
afterwards, not a configuration to leave in place.

**What root gets you:** on-device filtering that travels with the device and survives leaving your network,
which is the one thing router-based blocking cannot do. The proof of concept is on webOS rather than Fire
OS, where the Homebrew Channel's startup script bind-mounts a writable hosts file and appends vendor update
servers to it. Nobody has published the Fire OS equivalent.

**What it costs you:** the process is destructive and voids the warranty, it needs firmware old enough that
you are trading away security patches to keep the vulnerability, and a failure leaves a dead stick rather
than a degraded one. Sticks are cheap enough that Tier 3 plus a router rule is the better trade for almost
everyone.

**Where to go:** the `kamakiri` MediaTek bootrom exploit project. No verified upstream URL was recorded
during research and this project does not guess links to exploit code, so locating that permalink is an open
question below. We do not reproduce exploit steps, payloads or firmware patching procedures.
[37 CFR 201.40(b)(10)](https://www.ecfr.gov/current/title-37/section-201.40) [19] covers streaming sticks as
well as televisions but does not displace a licence agreement. See [LEGAL.md](../../LEGAL.md).

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Ads become less relevant. The home screen stops auto-playing trailers. Playback unaffected. | Turn the setting back on in Settings > Preferences > Privacy Settings |
| 1 | Over-blocking makes apps fail to load or installs fail. Blocking the NTP hosts breaks the clock, which later breaks certificate validation in ways that do not look like DNS. The static IP flow drops the device off Wi-Fi mid-change. | Remove the entry from your resolver and reboot the device. Switch the network back to DHCP in Settings > Network |
| 2 | ADB leaves an unauthenticated network service open. A local `VpnService` app blocks any commercial VPN from running. | Turn off ADB Debugging in Developer Options. Uninstall the observer app |
| 3 | Documented: the Settings UI, Display settings, Applications settings, Amazon logins and Netflix, depending on package and build. See the do-not-disable table. | `adb shell pm enable <package>`, or a factory reset |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform the check that matters most is **confirming
the on-device DNS field is actually honoured**, because some builds accept the value and ask elsewhere
anyway [7], and because Sticks are reported to reach 8.8.8.8 regardless of DHCP. Filter your resolver's
query log to the Fire TV's address and watch for a few minutes while the device sits idle on the home
screen. Silence means it is asking somewhere you cannot see.

Then capture the LAN side on port 53, port 853 and UDP 443, and repeat over IPv6. **Start the capture before
the Fire TV boots.** The IMC 2024 team noted most DNS requests fire in the first seconds after activation
[20], so a late start loses the hostname-to-address mapping and everything afterwards looks like traffic to
bare IP addresses. Once Tier 2 is running you can also verify from the device itself, which only Android TV
otherwise allows: PCAPdroid attributes each hostname to the app that asked for it, so you can tell Amazon's
own telemetry apart from a channel's ad SDK.

## Open questions

- **Does Fire OS do content recognition at all?** No toggle, endpoint or cadence is in our corpus. An
  owner with a query log and an HDMI source could settle it.
- **Does PCAPdroid work on Fire OS?** Android TV support declared since 1.3.0, never confirmed on Fire
  hardware. Explicit test item.
- **Does `settings put secure always_on_vpn_app` arm always-on VPN without device-owner privileges?**
  First thing to test on hardware; without always-on the observer misses the boot window.
- **Is `com.android.vpndialogs` present on Fire OS, and does disabling it permanently kill `VpnService`?**
- **Which Fire OS builds silently ignore custom Wi-Fi DNS?** The report exists; the build list does not.
- **Do Sticks really reach 8.8.8.8 regardless of DHCP?** Anecdotal. A LAN capture on port 53 answers it.
- **What is the factory reset menu path on Fire OS?** Needed to finish the Tier 3 recovery path.
- **What happens after `pm disable-user com.amazon.tv.launcher`?** No observation recorded.
- **Do the do-not-disable breakages hold on Fire OS 7.x?** Every documented case is 5.2.6.3 or 5.2.7.2.
- **Where does `kamakiri` live, and is any generation besides `sheldon` and `sheldonp` vulnerable?**
- **Confirm every Tier 0 and Tier 1 menu path on hardware,** naming the model and build. Amazon's help
  page returned 503 and every path here is a secondary source.

## Sources

1. Mandalari et al., *Blocking Without Breaking*, PETS 2021. https://arxiv.org/abs/2105.05162
2. Moghaddam et al., *Watching You Watch*, CCS 2019.
   https://blog.citp.princeton.edu/2019/09/18/watching-you-watch-the-tracking-ecosystem-of-over-the-top-tv-streaming-devices/
3. Varmarken et al., *The TV is Smart and Full of Trackers*, PETS 2020. https://arxiv.org/abs/1911.03447
4. Mazhar and Shafiq, IoTDI 2020. https://arxiv.org/abs/2001.08288
5. HaGeZi DNS blocklists, GPL-3.0. https://github.com/hagezi/dns-blocklists
6. Perflyst PiHoleBlocklist. https://github.com/Perflyst/PiHoleBlocklist
7. aftvnews, manually configuring the IP address or DNS server on a Fire TV.
   https://www.aftvnews.com/how-to-manually-configure-the-ip-address-or-dns-server-on-an-amazon-fire-tv-or-fire-tv-stick/
8. `firestick-loader` debloat script.
   https://github.com/esc0rtd3w/firestick-loader/blob/master/scripts/debloat/bloat-disable-noroot.sh
9. `Fire-Tools` debloat list. https://github.com/mrhaydendp/Fire-Tools/blob/main/Fire-Tools/Debloat.txt
10. Android `VpnService` documentation, quoted above.
11. Blokada issue 134, log from a Sony Android TV. https://github.com/blokadaorg/blokada/issues/134
12. PCAPdroid, package `com.emanuelef.remote_capture`, GPL-3.0.
13. `ezelab/rethink-tv`, an Android TV fork of RethinkDNS. https://github.com/ezelab/rethink-tv, proposed
    upstream as https://github.com/celzero/rethink-app/issues/2664. Talk to that maintainer before writing
    Android code for this project.
14. `sony-google-tv-debloat`. https://github.com/ironshadow786786-boop/sony-google-tv-debloat
15. Amazon Developer Services Agreement. No stable URL recorded; several related content policy pages
    returned 404 during research.
16. OpenWrt, intercept DNS. https://openwrt.org/docs/guide-user/firewall/fw3_configurations/intercept_dns
17. RFC 2132 §3.8, DHCP option 6. https://www.rfc-editor.org/rfc/rfc2132.html
18. RFC 8106, RDNSS option type 25 and DNSSL type 31 in IPv6 Router Advertisements.
19. 37 CFR 201.40(b)(10). https://www.ecfr.gov/current/title-37/section-201.40
20. Anselmi et al., *Watching TV with the Second-Party*, IMC 2024. https://arxiv.org/html/2409.06203v1
