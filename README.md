# Fightback: Consumer TV

**Your television is a data business. Here is how to opt out of it.**

Pick your TV, follow the steps, and it stops reporting what you watch. Most people can do the first
tier in five minutes with no hardware and no technical knowledge.

📖 **[Start here](guides/start-here.md)** · 🔍 **[Find your TV](guides/README.md)** ·
📡 **[Why do it at the router](guides/why-dns.md)** · 🤝 **[Help us measure](CONTRIBUTING.md)**

---

## What we know

In September 2026, Gamers Nexus and Level1Techs published packet captures from retail LG OLED
televisions. Their findings, as reported by [The Verge][verge], [PCMag][pcmag] and
[CyberInsider][ci]:

- The TV sweeps the local network and records device names, MAC addresses, internal IP addresses and
  signal strengths for phones, PCs, watches, printers, servers and HVAC equipment, plus the names and
  signal strengths of neighbouring Wi-Fi networks.
- Microphones captured usable audio while the screen appeared to be off.
- One G5 kept recording after its network cable was pulled and uploaded the audio once connectivity
  came back.
- Content recognition produced roughly 4 GB of traffic per month and kept running on some sets used
  as plain HDMI displays.

LG had not responded at the time of publication.

This is an industry pattern, not one company's mistake:

| When | What |
| --- | --- |
| Feb 2017 | The FTC fined Vizio $2.2M for collecting second-by-second viewing data from 11 million televisions, appending age, income, marital status and home value, and selling it. [Press release][ftc] |
| Sep 2024 | An FTC staff report described "vast surveillance" and indefinite retention across nine social media and video streaming firms. [Report][ftc6b] |
| Dec 2025 | Texas sued Samsung, LG, Sony, Hisense and TCL, alleging content recognition captures the screen about twice a second. |
| Mar 2026 | Samsung settled with Texas and agreed to stop collecting from Texans without explicit informed consent. |

A peer-reviewed measurement of 200-plus homes found that **68% of smart TVs bypass the DNS server
your router hands them** and talk to Google's resolver directly ([Mazhar and Shafiq, IoTDI
2020][iotdi]). That single fact is why changing the setting on the TV is not enough, and why this
project spends most of its words on the router.

A 2024 study of Samsung and LG sets found something more hopeful: **turning the setting off actually
works.** After opting out, the researchers saw a complete absence of traffic to every content
recognition domain they had identified, and no new ones appeared ([Anselmi et al., IMC
2024][imc24]). So start with the menus. They are free and they are effective.

## The four tiers

Work down the list. Stop wherever you like. Each tier states what it breaks and how to undo it.

| Tier | What you do | Who it is for | Time |
| --- | --- | --- | --- |
| **0** | Turn off content recognition and ad tracking in the TV's own menus | Everyone | 5 min |
| **1** | Filter DNS for the whole house at the router | Most people | 30 min |
| **2** | Use the vendor's official developer mode to inspect or sideload | Confident readers | 1 hr |
| **3** | Disable the preinstalled advertising and metrics apps | Power users | 1 hr |
| **4** | Root or reflash the TV | Documented, linked upstream, not reproduced here | days |

## Find your TV

| Brand | Platform | On-TV DNS field? | Guide |
| --- | --- | --- | --- |
| LG | webOS | Yes, with static IP | [lg-webos](guides/vendors/lg-webos.md) |
| Samsung | Tizen | Yes, standalone | [samsung-tizen](guides/vendors/samsung-tizen.md) |
| Roku, and Roku TVs from TCL, Hisense, Philips, Sharp | Roku OS | **No. Router only.** | [roku](guides/vendors/roku.md) |
| Amazon, Insignia, Toshiba, Panasonic (newer) | Fire OS | Yes, with static IP | [amazon-fire-tv](guides/vendors/amazon-fire-tv.md) |
| Sony, TCL, Hisense, Philips, Nvidia Shield, Chromecast | Android TV / Google TV | Yes, with static IP | [google-android-tv](guides/vendors/google-android-tv.md) |
| Vizio | SmartCast | Yes, with static IP | [vizio](guides/vendors/vizio.md) |
| Hisense, some Toshiba | VIDAA | Yes, with static IP | [hisense-vidaa](guides/vendors/hisense-vidaa.md) |
| Apple | tvOS | Yes, standalone | [apple-tvos](guides/vendors/apple-tvos.md) |
| Other brands | | | [other-brands](guides/vendors/other-brands.md) |

Not sure which platform you have? [Work it out here](guides/README.md).

## What this project is

Three things:

**Guides.** Per-vendor and per-router instructions, with citations, honest breakage warnings, and a
[verification page](guides/verify-it-works.md) so you can prove the block works instead of hoping.

**Blocklists.** Generated from [`data/endpoints/`](data/endpoints/) in hosts, dnsmasq, AdGuard and
Pi-hole formats. Every entry carries a flag for what it breaks. The core tier does not break your
TV. We build on [HaGeZi's lists][hagezi], which are excellent, rather than duplicating them.

**A dataset.** The [collector](collector/router/) reads the query log you already have from Pi-hole,
AdGuard Home or NextDNS, strips everything identifying, shows you the exact file before it leaves
your machine, and submits it as a pull request. Merged reports regenerate the blocklists and the
per-model pages.

## What this project is not

We record which endpoints a television contacts, and when. Hostnames, ports, protocols, byte counts.
Nothing else.

We do not decrypt traffic. We do not bypass certificate pinning. We do not impersonate vendor
services. We do not modify firmware, and we ship no exploit code. See [LEGAL.md](LEGAL.md) and
[SECURITY.md](SECURITY.md).

We publish observations that at least five separate contributors have seen independently, plus the
derived blocklists. We never publish IP addresses, MAC addresses, serial numbers, network names,
timestamps finer than one hour, or any payload content, because we never collect them. The full
field list is [the schema](data/schema/report.schema.json), versioned in git. See
[PRIVACY.md](PRIVACY.md).

Use it on equipment you are responsible for, on a network you are responsible for, and tell the
people who share it.

## Contributing

Corrections are the most useful thing you can send. If a menu path is wrong on your model, that is a
[bug report](../../issues/new?template=bug_report.yml) and it matters more than a feature.

- 🐞 [Something is wrong](../../issues/new?template=bug_report.yml)
- 📡 [Report what your TV contacts](../../issues/new?template=device_report.yml)
- 📺 [My TV or router is not covered](../../issues/new?template=guide_request.yml)
- 💡 [Feature request](../../issues/new?template=feature_request.yml)

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. You do not need to be a programmer.

## Licences

| What | Licence |
| --- | --- |
| Code, scripts, site | [MIT](LICENSE) |
| Guides and documentation | [CC BY 4.0](LICENSE-CONTENT) |
| Blocklists | [CC0 1.0](LICENSE-DATA) |
| Report corpus | [ODbL 1.0](LICENSE-DATA) plus DBCL 1.0 for contents |

The blocklists are CC0 so anyone can use them, including the resolver projects we build on. The
corpus is ODbL, following [Exodus Privacy's precedent][exodus], so derivatives stay open.

[verge]: https://www.theverge.com/tech/991190/lg-tv-spying-standby-recording-wi-fi-scanning-gamers-nexus
[pcmag]: https://www.pcmag.com/news/lg-tvs-reportedly-eavesdrop-on-users-even-when-the-screen-is-off
[ci]: https://cyberinsider.com/lg-smart-tvs-found-scanning-home-networks-for-nearby-devices/
[ftc]: https://www.ftc.gov/news-events/news/press-releases/2017/02/vizio-pay-22-million-ftc-state-new-jersey-settle-charges-it-collected-viewing-histories-11-million
[ftc6b]: https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-staff-report-finds-large-social-media-video-streaming-companies-have-engaged-vast-surveillance
[iotdi]: https://arxiv.org/abs/2001.08288
[imc24]: https://arxiv.org/html/2409.06203v1
[hagezi]: https://github.com/hagezi/dns-blocklists
[exodus]: https://github.com/Exodus-Privacy/exodus
