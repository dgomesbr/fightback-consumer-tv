# Find your TV

**Brand does not tell you what the TV runs.** Hisense ships three different platforms. Sharp ships
three. Panasonic's current flagships run Amazon's software. Work out the platform first, then click
once.

Cross-cutting pages, in the order most people need them:

| Page | Read it when |
| --- | --- |
| [Start here](start-here.md) | You read a news story, you have five minutes, you own no hardware |
| [Why do it at the router](why-dns.md) | You want to know why the on-TV setting is not enough |
| [Choose a resolver](choose-a-resolver.md) | You have decided to filter DNS and need to pick the software |
| [IPv6 leaks](ipv6-leaks.md) | Your filter is configured and nothing is being blocked |
| [Verify it works](verify-it-works.md) | You want proof rather than hope |
| [What breaks](what-breaks.md) | Something stopped working, or you want to know what will |

## How to find out what your TV runs

### The two-second checks

The logo on the boot splash and the name on the home screen usually give the platform away. Neither
is a verified test in our source material, so treat them as a hint and confirm with the menu wording
below.

### The menu-wording test

Open the settings menu and look for one of these. The wording is specific to the platform, so a match
is reliable even when the brand on the bezel is not.

| What you see in the menus | Platform | Guide |
| --- | --- | --- |
| "All Settings", plus a "Live Plus" item under General > System > Additional Settings | webOS | [lg-webos](vendors/lg-webos.md) |
| "General & Privacy" (2021 and later) or "General" (2016 to 2020), and Network Status > IP Settings > DNS Setting | Tizen | [samsung-tizen](vendors/samsung-tizen.md) |
| Settings > Privacy > "Smart TV Experience", and no static IP form anywhere in the menus | Roku OS | [roku](vendors/roku.md) |
| Settings > Preferences > Privacy Settings, listing "Device Usage Data" | Fire OS | [amazon-fire-tv](vendors/amazon-fire-tv.md) |
| Settings > Network & Internet > *network* > IP settings > Static, then separate screens labelled `DNS 1:` and `DNS 2:` with the placeholder "Enter a valid IP address or leave empty. Example: 8.8.8.8" | Android TV or Google TV | [google-android-tv](vendors/google-android-tv.md) |
| Menu > Network > Manual Setup, with "Pref DNS Server" and "Alt DNS Server" | SmartCast | [vizio](vendors/vizio.md) |
| Settings > Network > Network Configuration > Advanced Settings > IP Settings, with "DNS Server 1" | VIDAA | [hisense-vidaa](vendors/hisense-vidaa.md) |
| Settings > General > Network > *network* > Configure DNS > Manual | tvOS | [apple-tvos](vendors/apple-tvos.md) |

The Android TV placeholder string is quoted from the AOSP TvSettings source
([`AdvancedWifiOptionsFlow.java` and `res/values/strings.xml`](https://android.googlesource.com/platform/packages/apps/TvSettings/+/refs/heads/main/Settings/)),
so if you see that exact sentence you are on an Android-derived platform.

### If it is a Roku

You can read the model, serial number, device ID, software version, MAC addresses, timezone and
locale from another machine on the LAN. Roku's ECP service answers `GET /query/device-info` on port
8060, and `GET /query/apps` lists the installed channels. That is the fastest way to get the exact
firmware string for a bug report.

The same endpoint is a fingerprinting surface for anything else on your network, so if you never
control the TV from a phone, turn off "Control by mobile apps". From Roku OS 14.1 that gates most
control commands.

### If you want to prove it from the firmware

[epk2extract](https://github.com/throwaway96/epk2extract) unpacks firmware images for LG, Hisense,
Sharp, Philips and Thompson. Combined with the shared-object inventories in
[dev-toolbox-cli](https://github.com/webosbrew/dev-toolbox-cli), that is how you demonstrate a set
ships `libacrcloud_recognizer.so` instead of asserting it. This is contributor territory, not
consumer territory.

## Brand to guide

| Brand | Platform | Guide |
| --- | --- | --- |
| LG | webOS | [lg-webos](vendors/lg-webos.md) |
| Samsung | Tizen | [samsung-tizen](vendors/samsung-tizen.md) |
| Roku players, and Roku TVs from TCL, Hisense, Philips and Sharp | Roku OS | [roku](vendors/roku.md) |
| Amazon Fire TV sticks and cubes, Insignia, Toshiba Fire TV Edition, Panasonic current flagships | Fire OS | [amazon-fire-tv](vendors/amazon-fire-tv.md) |
| Sony Bravia | Google TV or Android TV on all current models | [sony](vendors/sony.md) |
| TCL | Google TV, Roku TV, some EU variants | [tcl](vendors/tcl.md) |
| Hisense | VIDAA, plus Google TV and Roku TV SKUs | [hisense-vidaa](vendors/hisense-vidaa.md) |
| Vizio | SmartCast | [vizio](vendors/vizio.md) |
| Apple TV | tvOS | [apple-tvos](vendors/apple-tvos.md) |
| Nvidia Shield, Chromecast with Google TV, Google TV Streamer | Android TV or Google TV | [google-android-tv](vendors/google-android-tv.md) |
| Philips | Titan OS on many current EU sets, Android TV on others, Saphi on older | [other-brands](vendors/other-brands.md) |
| Panasonic | My Home Screen on older EU sets, Fire TV built in on several current flagships | [other-brands](vendors/other-brands.md) |
| Sharp | Roku TV in the US, Android or Google TV, or Aquos Linux | [other-brands](vendors/other-brands.md) |
| Toshiba | Fire TV Edition in the US, Google TV on newer, VIDAA in some regions | [other-brands](vendors/other-brands.md) |

Sony gets its own page because the highest-value change on a Sony set is removing `tv.samba.ssm`,
Samba TV, which the rest of the Android TV world does not ship. TCL gets one because the same brand
sells Google TV and Roku TV sets that need completely different advice.

## How far you can get, per platform

Read this before you click. The [four tiers](../README.md#the-four-tiers) are settings (0), router DNS
(1), developer mode (2), disabling preinstalled apps (3), and root (4).

| Platform | DNS field on the device | Realistic ceiling | Why it stops there |
| --- | --- | --- | --- |
| webOS | Yes, but unticking Set Automatically pins a static IP too | Tier 2 | Developer mode is official and expires, and you cannot extend an expired session. As of 24 August 2025 the latest firmware for essentially all webOS 5, 6, 7 and 9 models is patched against the public root tools |
| Tizen | Yes, independent of the IP address | Tier 2 on Tizen 5.5 and earlier, Tier 1 from Tizen 6 | Retail sets from Tizen 6 reject the SDK distributor certificate outright. No public root exists for Tizen retail TVs |
| Roku OS | **No, and no static IP form either** | Tier 1, at the router | No ADB, no root, and a sideloaded app cannot see DNS or another app's traffic. Only the privacy toggles and a LAN-side ECP audit are available on the device. Everything else is router and DNS |
| Fire OS | Yes, full static IP required | Tier 3, Tier 4 on the Stick 3rd gen and Lite | ADB package disabling works well. Root needs a MediaTek bootrom exploit, Fire OS below 7.2.7.3, a USB cable and a Linux host |
| Android TV and Google TV | Yes, full static IP required | Tier 3, Tier 4 on the Nvidia Shield | The Shield is LineageOS-supported as `foster` and NVIDIA publishes stock recovery images. OEM TVs have locked bootloaders |
| SmartCast | Yes, full static IP required | Tier 1 | No developer mode, no sideloading, no ADB, no root, no third-party SDK, no homebrew project |
| VIDAA | Yes, full static IP required | Tier 1, plus a browser-based install path | The community install route works by pointing `vidaahub.com` at your own host. The same primitive means any page the TV's browser visits can install an app silently, so do not browse the web on a Hisense TV |
| tvOS | Yes, independent of the IP address | Tier 1 | tvOS 17 added packet tunnel support, but App Store guideline 5.4(a) requires a VPN app come from a VPN provider, which a local-only tool cannot claim. There is no content recognition on tvOS to turn off |
| Chromecast before Google TV | No DNS UI at all, and it hardcodes 8.8.8.8 and 8.8.4.4 | Tier 1, at the router | Router only, with an interception rule rather than a DHCP setting |

On-device DNS capability comes in three shapes. Two platforms let you set DNS without touching the IP
address, tvOS and Tizen. Everything Android-derived, plus webOS, SmartCast, VIDAA, Panasonic, Philips,
Sharp and Toshiba, makes you pin a full static IP to reach the DNS field. Roku OS gives you nothing,
in every version, including Roku TVs.

## Router guides

| Guide | For |
| --- | --- |
| [OpenWrt](routers/openwrt.md) | The interception recipe is documented verbatim on the OpenWrt wiki and is identical for fw3 and fw4 |
| [pfSense and OPNsense](routers/pfsense-opnsense.md) | Three rules, and the order matters |
| [ISP gateway](routers/isp-gateway.md) | Your router will not let you change DNS, so you own DHCP somewhere else instead |

## Resolver guides

| Guide | Pick it when |
| --- | --- |
| [AdGuard Home](resolvers/adguard-home.md) | General recommendation. Per-client tags, REST API, and built-in DHCP so you can own DHCP option 6 without the router |
| [Pi-hole](resolvers/pi-hole.md) | You want the largest community and the most tutorials |
| [Blocky](resolvers/blocky.md) | You want query logs in Postgres, MariaDB or Timescale and Grafana dashboards on day one |
| [NextDNS](resolvers/nextdns.md) | You will not run hardware. Read the warning about the free cap first |

[Choose a resolver](choose-a-resolver.md) compares all of them, including Technitium, Unbound on
OPNsense, ControlD and dnscrypt-proxy.

## Routers we could not verify

During research the documentation for **UniFi**, **GL.iNet**, **Firewalla** and **Asuswrt-Merlin** all
returned 403 or 404, and the Merlin DNSFilter wiki rendered as an empty edit form. We are not
publishing menu paths or recipes for those four, because we have not read a primary source for any of
them. The only thing confirmed about Asuswrt-Merlin's ecosystem is that Diversion is free.

If you own one of these, the concepts in [Why do it at the router](why-dns.md) and
[IPv6 leaks](ipv6-leaks.md) still apply. What is missing is the exact screen. That is a
[guide request](../../../issues/new?template=guide_request.yml), and it is one of the most useful
things you can send us.

## Your platform is not listed

Titan OS, Saphi, Aquos Linux and Panasonic's My Home Screen have no verified path in our notes.
Titan OS in particular is business-gated and we found no consumer developer mode. Router-level
filtering works on all of them, because it does not need the TV's cooperation.

Open a [guide request](../../../issues/new?template=guide_request.yml) with your model number and
firmware version, or read [other-brands](vendors/other-brands.md) first to check we have not covered
it under a different name.
