---
title: OpenWrt
updated: 2026-09-08
---

# OpenWrt

OpenWrt is the platform where this project can hand you exact commands instead of describing a shape.
The DNS interception recipe below is documented verbatim on the OpenWrt wiki and, per that page, is
identical for both firewall generations, fw3 and fw4. Everything in this file comes from that page or
from [RFC 2132][rfc2132], and nothing in it was reconstructed from memory.

Read [Router enforcement](../router-enforcement.md) first if you have not, because it explains what
each of these steps buys you. This page is the typing.

**Before you start.** Take a configuration backup through LuCI, so you can restore rather than
reverse-engineer if you lock yourself out. Then decide on your resolver's LAN address and write it
down, because you will substitute it into two separate blocks and the documented examples use
different addresses in each.

**Two addresses appear in the sources.** The DHCP example on the wiki uses `192.168.1.2` and the
firewall example uses `192.168.2.2`. They are placeholders from different pages, not two different
machines. Replace both with your own resolver's address, and use the same one in both places.

## Step 1: advertise your resolver with DHCP option 6

**What breaks:** nothing while the resolver is up. If the resolver goes down and it is the only
address you advertise, every device that honours the lease loses name resolution.

This adds `192.168.1.2` to the list of DNS servers handed out on the LAN, commits it, and restarts
dnsmasq so existing clients pick it up on renewal. To undo it, run
`uci del_list dhcp.lan.dhcp_option='6,192.168.1.2'` then the same `uci commit dhcp` and
`service dnsmasq restart`.

```
uci add_list dhcp.lan.dhcp_option='6,192.168.1.2'
uci commit dhcp
service dnsmasq restart
```

Option 6 is defined in [RFC 2132][rfc2132] §3.8. It is advisory. Roughly two-thirds of televisions
ignore it, which is why step 2 exists.

## Step 2: intercept port 53, add the IPv6 twin, reject port 853

**What breaks, before you type anything:**

- Your own troubleshooting. After this, `dig @1.1.1.1` from a LAN host answers from your resolver
  and looks like it came from Cloudflare. Expect to confuse yourself once.
- Any device you deliberately configured for encrypted DNS to an outside provider. Android's Private
  DNS in Automatic mode falls back to plaintext and survives. Set to a specific hostname, it stops
  working and the user sees no network.
- A device that does its own DNSSEC validation and does not trust your resolver's chain.
- Nothing else, in normal operation, provided the self-exclusion in the block below is present.

This one commit creates the IPv4 redirect (`dns_int`), the IPv6 counterpart (`dns_int6`) and the
DNS-over-TLS rejection (`dot_fwd`), then reloads the firewall. To undo it, run
`uci delete firewall.dns_int`, `uci delete firewall.dns_int6`, `uci delete firewall.dot_fwd`, then
`uci commit firewall` and `service firewall restart`. That is the exact inverse and it returns the
router to its previous behaviour.

```
uci set firewall.dns_int="redirect"
uci set firewall.dns_int.name="Intercept-DNS"
uci set firewall.dns_int.family="any"
uci set firewall.dns_int.proto="tcp udp"
uci set firewall.dns_int.src="lan"
uci set firewall.dns_int.src_dport="53"
uci set firewall.dns_int.target="DNAT"
uci set firewall.dns_int.dest_ip="192.168.2.2"
uci set firewall.dns_int.src_ip="!192.168.2.2"
uci set firewall.dns_int6.dest_ip="fd53::53"
uci set firewall.dns_int6.src_ip="!fd53::53"
uci set firewall.dot_fwd.target="REJECT"
uci set firewall.dot_fwd.dest_port="853"
uci commit firewall
service firewall restart
```

**The block above is what our sources record, and it is not complete for two of the three rules.**
The `dns_int` section is fully specified. The `dns_int6` and `dot_fwd` sections show only the lines
that differ from the pattern, so they are missing the section type, `name`, `family`, `proto`, `src`
and `src_dport` that `dns_int` sets. Do not fill those in from guesswork, and do not copy this block
expecting three working rules. Open the [wiki page][owrt] and take the complete sections from there.
We publish the recorded lines rather than a reconstruction, because a half-specified firewall rule
either does nothing or does something you did not intend.

### Callout 1: the `!` is the whole thing

`uci set firewall.dns_int.src_ip="!192.168.2.2"` means "match traffic from anything except the
resolver". Leave it out and your resolver's own upstream queries match the redirect, get sent back to
the resolver, leave again, and match again. That is a redirect loop, and the symptom is that DNS stops
working for the entire network, including the machine you are typing on.

The wiki calls this out and it is still the step people forget. If you skip one line in this document,
do not let it be this one.

Same logic in the IPv6 rule: `src_ip="!fd53::53"` excludes the resolver's own IPv6 address.

### Callout 2: without the IPv6 twin, IPv6 leaks past everything

An IPv4-only redirect is the top silent failure in this project. A device with a working IPv6 address
can receive a resolver through Router Advertisements with no DHCPv6 server involved at all, because
[RFC 8106][rfc8106] defines the RDNSS option as neighbour discovery type 25 and the DNS Search List as
type 31. Your option 6 setting is not consulted, and neither is any IPv4 NAT rule.

That is why `dns_int6` exists, and why `fd53::53` is a unique local address rather than a public one.
It also means your IPv4 test will pass while IPv6 leaks the entire time. Test both.
See [IPv6 leaks](../ipv6-leaks.md).

### Callout 3: REJECT on 853, never DROP

`dot_fwd.target="REJECT"` is deliberate. A rejected connection fails immediately, so the device falls
back to plain DNS on port 53, where `dns_int` catches it and your query log records it. A dropped
connection gives the client nothing to react to, so some firmware retries for minutes and some reads
the timeout as no internet and starts showing connectivity errors.

The same preference applies to answers, not just connections. Configure your resolver to return
NXDOMAIN for blocked names rather than SERVFAIL, for the same reason.

## What OpenWrt cannot do about DNS-over-HTTPS

Nothing on this page touches DoH, which is ordinary HTTPS on port 443. The only handle is an endpoint
blocklist, and the maintained one is HaGeZi's: 3,324 DoH hostnames, 16,372 including VPN and proxy
endpoints, and 1,451 DoH server addresses published specifically for firewall aliases. That is a
maintenance job rather than a fix, and it does not touch a vendor serving its own DoH endpoint from
the same content delivery network as its app store. See
[Router enforcement §4](../router-enforcement.md#4-dns-over-https).

## Filtering on the router itself

If you would rather not run a separate machine, OpenWrt has packages that do the blocking in place.
Four names come up:

| Package | Notes |
| --- | --- |
| `adblock` | The long-standing option |
| `adblock-fast` | A separate package with a different implementation |
| `adguardhome` | Full AdGuard Home on the router, if it fits in your flash and RAM |
| `adblock-lean` | Aimed at low-resource devices |

**Our research notes do not compare these four, so this page does not rank them.** We are not going to
tell you which is faster or which handles large lists better without a source, because the wrong
answer here costs you an afternoon. Read each project's own README, check the flash and RAM figures
against your device, and if you form a view worth writing down, [send it to
us](../../CONTRIBUTING.md) and this table gets a comparison column.

If you pick `adguardhome`, the [AdGuard Home page](../resolvers/adguard-home.md) covers per-client
policy and the query log, and its built-in DHCP server means you can own option 6 from the same
process.

For an encrypted upstream, the package usually named is `https-dns-proxy`, which fronts a DoH provider
with a plain resolver on localhost. **Also not documented in our research notes**, so verify its
current configuration against its own documentation rather than this page. Encrypting your router's
upstream hides your queries from your ISP. It does nothing at all about a television that resolves
around you, so it is a separate improvement rather than part of this job.

## What to feed the blocklist

Use HaGeZi's own tiering advice rather than turning everything on. The Light and Normal tiers
deliberately carry only native trackers that do not break things. Ultimate blocks every one of them
and does break things. The recommendation is Pro, plus the specific device lists for hardware your
household actually owns:

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.{lgwebos|samsung|roku|amazon|apple|xiaomi|huawei|oppo-realme|vivo|tiktok|winoffice}-onlydomains.txt
```

There is no HaGeZi native list for Google or Android TV, Vizio or Hisense. For those, use this
project's generated lists in [`blocklists/`](../../blocklists/), which carry a breakage flag per
entry.

## Verify it, then verify IPv6 separately

The whole point of the interception rule is that a device cannot tell it is being intercepted, which
means you cannot tell either without checking. In increasing rigour:

1. Create a record only your resolver knows, point a laptop at a public resolver, look it up.
2. Query a public resolver from a LAN host and confirm the query lands in your resolver's log.
3. Filter that log to the television's address, not just your laptop's.
4. Packet-capture the LAN side for ports 53, 853 and UDP 443.
5. Packet-capture the WAN side, to catch numeric dials that never appear in a DNS log.
6. Repeat all of it over IPv6.

Commands for each: [Verify it works](../verify-it-works.md).

## Documented sources

- [OpenWrt: intercept DNS, fw3 configurations][owrt]. This is the page the firewall block comes from.
  The wiki states the configuration is identical for fw3 and fw4, so the fw3 URL is the correct one to
  follow on a current release.
- [RFC 2132][rfc2132] §3.8, the DHCP Domain Name Server option.
- [RFC 8106][rfc8106], RDNSS and DNSSL in Router Advertisements.
- [HaGeZi DNS blocklists][hagezi], GPL-3.0.

**There is no `fw4_configurations/intercept_dns` page on the OpenWrt wiki.** It gets cited in forum
posts and it returns nothing. We do not link it, and if you find it linked in one of our guides, that
is a bug worth reporting.

[owrt]: https://openwrt.org/docs/guide-user/firewall/fw3_configurations/intercept_dns
[rfc2132]: https://www.rfc-editor.org/rfc/rfc2132.html
[rfc8106]: https://www.rfc-editor.org/rfc/rfc8106.html
[hagezi]: https://github.com/hagezi/dns-blocklists
