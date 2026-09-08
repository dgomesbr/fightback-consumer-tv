---
title: Samsung (Tizen)
platform: tizen
brands: [Samsung]
generations: "2016 onward, Tizen 5.5 through Tizen OS 9. DNS paths documented for 2016-2020 and 2021 onward."
dns_field: standalone
dev_mode: yes
adb: no
package_disable: no
root: none
max_tier: 2
updated: 2026-09-08
---

# Samsung (Tizen)

Tizen is Samsung's own television platform and no other brand in our source material ships it. Samsung
is one of only two platforms in this project where DNS is a standalone setting. You can point the
television at your own resolver without pinning a static IP address, without a gateway and without a
subnet mask, which makes Tier 1 a two-minute job here and a fifteen-minute job on most rivals. Above
that the platform closes down fast. Tier 3 does not exist, there is no public root, and Tier 2 is a
dead end on any set newer than roughly Tizen 5.5.

**Covers:** Samsung televisions from 2016 onward, Tizen 5.5 through Tizen OS 9.
**Also sold as:** nothing. No other brand in our sources ships Tizen.
**How far you can get:** Tier 1 for everyone. Tier 2 only on Tizen 5.5 and earlier, and even then it
expires.

Content recognition on Samsung sets is now a legal matter as well as a technical one. Texas sued
Samsung in December 2025 over content recognition, and in March 2026 Samsung settled and agreed to stop
collecting from Texans without explicit informed consent. Turning the setting off is a right somebody
won in court.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Content recognition, built in-house rather than licensed | `acr-us-prd`, `acr-eu-prd`, `acr-au-prd`, `acr-br-prd`, `acr-ca-prd`, `acr-in-prd`, `acr-kr-prd`, `acr-mx-prd`, `acr-nz-prd` under `.samsungcloud.tv`, plus `acr0.samsungcloudsolution.com` | Frames sampled every 500 ms, sent about every minute, peaking every five minutes | [IMC 2024][imc24] |
| Content recognition logging | `log-config.samsungacr.com`, `log-ingestion.samsungacr.com` (US), `log-ingestion-eu.samsungacr.com` (EU and UK), `log-1`, `log-2` and `log-3.samsungacr.com` | Not documented separately | [IMC 2024][imc24] |
| Advertising | `samsungads.com`, `ads.samsungads.com`, `config.samsungads.com`, `samsungtvads.com`, `samsungadhub.com` with `ad.` and `rd.` prefixes, `samsungads.adsmeasurement.com`, `samsungtv-d.openx.net`, `tvx.adgrx.com` | Not documented | [HaGeZi][hagezi], [Perflyst][perflyst] |
| Device telemetry | The `apu`, `bpu`, `cpu`, `dpu`, `kpu`, `upu`, `xpu`, `ypu`, `zpu` `.samsungelectronics.com` cluster, `nmetrics.samsung.com`, `smetrics.samsung.com`, `event-tracking.samsung.com`, `dc.di.atlas.samsung.com`, `dc.di.runestone.samsung.com`, `bigdata.ssp.samsung.com`, `analytics.bigdata.samsung.com`, `devicelog.samsungcloudsolution.net` | Not documented | [HaGeZi][hagezi], [Perflyst][perflyst] |
| Platform services | `samsungcloudsolution.com` and `.net` with many prefixes, `samsungqbe.com`, `samsungyosemite.com`, `internetat.tv`, `pavv.co.kr`, `samsungrm.net` | Not documented | [HaGeZi][hagezi], [Perflyst][perflyst] |
| Third-party marketing stack | 31 `*.demdex.net`, 30 `*.api.useinsider.com`, 15 `*.omtrdc.net`, plus Qualtrics, plus `connecttv.pelmorex.com` for weather app tracking | Not documented | [HaGeZi][hagezi], [Perflyst][perflyst] |

The recognition endpoints diverge by region, and the [IMC 2024][imc24] team measured materially
different behaviour between their UK and US units of the same models. Vendors can ship a
no-recognition configuration when the law requires one, because they already do.

The same study measured what happens when you opt out. Traffic to every recognition domain the
researchers had identified stopped completely, and no new domains appeared. On Samsung, the menus work.

Traffic evidence establishes which hosts a set contacted, how often and how many bytes moved. It does
not establish what was inside an encrypted payload. See [LEGAL.md](../../LEGAL.md).

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

Every path below is marked ⚠️ needs-confirmation. Samsung's own support page gives no path for the
privacy screen at all, so these come from a secondary source and nobody has checked them against real
hardware for this repository. If you confirm or correct one,
[tell us](../../.github/ISSUE_TEMPLATE/bug_report.yml) with your model number and firmware version.

### Turn off content recognition

The switch is called Viewing Information Services. Turn it off first. [IMC 2024][imc24] measured the
recognition traffic stopping entirely afterwards.

**What stops working:** not yet documented. See [Open questions](#open-questions).

| Generation | Path | Status |
| --- | --- | --- |
| 2022 onward | Settings > All Settings > General & Privacy > Terms & Privacy > Privacy Choices, then turn off Viewing Information Services | ⚠️ needs-confirmation |
| Older | Settings > Support > Terms & Privacy > Privacy Choices | ⚠️ needs-confirmation |

### Turn off ad tracking and personalisation

The same Privacy Choices screen holds the rest. The full set of switches recorded by [IMC 2024][imc24]:

| Switch | What it covers | Status |
| --- | --- | --- |
| Interest-Based Advertisements | Ad personalisation | ⚠️ needs-confirmation |
| Customization Service | Not documented in our sources | ⚠️ needs-confirmation |
| Improve personalized ads | Not documented in our sources | ⚠️ needs-confirmation |
| News and special offers | Marketing messages | ⚠️ needs-confirmation |
| Enable Do Not Track | Not documented in our sources | ⚠️ needs-confirmation |

All five sit on the same Privacy Choices screen as Viewing Information Services, so you are already
there. **What stops working:** not documented. See [Open questions](#open-questions).

### Other settings worth changing

| Setting | Where | Status |
| --- | --- | --- |
| Voice Recognition Services | Same Privacy Choices screen. Expect voice commands to stop once this is off. | ⚠️ needs-confirmation |

Our sources record no Tizen setting for local network access, mobile device access or automatic
firmware updates. Not yet documented. See [Open questions](#open-questions).

**What this does not fix:** whether a Samsung set falls back to a hardcoded resolver when you block or
redirect DNS is not established. Our sources record hardcoded resolvers on Chromecast and report them
on Roku and Fire TV, and say nothing either way about Samsung. Treat that as unknown rather than safe.
Separately, [Mazhar and Shafiq][iotdi] found 68% of smart televisions in 200-plus homes reaching Google
Public DNS directly instead of the resolver their router handed them, which is the reason Tier 1 belongs
at the router and not only on the television.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

Samsung and Apple are the only two platforms in this project where the DNS field is decoupled from IP
addressing. You change DNS Setting to Enter manually, type one address, and leave IP Setting on
automatic. No static address, no gateway, no subnet mask, nothing to reserve in your router's DHCP pool
and nothing to collide with later.

### On the device

| Generation | Path | Status |
| --- | --- | --- |
| 2016 to 2020 | Settings > General > Network > Network Status > IP Settings > DNS Setting > Enter manually | ⚠️ needs-confirmation |
| 2021 onward | Settings > General & Privacy > Network > Network Status > IP Settings > DNS Setting | ⚠️ needs-confirmation |

Source: [techjunctions][tj].

Two behaviours to expect. The DNS row stays greyed out until the network status test finishes, so wait
rather than assuming the option is missing. And on Tizen OS 9 there is a reported bug where DNS reverts
to Auto after you leave the IP Settings screen, so go back in and check the value stuck.

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: the on-device
field is easy enough that you should set it, then enforce the same resolver at the router anyway, since
nothing tells you what a firmware update does to that setting. Hand out your resolver over DHCP option
6, redirect outbound port 53 to it with the resolver's own address excluded from the rule, reject port
853 so DNS-over-TLS cannot slip past, and add the IPv6 twin of every rule. RFC 8106 lets a Router
Advertisement hand a device a resolver with no DHCPv6 involved, which is the most common silent
failure.

Prefer NXDOMAIN over SERVFAIL and REJECT over DROP. Some firmware reads a SERVFAIL or a silently
dropped connection as no internet and retries hard.

### What to block

The endpoint list lives in [`data/endpoints/samsung.yml`](../../data/endpoints/samsung.yml) with a
breakage flag per entry, rather than being duplicated here. The recognition hosts are the on-target
ones: `acr-<region>-prd.samsungcloud.tv` and the `samsungacr.com` logging hosts.

Generated lists: [`blocklists/fightback-tv-samsung.txt`](../../blocklists/)

Upstream, [HaGeZi][hagezi] publishes `native.samsung` with 199 entries, updated several times daily
under GPL-3.0:

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.samsung-onlydomains.txt
```

HaGeZi's own guidance is to run Pro plus the native lists for hardware you own. Light and Normal
deliberately include only native trackers that do not break things; Ultimate blocks everything and
does break things.

Do not wildcard `samsungcloudsolution.com` or `samsungcloudsolution.net`. Read the next table first,
because four of the entries in it live under those two names.

### What never to block

This table is longer for Samsung than for any other vendor here. Each entry stops a feature outright
rather than degrading it.

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `time.samsungcloudsolution.com` | Plex, YouTube and Prime Video | [Perflyst][perflyst] |
| `auth.samsungosp.com` | Account authentication | [Perflyst][perflyst] |
| `infolink.pavv.co.kr` | The app store and login | [Perflyst][perflyst] |
| `otnprd8` through `otnprd11.samsungcloudsolution.net` | Software updates | [Perflyst][perflyst] |
| `www.samsungotn.net` | Software updates | [Perflyst][perflyst] |
| `otn.samsungcloudcdn.com` | Software updates | [Perflyst][perflyst] |
| `cdn.samsungcloudsolution.com` | Update checks | [Perflyst][perflyst] |
| `lcprd1.samsungcloudsolution.net` | Smart Hub | [Perflyst][perflyst] |
| `osb-ussvc.samsungqbe.com` | TV Plus | [Perflyst][perflyst] |
| `ns11.whois.co.kr` | Series 7 sets cannot open YouTube | [Perflyst][perflyst] |
| `multiscreen.samsung.com` | Consequence not documented in our sources | [Perflyst][perflyst] |

Perflyst is the only list in this space that annotates per-domain breakage. It has also been stale
since 13 July 2023, so treat the annotations as good history rather than current fact.

### Hardcoded addresses

None known for Samsung. Our sources document hardcoded IP:port dials on LG and hardcoded resolvers on
Chromecast, and record nothing of either kind for Tizen. Nobody has captured a Samsung set's WAN traffic
for this repository, so treat that as unknown rather than clean. It is in Open questions.

## Tier 2: developer mode and sideloading

**Time:** 1 hour. **Risk:** low. **Reversible:** yes. **Warranty:** unaffected, this is an official
vendor feature.

Read this section before you download Tizen Studio, because on most sets sold since about 2020 the
answer at the end of the hour is that it does not work.

> ⚠️ **The hard wall.** Tizen 6 and later retail sets reject SDK-generic distributor certificates
> outright:
>
> ```
> install failed[118, -12] ... Invalid certificate chain with certificate in signature
> ```
>
> Both `tizen-distributor-signer.p12` (expired November 2012) and `tizen-distributor-signer-new.p12`
> (valid to 2032) are rejected. A self-signed setup did work on a 2020 Q70T running Tizen 5.5 with no
> Samsung account and no DUID registration, so the cutoff sits around Tizen 5.5 versus Tizen 6. Error
> 115 instead of 118 means the DUID is wrong.

> ⚠️ **Certificates expire.** Sideloaded certificates expire and community reports describe apps
> vanishing from the Apps row when they do. A specific interval circulates for this; it has no primary
> source, so we do not repeat the number. Expiry is real, the interval is not established.

### Enabling it

Smart Hub > Apps > App Settings, type `12345`, toggle Developer mode on, enter your PC's IP address,
reboot. The television whitelists that address, so developer mode is scoped to one machine.

Tooling is Tizen Studio with the Extension SDK and the Samsung Certificate Extension. Tizen's device
bridge is `sdb` rather than `adb`:

```bash
tizen build-web -- /path/to/Project
tizen package -t wgt -s myCert -- /path/to/Project/.buildResult
sdb connect <TV_IP>
tizen install-permit -t <TV_NAME>
tizen install -n App.wgt -t <TV_NAME>
```

### What a Tizen app cannot do

Traffic monitoring is impossible, and Samsung says so itself. Its Network API reference states that the
API "does not provide traffic monitoring or packet inspection capabilities". No app you sideload will
ever show you what the television is sending. That is what Tier 1 at the router is for.

### What a Tizen app can read

An app can read the network and device configuration, including whether the privacy toggles are on. So
a settings-audit app is possible even though a traffic monitor is not:

| Call | What it returns |
| --- | --- |
| `getDns()`, `getSecondaryDns()` | The resolvers the set is actually using, which is how you catch a Tizen OS 9 DNS revert |
| `getGateway()`, `getIp()`, `getMac()`, `getWiFiSsid()` | Network configuration |
| `ProductInfo.getModel()`, `getFirmware()`, `getDuid()`, `getLocalSet()` | Model, firmware version, device unique ID, locale |
| `AdInfo.getTIFA()` | The advertising identifier |
| `AdInfo.isLATEnabled()` | Whether Limit Ad Tracking is on |

Those calls would settle whether the privacy settings survive a firmware update. An app that records
model, firmware, `isLATEnabled()` and the configured resolvers before an update and again after it
would produce evidence nobody has published.

## Tier 3: disable preinstalled advertising and metrics apps

Not available on Tizen. There is no package manager exposed to the user, no `adb`, and developer mode
only installs your own signed applications alongside Samsung's.

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

There is nothing to publish. No public root exists for Tizen retail televisions.
[samygo.tv][samygo], the long-running Samsung television modding project, fails TLS with an expired
certificate, and its work targeted the pre-Tizen Orsay era rather than anything you can buy now.

**What root gets you:** unknown on this platform, because nobody has it. On webOS, root buys a
writable hosts file and boot hooks, which is what device-level blocking needs. No equivalent exists
here.

**What it costs you:** not applicable.

**Where to go:** nowhere yet. Treat Tizen as unrootable and put your effort into Tier 1. If that
changes, the compatibility question would surface first at [samygo.tv][samygo].

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Voice commands, once Voice Recognition Services is off. What the other five switches cost is not documented. | Turn each switch back on in the same Privacy Choices screen. |
| 1 | Over-blocking breaks Plex, YouTube, Prime Video, Smart Hub, TV Plus, login, the app store and software updates. See the never-block table. | Remove the entry from your blocklist and flush the resolver cache. |
| 2 | Install fails outright on Tizen 6 and later. On older sets, apps vanish from the Apps row when the certificate expires. | Re-sign and reinstall. Turn developer mode off in the same App Settings screen. |
| 3 | Not available on this platform. | Not applicable. |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is confirming
that `acr-<region>-prd.samsungcloud.tv` and the `samsungacr.com` logging hosts stop appearing in your
resolver's query log after you turn Viewing Information Services off. [IMC 2024][imc24] saw those
queries stop completely, so if yours do not, either the toggle did not take or your model behaves
differently and we want the report.

Second: re-open Settings > General & Privacy > Network > Network Status > IP Settings and confirm your
DNS value is still there. The Tizen OS 9 revert bug means a setting you made an hour ago may be back on
Auto. Third: start any capture before the television boots, because the [IMC 2024][imc24] team note
that most DNS requests fire in the first seconds after activation.

## Open questions

Things we do not know about Tizen. If you have the hardware, these are what would help.

- **Every menu path on this page.** Samsung's own support pages give no path for Privacy Choices, so
  all of these come from a secondary source. Report the model number and firmware version with any
  correction.
- **The sideload certificate lifetime.** A specific interval of a few months circulates in community
  posts with no primary source behind it, so we do not repeat the number. Community reports of apps
  disappearing from the Apps row document the expiry itself.
- **Whether a properly registered Samsung certificate installs on retail Tizen 6 and later.** We know
  the SDK-generic distributor certificates are rejected and that error 115 means a wrong DUID. Whether
  a correctly registered DUID plus a Samsung account clears the wall is untested.
- **The exact Tizen version cutoff.** A 2020 Q70T on Tizen 5.5 worked and Tizen 6 sets do not, so the
  boundary is approximate.
- **Whether Samsung sets fall back to a hardcoded resolver** when port 53 is redirected or blocked. No
  source either way. A WAN-side capture on ports 53, 853 and UDP 443 would answer it.
- **Whether firmware updates silently re-enable content recognition.** Widely repeated, undocumented,
  and measurable. `isLATEnabled()` plus `getDns()` from a sideloaded audit app on a Tizen 5.5 set is
  one way to get the before-and-after.
- **What the Customization Service, improve personalized ads and Do Not Track switches actually
  control.** They appear on the same screen in [IMC 2024][imc24]. Their scope is not documented.
- **Whether the Tizen OS 9 DNS revert bug affects all models** or only some. One secondary source.
- **Menu paths for local network access, mobile device access and automatic firmware updates.** Our
  sources give none for Tizen, so we cannot say whether the settings exist.
- **A claimed Samsung DNS-over-HTTPS bootstrap IP set.** It circulates on a site whose captures are
  unpublished and whose IP set is just the usual public resolvers. We do not cite it and neither should
  you.
- **The Texas filings.** Samsung settled with Texas in March 2026 and agreed to stop collecting from
  Texans without explicit informed consent. We have not read the complaint or the settlement document,
  so a specific screenshot rate quoted in coverage is not repeated here, and this page carries no link
  to the primary filings. Finding them is a wanted contribution.

## Sources

1. Anselmi et al., *Watching TV with the Second-Party*, IMC 2024. <https://arxiv.org/html/2409.06203v1>
   Code and data: <https://github.com/SafeNetIoT/ACR> (AGPL-3.0)
2. Mazhar and Shafiq, IoTDI 2020, §IV-C. <https://arxiv.org/abs/2001.08288>
3. techjunctions, Samsung TV DNS settings. <https://techjunctions.com/samsung-tv-dns-settings/>
4. HaGeZi DNS blocklists. <https://github.com/hagezi/dns-blocklists> (GPL-3.0)
5. Perflyst/PiHoleBlocklist. <https://github.com/Perflyst/PiHoleBlocklist> (MIT, stale since
   13 July 2023)
6. Samsung Tizen Network API reference, quoted for the absence of traffic monitoring and packet
   inspection.
7. SamyGO. <https://samygo.tv/> (TLS certificate expired at the time of checking; pre-Tizen Orsay era)
8. Texas v. Samsung, December 2025, and the March 2026 settlement. Primary filings not yet located;
   see Open questions.

[imc24]: https://arxiv.org/html/2409.06203v1
[iotdi]: https://arxiv.org/abs/2001.08288
[tj]: https://techjunctions.com/samsung-tv-dns-settings/
[hagezi]: https://github.com/hagezi/dns-blocklists
[perflyst]: https://github.com/Perflyst/PiHoleBlocklist
[samygo]: https://samygo.tv/
