---
title: Other brands
platform: other
# A routing page rather than a platform guide. Field values vary by brand and model.
brands: [Philips, Panasonic, Sharp, Toshiba, Xiaomi, game consoles]
generations: "Any television or console not covered by a platform page"
dns_field: varies
dev_mode: varies
adb: varies
package_disable: varies
root: varies
max_tier: varies
updated: 2026-09-08
---

# Other brands

Most television brands are a badge on someone else's operating system. Philips, Panasonic, Sharp,
Toshiba and TCL all ship at least two different platforms depending on the model and the market, and the
guide you need is the one for the operating system, not the one for the logo on the bezel [7]. Find the
operating system first. Everything else follows from that.

This page routes you. It does not follow the tier structure of the platform guides, because the tiers
differ per platform.

## Work out which operating system you have

Three methods, in increasing effort and increasing certainty.

**Settings > About.** The platform name is usually printed there, along with a version number. This is
the method the project's own guide-request form asks people to use [10]. ⚠️ needs-confirmation, since
"Settings > About" is not a vendor-documented path on every brand.

**Watch it boot.** Google TV, Android TV, Roku and Fire TV each show their own splash screen before the
manufacturer's interface appears. ⚠️ needs-confirmation.

**Extract the firmware.** [epk2extract](https://github.com/throwaway96/epk2extract) unpacks firmware
images for LG, Hisense, Sharp, Philips and Thompson [1]. Combined with the shared-object inventories in
[dev-toolbox-cli](https://github.com/webosbrew/dev-toolbox-cli) [2], this is how you prove a set ships a
named content recognition binary such as `libacrcloud_recognizer.so` rather than asserting that it does.
This is analysis on your own computer, it does not modify the television, and it carries none of the risk
of the root tier.

## Brand to platform

| Brand | Platform | Route to |
| --- | --- | --- |
| Sony Bravia | Google TV or Android TV on all current models | [sony](sony.md), which adds the `tv.samba.ssm` removal |
| Philips | Titan OS on many current EU sets, Android TV on others, Saphi on older | Titan OS has no consumer developer mode we could find, **UNVERIFIED** [7]. Android TV models to [google-android-tv](google-android-tv.md) |
| Panasonic | My Home Screen on older EU sets, Amazon Fire TV built in on several current flagships | Fire TV models to [amazon-fire-tv](amazon-fire-tv.md). No known path for My Home Screen [7] |
| Sharp | Roku TV in the US, Android or Google TV, or Aquos Linux | [roku](roku.md) or [google-android-tv](google-android-tv.md). No known path for Aquos Linux [7] |
| Toshiba | Fire TV Edition in the US, Google TV on newer sets, VIDAA in some regions | [amazon-fire-tv](amazon-fire-tv.md), [google-android-tv](google-android-tv.md) or [hisense-vidaa](hisense-vidaa.md) [7] |
| Hisense | VIDAA, plus Google TV and Roku TV models | [hisense-vidaa](hisense-vidaa.md), [google-android-tv](google-android-tv.md) or [roku](roku.md) [7] |
| TCL | Google TV, Roku TV, some EU variants | [tcl](tcl.md), which has the decision table [7] |
| Xiaomi | Android-based. The exact platform per model is not documented | The four tracking hosts below, then check Settings > About and open a [guide request](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=guide_request.yml) |

Every endpoint in the four sections below lives in
[`data/endpoints/other.yml`](../../data/endpoints/other.yml) with a per-entry source, tier and breakage
flag. Almost all of it comes from Perflyst's `SmartTV.txt` [6], which has not been updated since 13 July
2023, so treat the hostnames as a starting point rather than a current inventory.

## Philips

Current EU Philips sets largely run Titan OS, others run Android TV, and older sets run Saphi [7].

Titan OS is business-gated. We found no consumer developer mode for it, and that negative result is
**UNVERIFIED**, meaning we could not confirm the absence rather than confirm it exists [7]. If you have
found a consumer developer path on Titan OS, that is a valuable correction.

Philips is in the group of platforms that expose DNS only as part of a full static IP configuration [7],
so the field exists but pinning it means owning the address for that TV. We have no verified menu path for
it on Titan OS or Saphi, and no privacy menu path on any Philips firmware.

| Domain | What it is | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `ad.nettvservices.com` | Ads | Nothing recorded | [6][9] |
| `legacyportal.nettvservices.com` | Telemetry | Nothing recorded | [6][9] |
| `nettv.corio.com` | Telemetry | Nothing recorded | [6][9] |
| `deviceportal.nettvservices.com` | **Never block** | Applications stop working | [6][9] |
| `epg.corio.com` | **Never block** | The programme guide stops working | [6][9] |
| `ecdinterface.philips.com` | **Never block** | Hue Bridge integration stops working | [6][9] |

Three of the six break something. `nettvservices.com` carries both the ad host and the device portal, so
do not wildcard it.

Some Philips sets get their content recognition from Samba TV through `flingo.tv` [6][9], which is the
same supplier as on Sony and Toshiba. Blocking `*.samba.tv` and `*.flingo.tv` covers all three brands.

Generated list: [`blocklists/fightback-tv-philips.txt`](../../blocklists/)

Android TV Philips models are a different machine. Read [google-android-tv](google-android-tv.md), which
covers DNS, ADB and package disabling.

## Panasonic

Older EU Panasonic sets run My Home Screen. Several current flagships have Amazon Fire TV built in [7].

If yours is a Fire TV model, read [amazon-fire-tv](amazon-fire-tv.md), which is one of the most complete
pages in the project because Fire OS allows package disabling. If yours runs My Home Screen, there is no
known device-side path beyond the settings menu [7]. Panasonic is in the static-IP DNS group, so a DNS
field exists [7], and we have no verified menu path for it.

| Domain | What it is | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `^(collect\|usage)(-(us\|eu)-fy20[0-9]{2})?\.myhomescreen\.tv$` | Telemetry collectors, per fiscal year from fy2014 to fy2022, plus the unsuffixed hosts | Nothing recorded | [6][9] |
| `x2.vindicosuite.com` | Ads | Nothing recorded | [6][9] |
| `mhc-sec-eu.myhomescreen.tv` | Telemetry, consequence unknown, held in the aggressive tier | Unknown | [6][9] |
| `mhc-eu.myhomescreen.tv` | **Never block** | The TV loses internet connectivity | [6][9] |
| `mhc-us.myhomescreen.tv` | **Never block** | The TV loses internet connectivity | [6][9] |
| `vcs.vdspf.com` | **Never block** | The TV is told about new firmware but cannot download it, leaving a permanent update prompt | [6][9] |

**Do not wildcard `myhomescreen.tv`.** Perflyst warns against it explicitly, because the `mhc-` hosts
under that domain carry connectivity and app startup while the `collect-` and `usage-` hosts carry
telemetry [6][9]. Use the regex in the first row instead.

Generated list: [`blocklists/fightback-tv-panasonic.txt`](../../blocklists/)

## Sharp and Toshiba

Both are badge cases, so identify the platform first.

| Brand | If it is | Read |
| --- | --- | --- |
| Sharp | Roku TV, common in the US | [roku](roku.md). No DNS field exists anywhere in Roku OS, so the router is the only option |
| Sharp | Android or Google TV | [google-android-tv](google-android-tv.md) |
| Sharp | Aquos Linux | No known path. Open a guide request |
| Toshiba | Fire TV Edition, common in the US | [amazon-fire-tv](amazon-fire-tv.md) |
| Toshiba | Google TV on newer sets | [google-android-tv](google-android-tv.md) |
| Toshiba | VIDAA in some regions | [hisense-vidaa](hisense-vidaa.md), and read the browser warning at the top of that page |

Both sit in the static-IP DNS group in our notes [7], which tells you a field exists without telling you
where it is.

Toshiba has one hostname of its own, `*.fxmconnect.com`, which carries telemetry and has no recorded
breakage [6][9]. Toshiba's content recognition is Samba TV, the same supplier as on Sony, so `*.samba.tv`
applies here too [6][9]. Generated list:
[`blocklists/fightback-tv-toshiba.txt`](../../blocklists/)

Sharp is the emptiest entry in our data. Perflyst's Sharp section contains two hosts and both are
never-block: `api.accuweather.com`, where blocking it stops the weather widget, and
`time-a.timefreq.bldrdoc.gov`, where blocking it makes the clock drift until certificate validation starts
failing [6][9]. Sharp's own telemetry has not been documented by anyone. If you own an Aquos Linux set,
one query log would be the first data anybody has.

## Xiaomi

Xiaomi televisions are Android-based, and the platform mapping and menu paths are **not yet documented**.
See Open questions. What we do hold is four hostnames.

| Domain | What it is | Source |
| --- | --- | --- |
| `mitv.tracking.intl.miui.com` | Television telemetry | [6][9] |
| `tracking.intl.miui.com` | Telemetry | [8][9] |
| `data.mistat.intl.xiaomi.com` | Telemetry | [8][9] |
| `sdkconfig.ad.intl.xiaomi.com` | Ads | [6][9] |

None has a recorded breakage consequence, and none has been tested on a television by anybody in our
sources. HaGeZi also publishes a `native.xiaomi` device list [3], which is worth adding if you own Xiaomi
phones as well as a Xiaomi TV.

Generated list: [`blocklists/fightback-tv-xiaomi.txt`](../../blocklists/)

If you own a Xiaomi television, Settings > About plus one query log would let us write a full page.

## Entries that apply to any brand

Three cross-vendor entries matter more than any single brand's list [9].

| Domain | What it is | Source |
| --- | --- | --- |
| `*.imrworldwide.com` | Nielsen audience measurement. Appears across many platforms and is safe to block | [6][9] |
| `*.gracenote.com` | **Never block.** Gracenote supplies programme guide data, so blocking it kills the TV guide on many sets. At least one circulating content-recognition blocklist includes it, which will break a reader's television for no benefit | [9] |
| `*.nielsen.com` | **Never block.** Nielsen's corporate website. Blocking it achieves nothing, and its presence in a list suggests that list was built by pattern-matching on company names | [9] |

The `gracenote.com` and `nielsen.com` entries are guards. They exist in our data so that the generator
never emits them, whatever an upstream list says.

Generated list: [`blocklists/fightback-tv-multiple.txt`](../../blocklists/)

## Game consoles

Consoles are in scope for the router work and out of scope for everything else, and the honest reason is
that nobody has done the research.

Two facts we can stand behind:

**Consoles bypass your router's DNS almost as often as televisions do.** In a study of 200-plus homes,
46% of game consoles reached Google Public DNS directly rather than using the resolver they were handed,
against 68% of smart TVs [4]. So the port 53 redirect in
[Router enforcement](../router-enforcement.md) matters here for the same reason it matters for a TV.

**The console filter lists are short.** The only console-specific blocklist we found is
[DandelionSprout's GameConsoleAdblockList](https://github.com/DandelionSprout/adfilt/blob/master/GameConsoleAdblockList.txt),
last updated in 2024, carrying roughly 11 relevant entries [5]. Set that against HaGeZi's device lists
for televisions and streaming hardware, which run to 369 entries for Amazon, 341 for LG, 199 for Samsung,
108 for Apple and 72 for Roku [3]. A short list can mean a console sends less home, or it can mean fewer
people have looked. We do not know which, and the same repository publishes no smart TV list at all [5],
which suggests the second explanation deserves weight.

Where the DNS field is on each console is **not yet documented** in our notes, so we will not print menu
paths. Do the router work and the console's own setting stops mattering.

## What to do regardless of brand

The router is the answer that works on every platform, including the ones with no DNS field and the ones
whose menus we have not mapped. Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md).

Two platforms give you nothing on the device at all. Roku OS has no DNS field and no static IP form in
any version, including Roku TVs. Chromecast before Google TV hardcodes 8.8.8.8 and 8.8.4.4 and has no
DNS interface [7]. For both, a port 53 redirect at the router is the only thing that works.

For a starting blocklist, follow HaGeZi's own guidance. The Light and Normal tiers deliberately carry
only native trackers that do not break things, while Ultimate blocks everything and does break things.
Use Pro plus the specific device lists for the hardware your household actually owns [3][7].

Two more notes before you pick a list. Perflyst's list has been stale since 13 July 2023, and it is
still the only list that annotates what each individual domain breaks, which makes that commentary more
useful than the list itself [6]. And oisd explicitly prioritises functionality over blocking, which
makes it a good safe default and weaker on device-native telemetry [7].

Two resolvers do not solve this problem. Quad9 and Cloudflare for Families block malware, not advertising
or telemetry [7]. And Mullvad DNS is scheduled for discontinuation on 2 November 2026, so do not build
anything on it [7].

## Open questions

Every brand section above has gaps. These are the ones where a single contribution closes a hole. Use the
[device report form](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=device_report.yml)
for captures and the
[guide request form](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=guide_request.yml)
for hardware we do not cover.

- **Menu paths, on every brand on this page.** We have no verified path for DNS, ads or content
  recognition on Titan OS, Saphi, My Home Screen, Aquos Linux or any Xiaomi television. This is the
  largest hole here, and confirming one path takes five minutes with the TV in front of you.
- **Whether the endpoints above are still live.** Nearly all of them come from a list last updated in
  July 2023 [6]. A 2026 query log from a Philips, Panasonic, Toshiba or Xiaomi set would tell us which
  hostnames survived and which are gone.
- **Philips Titan OS developer access.** Our negative finding is unconfirmed [7]. Is there a consumer
  developer mode?
- **Titan OS content recognition.** Nobody has run `epk2extract` against a Titan OS image and looked for
  a recognition binary [1][2]. That is a desk-based contribution needing no special hardware.
- **Sharp's own telemetry.** Perflyst's Sharp section contains two never-block hosts and nothing else
  [6][9]. Nobody has documented what a Sharp actually sends.
- **Panasonic `mhc-sec-eu.myhomescreen.tv`.** Recorded with an unknown consequence [9]. Somebody needs to
  block it and see what stops working.
- **Xiaomi platform mapping.** Which Xiaomi models run which Android variant, and whether the four hosts
  above appear on televisions rather than only on phones.
- **Console DNS fields.** Where the setting is on each current console, and whether the console honours
  it.
- **Console endpoints.** Whether the 11-entry list reflects modest telemetry or modest research effort
  [5].

## Not covered here at all

If your television, streaming box, router or resolver is not on this page or in
[the index](../README.md), ask for it. We would rather write a guide for hardware someone owns than
guess at what is popular.

📺 [My TV or router is not covered](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=guide_request.yml)

Tell us the brand, the model number, the market you bought it in and what Settings > About says. That is
enough to start.

## Sources

1. [epk2extract](https://github.com/throwaway96/epk2extract). Firmware extraction for LG, Hisense, Sharp,
   Philips and Thompson.
2. [webosbrew/dev-toolbox-cli](https://github.com/webosbrew/dev-toolbox-cli). Firmware shared-object
   inventories, including `libacrcloud_recognizer.so`.
3. HaGeZi, [dns-blocklists](https://github.com/hagezi/dns-blocklists). GPL-3.0. Device list entry counts
   and the Light, Normal, Pro, Ultimate tier guidance.
4. Mazhar and Shafiq, IoTDI 2020, [Characterizing Smart Home IoT Traffic in the
   Wild](https://arxiv.org/abs/2001.08288) §IV-C. 46% of game consoles and 68% of smart TVs reached
   Google Public DNS directly.
5. [DandelionSprout GameConsoleAdblockList](https://github.com/DandelionSprout/adfilt/blob/master/GameConsoleAdblockList.txt).
   2024, roughly 11 relevant entries. No smart TV list in that repository.
6. Perflyst, [PiHoleBlocklist SmartTV.txt](https://github.com/Perflyst/PiHoleBlocklist/blob/master/SmartTV.txt).
   MIT, stale since 13 July 2023, and the only list with per-domain breakage annotations. Source of almost
   every hostname on this page, including the warning against wildcarding `myhomescreen.tv`.
7. [Project research notes](../../RESEARCH-NOTES.md), "Which OS is it" table, cross-cutting facts,
   blocklists and resolvers sections, gathered 8 September 2026.
8. NextDNS, [native-tracking-domains, xiaomi](https://github.com/nextdns/native-tracking-domains/blob/main/domains/xiaomi).
9. Project endpoint data, [`data/endpoints/other.yml`](../../data/endpoints/other.yml), where every entry
   carries its own upstream source, tier and breakage flag. The `gracenote.com` and `nielsen.com` guard
   entries come from a circulating content-recognition list, cited in the file.
10. [Project guide-request issue template](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=guide_request.yml),
    which asks readers to check Settings > About.
