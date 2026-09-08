---
title: Router enforcement
updated: 2026-09-08
---

# Router enforcement

Changing the DNS server on the television is the cheap version. It works on a set that honours the
setting, and **68% of smart TVs measured in 200-plus homes ignored the resolver their router handed
them and talked to Google Public DNS directly** ([Mazhar and Shafiq, IoTDI 2020][iotdi] §IV-C, which
also found 46% of games consoles doing the same). Roku has no DNS field at all, and Chromecast before
Google TV hardcodes `8.8.8.8` and `8.8.4.4`.

So the work happens at the router. This page explains what each technique actually buys, in what
order, and what it costs. It contains almost no configuration. Once you know which techniques you
want, go to your platform page:

| Platform | Page |
| --- | --- |
| OpenWrt | [routers/openwrt.md](routers/openwrt.md) |
| pfSense, OPNsense | [routers/pfsense-opnsense.md](routers/pfsense-opnsense.md) |
| A carrier or ISP-supplied box you cannot fully control | [routers/isp-gateway.md](routers/isp-gateway.md) |

You also need somewhere for the queries to go. Pick one first, because every technique below assumes
you have a resolver with a known address: [AdGuard Home](resolvers/adguard-home.md),
[Pi-hole](resolvers/pi-hole.md) or [NextDNS](resolvers/nextdns.md).

## Do the menus first

None of this replaces Tier 0. A 2024 measurement of Samsung and LG sets found that after opting out of
content recognition in the television's own settings, traffic to every recognition domain the
researchers had identified stopped completely, and no new ones appeared ([Anselmi et al., IMC
2024][imc24]). The toggles work, they take five minutes, and they cost nothing.

Router work is what you do because the toggles do not cover everything: advertising identifiers,
platform telemetry, home screen recommendations, third-party trackers inside apps, and the categories
the vendor did not put a switch on. Start at [Find your TV](README.md), then come back.

## The six techniques, by effort

| # | Technique | What it stops | What it does not stop | Effort |
| --- | --- | --- | --- | --- |
| 1 | DHCP option 6 | Devices that ask politely | The 68% that do not ask | 5 min |
| 2 | Redirect outbound TCP/UDP 53 | Hardcoded plaintext resolvers, including `8.8.8.8` | Encrypted DNS, hardcoded IPs | 20 min |
| 3 | Reject TCP 853 | DNS-over-TLS, cleanly | DNS-over-HTTPS | 5 min |
| 4 | Block known DoH endpoints | Public DoH resolvers on a maintained list | A vendor's own DoH on its own CDN address | ongoing |
| 5 | Block UDP 443 | QUIC, forcing TCP fallback | Anything, if the client refuses to fall back | 5 min, with real cost |
| 6 | VLAN isolation | Hardcoded IP dials, LAN reconnaissance, cross-device reach | Nothing the TV sends to the internet | 1-2 hr |

Techniques 1 and 2 belong together. On their own, 1 is advisory and 2 is what makes it binding.

## 1. Advertise your resolver with DHCP option 6

DHCP option 6 is the Domain Name Server option, defined in [RFC 2132][rfc2132] §3.8. Your DHCP server
lists one or more resolver addresses in the lease it hands out, and a well-behaved client uses them.

**What breaks:** nothing, in normal operation. If your resolver goes down and it is the only address
you advertise, every device that honours option 6 loses name resolution and the household reads that
as "the internet is broken". Decide now whether you advertise a second address, and what it is.

**What it buys:** every device that follows the DHCP lease, which is most of your phones and laptops
and roughly a third of your televisions. Do it because it is five minutes, and then do not believe
it is finished.

This is the one command block on this page. On OpenWrt, this adds `192.168.1.2` as the advertised
resolver for the LAN and restarts the DHCP server. To undo it, run
`uci del_list dhcp.lan.dhcp_option='6,192.168.1.2'` followed by the same commit and restart.

```
uci add_list dhcp.lan.dhcp_option='6,192.168.1.2'
uci commit dhcp
service dnsmasq restart
```

Your platform page has the equivalent. Some carrier gateways do not expose option 6 at all, which is
the whole subject of [routers/isp-gateway.md](routers/isp-gateway.md).

## 2. Redirect outbound port 53 to your resolver

A destination NAT rule on the LAN interface rewrites every plaintext DNS query, whatever address the
device chose, so it lands on your resolver instead. A Chromecast asking `8.8.8.8` gets an answer from
your Pi-hole and cannot tell the difference. This is what turns option 6 from a suggestion into a
rule.

**What breaks:** a device that validates DNSSEC itself and does not trust your resolver's chain. A
device pinned to a resolver by IP for licensing reasons, which we have not observed on a television
but is the shape of failure to watch for. And your own troubleshooting, because after this rule
`dig @1.1.1.1` from a LAN host silently answers from your resolver, which confuses everyone at least
once.

Two details cause nearly all the failures.

### The rule must exclude the resolver itself

Your resolver's own upstream queries leave on port 53. If the redirect rule matches them, they get
sent back to the resolver, which sends them out again, which matches the rule again. That is a
redirect loop, and the symptom is that name resolution stops for the entire network.

Every documented recipe handles this by inverting the source. OpenWrt writes it as
`src_ip="!192.168.2.2"`, where `!` means "not from this address". pfSense inverts the destination on
the port forward and puts a No RDR rule above it. Whatever your platform calls it, the rule has to be
there. This is the step people forget.

### It needs an IPv6 twin, or IPv6 walks straight past it

An IPv4-only redirect is the most common silent failure in this whole project. A device with a
working IPv6 address can be handed a resolver over Router Advertisements with no DHCPv6 server
involved at all, because [RFC 8106][rfc8106] defines the RDNSS option as ND type 25 and the DNS
Search List as type 31. Your option 6 setting never enters the picture, and neither does an IPv4 NAT
rule.

So every interception rule gets an IPv6 counterpart. OpenWrt documents `firewall.dns_int6` with
`dest_ip="fd53::53"` and `src_ip="!fd53::53"` for exactly this case. Read
[IPv6 leaks](ipv6-leaks.md) before you decide you are done, and test over IPv6 specifically, because
an IPv4 test will pass while IPv6 leaks the whole time.

Carrier-grade NAT comes up constantly in forum threads about this. It is irrelevant to outbound
interception and it is a red herring.

## 3. Reject DNS-over-TLS on port 853

DNS-over-TLS uses a dedicated port, so it is trivial to spot and trivial to stop. Add a firewall rule
that rejects outbound TCP 853 from the LAN.

**Use REJECT, not DROP.** A rejected connection fails immediately, and the device falls back to plain
DNS on port 53, where your redirect rule catches it and your query log records it. A silently dropped
connection gives the client nothing to react to, so some firmware retries for minutes and some treats
the timeout as "no internet" and starts throwing connectivity errors at the user. The same logic
applies inside your resolver: prefer NXDOMAIN over SERVFAIL for blocked names, because SERVFAIL
triggers the same aggressive-retry behaviour.

**What breaks:** a phone or laptop deliberately configured for encrypted DNS to an outside provider.
Android's Private DNS in Automatic mode fails over to plaintext, so it survives. Android's Private DNS
set to a specific hostname does not, and the user sees no network. If you have set that on a device on
purpose, either exempt the device or accept that you will be changing it back.

## 4. DNS-over-HTTPS

DoH is HTTPS on port 443 to a hostname that resolves to an ordinary web address. There is no port to
close and no field in the packet that says "this is DNS". The only network-layer handle is the
endpoint list.

HaGeZi maintains the usable ones, and the counts show the size of the job:

| List | Entries |
| --- | --- |
| DoH hostnames | 3,324 |
| DoH hostnames including VPN and proxy | 16,372 |
| DoH server IP addresses, for firewall aliases | 1,451 |

Those live in [HaGeZi's repository][hagezi], GPL-3.0, updated several times daily. The same repository
publishes the per-vendor native telemetry lists we recommend elsewhere, at this URL pattern:

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.{lgwebos|samsung|roku|amazon|apple|xiaomi|huawei|oppo-realme|vivo|tiktok|winoffice}-onlydomains.txt
```

Our research notes record the DoH list contents and counts but not the exact file paths for the DoH
lists, so check the repository's own README for those rather than guessing at a URL.

Treat this as blocklist maintenance rather than enforcement. Two limits are worth being blunt about:

**A vendor's own DoH endpoint on its own CDN address cannot be stopped at the network layer.** If a
television ships a resolver pointed at a hostname the vendor controls, hosted on the same content
delivery network as its app store and its firmware updates, then a blocklist entry either misses it
or takes down the app store with it. Separating the two would need TLS interception, and
[TLS interception is out of scope for this project](../LEGAL.md). mitmproxy's own documentation says
pinned applications will not accept its certificates, and the one published baseline found roughly a
third of tested IoT devices interceptable, which is not a methodology you can hand to a reader.

**The problem is getting worse on a schedule.** [RFC 9462][rfc9462] Discovery of Designated Resolvers
lets a client query `_dns.resolver.arpa` and upgrade itself to the network's encrypted resolver with
no user configuration. When televisions implement it, the upgrade happens by default rather than
because a vendor chose it.

## 5. Block QUIC on UDP 443

QUIC carries HTTPS over UDP 443. Blocking that port pushes clients back to TCP, where SNI is visible
to a passive observer and where your other rules behave predictably. It also puts DoH-over-QUIC back
on TCP, where the endpoint blocklist can see it.

**What breaks, and this one is a real cost.** UDP 443 is not a telemetry channel, it is how a large
share of modern HTTPS traffic moves, including YouTube and Google services. Blocking it network-wide
affects every device you own, not just the television. Well-behaved clients fall back to TCP and you
notice nothing except slightly slower connection setup. Clients that assume QUIC works may stall.

**Whether specific TV firmware falls back gracefully is UNVERIFIED.** We have no capture on record
either way. This is a small, cheap, high-value thing to test if you own the hardware: block UDP 443
for the TV's address only, watch what the set does for an evening, and
[tell us](../CONTRIBUTING.md). Scope the rule to one device rather than the whole LAN, both because
that is the honest experiment and because it is the version you can undo in one line.

## 6. VLAN isolation

Everything above is DNS. None of it touches a device that dials a numeric address, and none of it
touches what the television does to your other devices. A separate network segment does.

Three things make this the only real answer for some behaviours:

**Hardcoded addresses.** DNS filtering never sees a connection that skips the lookup. Two are on
record from a rooted LG OLED65G5WUA, via the [Level1Techs wiki][l1t]: an OTA fallback at
`156.147.69.32:8080` and live telemetry at `54.186.247.229:443`. Only a firewall rule reaches those.

**Store-and-forward capture.** A G5 kept recording after its network cable was pulled and uploaded
the audio once connectivity came back ([The Verge][verge]). Blocking a name does nothing to a device
that queues locally and drains the queue later. Cutting the segment's route out does.

**LAN reconnaissance.** The same reporting found the set sweeping the local network and recording
device names, MAC addresses, internal IP addresses and signal strengths for phones, PCs, watches,
printers, servers and HVAC equipment, plus the names and signal strengths of neighbouring Wi-Fi
networks. That is data your firewall rules do not touch and your DNS log does not show. Put the
television where there is nothing to enumerate.

**What breaks:** casting, screen mirroring, phone-as-remote apps, and any smart home integration that
expects the TV and the controller on one subnet. That is not a small list, and for some households it
is the reason not to do this.

### The multicast DNS reflector tradeoff

Casting across a VLAN boundary needs an mDNS reflector, and a reflector partially undoes the
isolation you just built. Given that LG sets enumerate LAN devices, a reflector that republishes your
whole service catalogue hands back the reconnaissance surface the VLAN removed.

Two honest options, and no third:

1. Reflect only the service types you actually need. If you cast from one phone to one TV, reflect
   that and nothing else.
2. Accept the tradeoff explicitly, knowing you have traded LAN visibility for convenience.

What you should not do is enable a blanket reflector, forget you did, and describe your network as
isolated.

### Turn off UPnP while you are in there

UPnP lets a device on your LAN ask the router to open an inbound port for it, with no prompt and no
log entry you are likely to read. A television that can request its own port mapping can make a
LAN-only service reachable from the internet. That is not hypothetical for this hardware: Bitdefender
found over 91,000 devices exposing the webOS SSAP service on ports 3000 and 3001 to the public
internet, and that service is the entry point for the CVE-2023-6317 through CVE-2023-6320
chain ([writeup][bd]). Nothing in this project needs an inbound port, so switch UPnP off.

## IP-level blackholing, and why it is last

Blocking destination addresses at the firewall is the only thing that reaches a hardcoded dial. It is
also the technique most likely to break something in a way you cannot diagnose, so it goes at the end
of the list rather than the start.

**Telemetry now shares addresses with things you need.** Amazon metrics arrive at
`d3p8zr0ffa9t17.cloudfront.net`, and `amazonadsi-a.akamaihd.net`, which breaks app installs and
updates if you block it, sits on comparable shared infrastructure. Block an entire ASN and you take
down Netflix, the app store, and firmware updates along with the telemetry. There is no version of
blanket ASN blocking that only hits the bad traffic.

**IP rules give you no observability.** A DNS block produces a log line with a hostname in it, so you
can see what was blocked and reverse the specific entry that broke your Content Store. A dropped
packet to `203.0.113.10` produces a counter. Six weeks later, when an app stops loading, nothing in
your logs connects the two.

So reserve IP blocking for addresses you have captured yourself. Run a WAN-side packet capture, find
the numeric dials, block those, and write down what you did. The two LG addresses above came from
someone doing exactly that on one rooted set, which is why they are the only two we publish.

## When something breaks, it will be a blocklist entry

Techniques 1, 2, 3 and 6 either work or fail loudly. The thing that breaks a household's television
quietly, a fortnight after you finished, is a blocklist entry that took out a load-bearing hostname.
Three examples, so you know the shape:

| Blocked | What stops working |
| --- | --- |
| `ngfts.lge.com` | LG Content Store thumbnails |
| `time.samsungcloudsolution.com` | Plex, YouTube and Prime Video on a Samsung |
| `mas-ext.amazon.com` | Fire TV app installs |

None of those look like functional hostnames. All three appear in do-not-block tables on the vendor
pages, with sources and consequences, and those tables are the reason this project exists rather than
just pointing at an existing list. Read yours before you enable anything aggressive.

Two habits that make the difference:

- **Add one list at a time and use the television for a day.** A single change is diagnosable. Six
  changes at once means a factory reset.
- **Keep the query log on while you tune.** A blocked hostname in a log is a two-minute fix. The same
  block with no log is a week of guessing, which is the whole argument against IP-level rules above.

## None of this counts until you have proved it

Configuring a rule and confirming a rule are different activities, and the gap between them is where
this whole exercise usually fails. The checks, in increasing rigour:

1. Create a record only your resolver knows about, point a laptop at a public resolver, and look it up.
2. Query a public resolver from a LAN host and confirm the query appears in your resolver's log.
3. Filter that log to the television's address and confirm you see its queries, not just your laptop's.
4. Packet-capture the LAN side for ports 53, 853 and UDP 443.
5. Packet-capture the WAN side, to catch hardcoded-IP dials that never appear in any DNS log.
6. Repeat every one of those over IPv6.

Browser-based DNS leak tests only test the browser, so they tell you nothing about the television.

Full procedure with commands: [Verify it works](verify-it-works.md).

[iotdi]: https://arxiv.org/abs/2001.08288
[imc24]: https://arxiv.org/html/2409.06203v1
[rfc2132]: https://www.rfc-editor.org/rfc/rfc2132.html
[rfc8106]: https://www.rfc-editor.org/rfc/rfc8106.html
[rfc9462]: https://www.rfc-editor.org/rfc/rfc9462.html
[hagezi]: https://github.com/hagezi/dns-blocklists
[l1t]: https://forum.level1techs.com/t/lg-tv-block-mini-how-to/255178
[verge]: https://www.theverge.com/tech/991190/lg-tv-spying-standby-recording-wi-fi-scanning-gamers-nexus
[bd]: https://www.bitdefender.com/en-us/blog/labs/vulnerabilities-identified-in-lg-webos
