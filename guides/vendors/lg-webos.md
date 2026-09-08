---
title: LG (webOS)
platform: webos
brands: [LG]
generations: "webOS 1.x through webOS 25 (10.0). DNS paths documented for 4.0 and earlier, 4.5, 5.0, and 6.0 and later."
dns_field: static-ip-required
dev_mode: yes
adb: no
package_disable: no
root: patched
max_tier: 4
updated: 2026-09-08
---

# LG (webOS)

webOS is LG's own television platform and no other brand in our source material ships it. Two menu
toggles and one settings command do most of the work available to you, and all three are free. Past
that, LG's set has a single DNS field that only unlocks when you also pin a static IP, and it dials at
least two hardcoded IP addresses that no DNS filter can touch, so the router is where this guide ends
up for anyone who wants the block to hold. Content recognition on webOS is Alphonso, which LG has owned
since 2021, and the 2024 IMC study found that switching it off stopped the traffic to every recognition
domain the researchers had identified.

**Covers:** LG televisions running webOS 1.x through webOS 25 (10.0).
**Also sold as:** nothing. No other brand in our sources ships webOS.
**How far you can get:** Tier 2 for almost everyone, though Tier 1 is where the block holds. Tier 4 is
documented upstream, but as of 24 August 2025 the latest firmware for essentially all webOS 5, 6, 7 and
9 models is patched.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Content recognition (Alphonso, LG-owned since 2021) | `eu-acrX.alphonso.tv` in the EU and UK, `tkacrX.alphonso.tv` in the US, where X rotates | Frames sampled every 10 ms, batched and sent every 15 seconds, peaking every minute | [IMC 2024][imc24] |
| Advertising | `lgads.tv`, roughly 159 `<cc>.lgsmartad.com` hosts and 163 `<cc>-ad-lgsmartad-com.aws-prd.net` mirrors | Not documented | [HaGeZi][hagezi], [Perflyst][perflyst] |
| Home screen and platform telemetry | `cdpbeacon`, `cdpsvc`, `homeprv`, `nudge`, `rdl`, `wiseconfig`, `recommend`, `service` and `ads` under `.lgtvcommon.com`, plus `aic.*` variants | Not documented | [Perflyst][perflyst] |
| Service delivery platform | `nextlgsdp.com` family including `us.`, `ngfts.`, `aic-gfts.`, `rdx2.`; `smartshare.lgtvsdp.com`, `us.rdx2.lgtvsdp.com`, `ibis.lgappstv.com`, `us.ibs.lgappstv.com`, `ad.lgappstv.com`, `tv.wiselg.com`, `lggalleryplus.com` | Not documented | [Perflyst][perflyst] |
| Third-party ad exchanges | `yumenetworks.com`, `smartclip.com`, `lgad.cjpowercast.com.edgesuite.net` | Not documented | [Perflyst][perflyst] |
| IoT and appliance pairing | `*.lgtviot.com`, `*.lgthinq.com` | Not documented | [Perflyst][perflyst] |
| Crash and diagnostic uploads | Spooled locally in `/tmp/rdxd`, `/tmp/uploadd`, `/var/spool/rdxd`, `/var/spool/uploadd/*` before upload | Not documented | [webos-homebrew-channel `startup.sh`][hbc-startup] |
| OTA firmware fallback | `156.147.69.32:8080`, no DNS lookup | Not documented | [Level1Techs wiki][l1t], from a rooted OLED65G5WUA |
| Live telemetry | `54.186.247.229:443`, no DNS lookup | Not documented | [Level1Techs wiki][l1t], from a rooted OLED65G5WUA |
| LAN inventory: device names, MAC addresses, internal IP addresses and signal strengths for phones, PCs, watches, printers, servers and HVAC equipment, plus names and signal strengths of neighbouring Wi-Fi networks | Endpoints not published | Not documented | Gamers Nexus and Level1Techs, September 2026, as reported by [The Verge][verge], [PCMag][pcmag] and [CyberInsider][ci] |
| Microphone audio captured while the screen appeared to be off | Endpoints not published | Not documented | Same |

Firmware shared-object inventories in
[webosbrew/dev-toolbox-cli][devtoolbox] contain `libacrcloud_recognizer.so`,
`libAdvertisementPlugin.so` and `libTVIS.so`, so the engine is ACRCloud and it sits on the filesystem
where a rooted set can reach it. If you want to prove your own model ships it rather than take our
word, [epk2extract][epk2] pulls apart LG firmware images.

### What Gamers Nexus and Level1Techs published in September 2026

Their packet captures from retail LG OLED sets are why this page exists. As reported:

- The television sweeps the local network and records device names, MAC addresses, internal IP
  addresses and signal strengths for phones, PCs, watches, printers, servers and HVAC equipment, plus
  the names and signal strengths of neighbouring Wi-Fi networks.
- Microphones captured usable audio while the screen appeared to be off.
- One G5 kept recording after its network cable was pulled and uploaded the audio once connectivity
  came back.
- Content recognition produced roughly 4 GB of traffic per month and kept running on some sets used as
  plain HDMI displays.

LG had not responded at the time of publication. Reported by [The Verge][verge], [PCMag][pcmag] and
[CyberInsider][ci].

Traffic evidence establishes which hosts a set contacted, how often, and how many bytes moved. It does
not establish what was inside an encrypted payload. "This television contacted an advertising endpoint
1,400 times while idle" is supportable. "This television sent your viewing history to an advertiser" is
not, unless someone has shown the payload. See [LEGAL.md](../../LEGAL.md), where the same line holds
for every page in this repository.

The specific endpoint list from that reporting has not been reproduced in any article we can cite, so
it is not in [`data/endpoints/lg.yml`](../../data/endpoints/lg.yml) yet. What we do have is
[Perflyst][perflyst], which added a section headed `# Gamers Nexus - LG Smart TV spying` containing
`aic.cdpsvc.lgtvcommon.com`, `aic.cdpbeacon.lgtvcommon.com`, `us.nextlgsdp.com`,
`ngfts.nextlgsdp.com`, `aic.rdl.lgtvcommon.com` and `aic-gfts.nextlgsdp.com`.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

Every path below is marked ⚠️ needs-confirmation. They come from LG's own support library or from
webosbrew, and nobody has checked them against real hardware for this repository. If you confirm or
correct one, [tell us](../../.github/ISSUE_TEMPLATE/bug_report.yml) and include your model number and
firmware version.

### Turn off content recognition

Live Plus is the content recognition feature on webOS. Turning it off takes five seconds and it works.
The [IMC 2024][imc24] team measured a complete absence of traffic to every recognition domain they had
identified after opting out, and no new domains appeared.

**What stops working:** not yet documented. See [Open questions](#open-questions).

| Generation | Path | Status |
| --- | --- | --- |
| Current webOS | Settings > All Settings > General > System > Additional Settings > Live Plus | ⚠️ needs-confirmation |

Our source gives this one path and does not break it down by webOS version, so the older menu layouts
are not yet documented. See [Open questions](#open-questions).

### Close the phone-control port

This one needs no developer mode and closes a real attack surface, so do it second. Setting
`allowMobileDeviceAccess` to false disables the SSAP listener on ports 3000 and 3001, which is the
entry point for the whole CVE-2023-63xx chain that Bitdefender documented: CVE-2023-6317
(authorisation bypass), CVE-2023-6318 (privilege escalation to root through the analytics reporting
service), CVE-2023-6319 (command injection in the lyrics library, webOS 4.9.7 to 7.3.1-43) and
CVE-2023-6320 (authenticated command injection in network configuration). Bitdefender counted over
91,000 devices exposing that LAN-intended service to the public internet ([writeup][bitdefender]).

**What stops working:** the SSAP listener is what phone apps use to control the television over your
network, so expect phone-based remote control to stop. Which specific apps break is not documented in
our sources.

```bash
luna-send -f -n 1 'luna://com.webos.settingsservice/setSystemSettings' \
  '{"category":"network","settings":{"allowMobileDeviceAccess":false}}'
```

Documented at [webosbrew's settings notes][wb-settings], which record this as requiring no developer
mode. There is an equivalent toggle in the television's own menus. Our sources do not give its label
or its path, so that is an open question below rather than a table row we made up.

### Turn off ad tracking and personalisation

**What stops working:** not yet documented. See [Open questions](#open-questions).

| Generation | Path | Status |
| --- | --- | --- |
| Current webOS | Settings > All Settings > Support > Privacy & Terms > Advertising, then Limit Ad Tracking | ⚠️ needs-confirmation |
| Older webOS | All Settings > General > Additional Settings > Advertising | ⚠️ needs-confirmation |

### Other settings worth changing

| Setting | Path | What it covers | Status |
| --- | --- | --- | --- |
| User Agreements | Settings > All Settings > Support > Privacy & Terms > User Agreements | Viewing information, voice information, interest-based advertising | ⚠️ needs-confirmation |
| Voice Recognition | Settings > All Settings > General > AI Service > Voice Recognition | Microphone and voice command handling. Expect voice commands to stop once this is off. | ⚠️ needs-confirmation |

Our sources give no menu path for turning off automatic firmware updates or local network access on
webOS. Not yet documented. See [Open questions](#open-questions).

**What this does not fix:** the two hardcoded addresses at the top of this page, `156.147.69.32:8080` and
`54.186.247.229:443`, are dialled without a DNS lookup, so no menu toggle and no DNS filter reaches
them. A [Level1Techs wiki][l1t] page also states that some webOS firmware hardcodes 8.8.8.8, which is
a secondary source we have not confirmed. Separately, [Mazhar and Shafiq][iotdi] found that 68% of
smart televisions in 200-plus homes reached Google Public DNS directly rather than the resolver their
router handed them. Go to Tier 1 and do it at the router.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

webOS has one DNS field, not two, and it is not standalone. Unticking Set Automatically pins a static
IP address at the same time, so you cannot change DNS without also taking over addressing for that
device. Whether the firmware then honours what you typed is unsettled, since a hardcoded 8.8.8.8
fallback has been reported on some builds and never confirmed.

### On the device

| Generation | Path | Status |
| --- | --- | --- |
| webOS 6.0 and later, Wi-Fi | Settings > All Settings > General > Network > Wi-Fi Connection > Advanced Wi-Fi Settings, untick Set Automatically, edit DNS Server | ⚠️ needs-confirmation |
| webOS 6.0 and later, wired | Settings > All Settings > General > Network > Wired Connection > Edit, untick Set Automatically, edit DNS Server | ⚠️ needs-confirmation |
| webOS 5.0 | All Settings > Connection > Network Connection Settings | ⚠️ needs-confirmation |
| webOS 4.5 | All Settings > Connection | ⚠️ needs-confirmation |
| webOS 4.0 and earlier | All Settings > Network | ⚠️ needs-confirmation |

Source: [LG support][lg-dns].

Because unticking Set Automatically also pins the IP, choose an address outside your router's DHCP
pool or reserve it, or you will collide with another device later.

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: hand the set your
resolver over DHCP option 6, redirect outbound port 53 to it with the resolver's own address excluded
from the rule, reject port 853 so DNS-over-TLS cannot slip past, and add the IPv6 twin of every rule.
RFC 8106 lets a Router Advertisement hand a device a resolver with no DHCPv6 involved, which is the most
common silent failure. Two LG-specific reasons not to stop at the on-device field: the reported 8.8.8.8
hardcoding, and the two hardcoded IP addresses below, which need a firewall rule rather than a resolver.

### What to block

The endpoint list lives in [`data/endpoints/lg.yml`](../../data/endpoints/lg.yml) with a breakage flag
per entry, rather than being duplicated here. Two notes on shape:

- `lgsmartad.com` has roughly 159 country-code hosts plus 163 `aws-prd.net` mirrors, so match it with
  the regex `(^|\.)lgsmartad\.com` instead of enumerating hostnames.
- The OTA hosts (`snu`, `su`, `su-ssl` and `nsu` under `.lge.com`) are opt-in. Blocking them stops
  firmware updates, including security fixes, which is why the webOS Homebrew Channel gates update
  blocking behind an explicit setting.

Generated lists: [`blocklists/fightback-tv-lg.txt`](../../blocklists/)

Upstream, [HaGeZi][hagezi] publishes `native.lgwebos` with 341 entries, updated several times daily
under GPL-3.0. It is the most thorough per-vendor list we found.

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.lgwebos-onlydomains.txt
```

HaGeZi's own guidance is to run Pro plus the native lists for hardware you actually own. The Light and
Normal tiers deliberately include only native trackers that do not break things; Ultimate blocks
everything and does break things.

### What never to block

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `ngfts.lge.com` | Content Store thumbnails | [Perflyst][perflyst] |
| `lgtvsdp.com` | Content Store | [Perflyst][perflyst] |
| `lgappstv.com` | Content Store | [Perflyst][perflyst] |
| `us.lgtvsdp.com` | Content Store, per Perflyst issue 117 | [Perflyst][perflyst] |
| `lgsmartweb.com` | Voice search | [Perflyst][perflyst] |

Perflyst is the only list in this space that annotates per-domain breakage. It has also been stale
since 13 July 2023, so treat the annotations as good history rather than current fact.

### Hardcoded addresses

| Address | What it is | Why DNS cannot help |
| --- | --- | --- |
| `156.147.69.32:8080` | OTA firmware fallback | Dialled by IP, so no name is ever resolved and no resolver sees the request. Only a firewall rule reaches it. |
| `54.186.247.229:443` | Live telemetry | Same. |

Both come from the [Level1Techs wiki][l1t], observed on a rooted OLED65G5WUA. If you block these,
block them outbound at the firewall and expect the OTA rule to stop firmware updates.

## Tier 2: developer mode and sideloading

**Time:** 1 hour. **Risk:** low. **Reversible:** yes. **Warranty:** unaffected, this is an official
vendor feature.

Read the expiry trap before you install anything, because the failure mode is LG deleting your work.

> ⚠️ **The expiry trap.** LG's documentation says developer mode enables for a limited time, that you
> check the Remain Session field and press EXTEND, and that **if the session runs out you cannot
> extend it**. It disables after ten reboots while the set is off the network, or after a reboot once
> the session has expired. LG's wording on the consequence: "After Developer Mode is disabled, the
> installed apps that you were using on Developer Mode are uninstalled." The session length is
> **1000 hours** according to [webosbrew][wb-root]. That figure is not corroborated by LG, and LG's
> own documentation gives no number at all.

### Enabling it

Install the Developer Mode app from the Content Store and sign in with an LG account. You get
unsigned IPK installation, SSH on port 9922 as the user `prisoner`, and a key server on port 9991.

Tooling is `@webosose/ares-cli`:

```bash
ares-setup-device -a webos -i "username=prisoner" -i "privatekey=webos_rsa" \
  -i "passphrase=PASSPHRASE" -i "host=TV_IP" -i "port=9922"
ares-package sampleApp
ares-install --device webos com.example.app_1.0.0_all.ipk
ares-launch --device webos com.example.app
```

If you would rather not install LG's SDK, [dev-manager-desktop][devmgr] does the same work through a
GUI and has 2,549 stars.

### What it does not give you

The `prisoner` account is not root. It is jailed and has no PTY, so developer mode is a route to
running your own app on the set, not a route to changing the system. Nothing in Tier 3 is reachable
from here.

### If your set is rooted, or might be

Two rules from webosbrew that catch people out: uninstall the LG Developer Mode app before rebooting
after rooting, and never install it on a rooted television.

## Tier 3: disable preinstalled advertising and metrics apps

Not available on webOS. There is no ADB, no package manager exposed to the user, and developer mode's
`prisoner` account is jailed and not root, so the components in the table at the top of this page
cannot be disabled without root. That capability is Tier 4.

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

Almost certainly not available on your set. As of 24 August 2025, the latest firmware for essentially
all webOS 5, 6, 7 and 9 models is patched, and for 2025 models only factory webOS 10.0 was vulnerable.
Check [cani.rootmy.tv][cani] against your exact model and firmware before reading further. RootMyTV v1
and v2 are both patched and dead.

**What root gets you:** the ability to block on the device rather than at the router, which is the one
thing DNS filtering and menu toggles cannot do. The webOS Homebrew Channel's
[startup script][hbc-startup] already bind-mounts a writable hosts file and appends LG update servers
to it when `webosbrew_block_updates` is set, and it read-only bind-mounts `/tmp/rdxd`, `/tmp/uploadd`,
`/var/spool/rdxd` and `/var/spool/uploadd/*` to neuter crash and diagnostic upload spools. That is
crash telemetry only and does not touch content recognition. Boot hooks run from
`/var/lib/webosbrew/init.d`, which is where a blocking script belongs. Root also puts
`libacrcloud_recognizer.so` and `libAdvertisementPlugin.so` within reach.

Nothing on [repo.webosbrew.org][wb-repo] blocks or reports LG telemetry. All 51 apps were checked. The
closest entries are an app update blocker, YouTube and Twitch ad removal patchers, an OpenVPN client
and a WireGuard client. So the capability is proven and unbuilt, which makes this the clearest open
slot for anyone who wants to write code for the project.

**What it costs you:** the warranty, and possibly the television. The Homebrew Channel writes this to
`/etc/motd` on every boot:

> NEVER EVER OVERWRITE SYSTEM PARTITIONS LIKE KERNEL, ROOTFS, TVSERVICE. Your TV will be bricked,
> guaranteed!

Whether `iptables` is present and reliable across webOS versions is unverified, so even with root the
firewall half of the job may not be available. Bricked-set reports belong with the people who maintain
these exploits, not with us.

**Where to go:** [cani.rootmy.tv][cani] for the compatibility oracle,
[webosbrew.org/rooting][wb-root] for the current tooling, and
[webos-homebrew-channel][hbc] for what runs afterwards.

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Phone-based remote control, once the SSAP listener on 3000 and 3001 is off. Voice commands, if you turn Voice Recognition off. What Live Plus off costs you is not documented. | Set `allowMobileDeviceAccess` back to true, or re-enable each toggle in the same menu. |
| 1 | Over-blocking breaks the Content Store, its thumbnails and voice search. Blocking the OTA hosts stops firmware updates. | Remove the entry from your blocklist and flush the resolver cache. |
| 2 | Nothing while the session lasts. When it lapses, LG uninstalls every app you sideloaded. | Re-enable developer mode and reinstall, subject to the no-extension rule above. |
| 3 | Not available on this platform. | Not applicable. |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is a WAN-side
packet capture, because `156.147.69.32:8080` and `54.186.247.229:443` never appear in a DNS query log
at all. A clean resolver log is not evidence that this set has stopped talking.

Second most useful: start the capture before the television boots. The [IMC 2024][imc24] team note
that most DNS requests fire in the first seconds after activation, so a late start loses the
hostname-to-address mapping for the session. Then confirm that nothing reaches `alphonso.tv` after
Live Plus is off.

## Open questions

Things we do not know about webOS. If you have the hardware, these are what would help.

- **Every menu path on this page.** None has been confirmed on hardware for this repository. Report
  the model number and firmware version with any correction.
- **The developer mode session length.** A much shorter expiry figure circulates in community posts.
  It appears in no LG documentation, so we do not repeat the number. Only the 1000-hour figure is
  corroborated, and only by webosbrew.
- **The UI equivalent of `allowMobileDeviceAccess`.** webosbrew records that a toggle exists. Nobody
  has given us its label or its menu path. Also unclear is how to reach a shell to run `luna-send`
  without developer mode.
- **What Live Plus off actually costs.** No source describes the features you lose.
- **Menu paths for automatic firmware updates and local network access.** Our sources give none for
  webOS, so we cannot say whether either setting exists in the menus.
- **The Gamers Nexus endpoint list.** Not reproduced in any article we can cite. It needs pulling from
  the video directly before it can go into `data/endpoints/lg.yml`.
- **Whether firmware updates silently re-enable content recognition.** Widely repeated, undocumented,
  and measurable. This would be an original contribution: record the toggle state, take an update,
  record it again.
- **Which webOS firmware hardcodes 8.8.8.8.** The [Level1Techs wiki][l1t] states that some does. No
  version list, no capture.
- **Whether `iptables` works on webOS.** Unverified across versions, which decides whether a rooted set
  can enforce anything beyond a hosts file.
- **A claimed LG DNS-over-HTTPS bootstrap IP set.** It circulates on a site whose captures are
  unpublished and whose IP set is just the usual public resolvers. We do not cite it.
- **The Texas complaint.** Texas sued LG among others in December 2025 over content recognition. A
  specific screenshot rate is quoted in coverage; we have not read the complaint PDFs, so we do not
  repeat the figure.

## Sources

1. Anselmi et al., *Watching TV with the Second-Party*, [IMC 2024][imc24]. Data:
   [SafeNetIoT/ACR](https://github.com/SafeNetIoT/ACR), AGPL-3.0
2. Mazhar and Shafiq, [IoTDI 2020][iotdi], §IV-C
3. Gamers Nexus and Level1Techs, September 2026, per [The Verge][verge], [PCMag][pcmag], [CyberInsider][ci]
4. [LG support][lg-dns], manually changing DNS server settings
5. [webosbrew settings notes][wb-settings] for `allowMobileDeviceAccess`
6. [webosbrew rooting][wb-root] for tooling and the 1000-hour figure
7. [webos-homebrew-channel `services/startup.sh`][hbc-startup] for the hosts bind-mount
8. [repo.webosbrew.org][wb-repo], all 51 apps checked
9. [webosbrew/dev-toolbox-cli][devtoolbox] for the shared-object inventories
10. [webosbrew/dev-manager-desktop][devmgr]
11. [cani.rootmy.tv][cani], root compatibility oracle
12. [Bitdefender][bitdefender] on CVE-2023-6317 through CVE-2023-6320
13. [Level1Techs wiki][l1t] for the hardcoded addresses, from a rooted OLED65G5WUA
14. [HaGeZi DNS blocklists][hagezi], GPL-3.0
15. [Perflyst/PiHoleBlocklist][perflyst], MIT, stale since 13 July 2023
16. [epk2extract][epk2] for firmware extraction

[imc24]: https://arxiv.org/html/2409.06203v1
[iotdi]: https://arxiv.org/abs/2001.08288
[verge]: https://www.theverge.com/tech/991190/lg-tv-spying-standby-recording-wi-fi-scanning-gamers-nexus
[pcmag]: https://www.pcmag.com/news/lg-tvs-reportedly-eavesdrop-on-users-even-when-the-screen-is-off
[ci]: https://cyberinsider.com/lg-smart-tvs-found-scanning-home-networks-for-nearby-devices/
[lg-dns]: https://www.lg.com/us/support/help-library/lg-tv-how-to-manually-change-the-dns-server-settings--20150576570174
[wb-settings]: https://github.com/webosbrew/pages/blob/main/content/pages/hacking/settings.md
[wb-root]: https://www.webosbrew.org/rooting/
[wb-repo]: https://repo.webosbrew.org/api/apps.json
[hbc]: https://github.com/webosbrew/webos-homebrew-channel
[hbc-startup]: https://github.com/webosbrew/webos-homebrew-channel/blob/main/services/startup.sh
[devtoolbox]: https://github.com/webosbrew/dev-toolbox-cli
[devmgr]: https://github.com/webosbrew/dev-manager-desktop
[cani]: https://cani.rootmy.tv/
[bitdefender]: https://www.bitdefender.com/en-us/blog/labs/vulnerabilities-identified-in-lg-webos
[l1t]: https://forum.level1techs.com/t/lg-tv-block-mini-how-to/255178
[hagezi]: https://github.com/hagezi/dns-blocklists
[perflyst]: https://github.com/Perflyst/PiHoleBlocklist
[epk2]: https://github.com/throwaway96/epk2extract
