---
title: pfSense and OPNsense
updated: 2026-09-08
---

# pfSense and OPNsense

Both platforms can do everything on the [Router enforcement](../router-enforcement.md) page. Neither
gives us a copy-paste command file, because the work happens in a web interface, so this page describes
rules rather than printing config. That is deliberate: we have a documented prose recipe for pfSense
and we are not going to turn it into invented screenshots or invented field names.

Read [Router enforcement](../router-enforcement.md) first for what each technique buys. Read the
warning under rule 3 below before you build anything, because it is the decision you cannot easily
reverse later.

## pfSense: the three-rule DNS redirect

The recipe is three NAT rules and **the order matters**. It comes from [LabZilla][labzilla].

### Rule 1, at the top: No RDR for the resolver's own queries

Your resolver has to reach its upstream on port 53, and its queries leave through the same interface
the redirect watches. Without an exemption, those queries match the redirect, get sent back to the
resolver, leave again, and match again. The result is a redirect loop, and the symptom is that DNS
stops working for everything on the network at once.

So a No RDR rule for the resolver goes above the redirect. The notes record only that ordering
requirement, so follow it exactly rather than reasoning about it.

**To undo:** disable the rule and apply. Keep it disabled rather than deleted while you are still
testing, because you will want it back.

### Rule 2: the port forward

A port forward on the LAN interface for TCP and UDP 53, with the destination inverted so it excludes
the resolver, redirecting to the resolver. The inverted destination is the same self-exclusion idea as
rule 1 approached from the other side, and both are in the documented recipe.

After this rule is live, a television that has hardcoded `8.8.8.8` gets its answers from your resolver
and cannot tell. So does your laptop, which means `dig @1.1.1.1` now lies to you. Expect that to
confuse you once.

**What breaks:** a device deliberately pointed at an outside encrypted-DNS provider by hostname stops
resolving. A device that validates DNSSEC itself and does not trust your resolver's chain stops
resolving. Everything else keeps working.

**To undo:** disable the port forward and apply. Clients recover on their next query.

### Rule 3: outbound NAT, and the reason to avoid needing it

Read this before you build it.

**Outbound NAT masquerades the source address, so your resolver logs the router instead of the
client.** Every query in the log then appears to come from one address. You lose per-client
attribution completely.

That is not a cosmetic loss:

| What you lose | Why it matters |
| --- | --- |
| Which device asked for a hostname | You cannot tell the television's queries from the games console's, so you cannot tell what the television does |
| Per-client policy | A per-client blocklist needs to know the client, and now every client looks identical |
| The ability to file a report | Our schema requires observations scoped to one `device.model_family`. If every query comes from the router, there is nothing to scope |

If you want to [contribute a device report](../../CONTRIBUTING.md), rule 3 makes that impossible from
your query log. The notes are explicit that you should prefer a topology that does not need it.

Rule 3 exists to fix a return-path problem when the resolver and the client sit on different subnets.
Our notes state the preference without spelling out the alternative, so treat the next sentence as our
reading rather than a sourced instruction: in practice, avoiding rule 3 means putting the resolver on
the same subnet as the clients it serves, so replies find their way back without rewriting.

If you cannot avoid it, you still get the blocking. You just do not get the evidence.

**To undo:** delete the outbound NAT entry and apply. Attribution returns immediately for new queries.
Log records already written stay masqueraded.

### The two rules the recipe does not include

The LabZilla recipe covers plaintext DNS. Two things sit outside it and you have to add them yourself
from your platform's own documentation:

- **A reject rule for TCP 853**, DNS-over-TLS. Use reject, not drop, so the device fails fast and
  falls back to port 53 where the redirect catches it. A dropped connection makes some firmware retry
  for minutes and makes some report no internet.
- **An IPv6 counterpart to the redirect.** [RFC 8106][rfc8106] lets a Router Advertisement hand a
  device a resolver as neighbour discovery option type 25, with no DHCPv6 involved, so an IPv4-only
  redirect leaks IPv6 the whole time it looks like it is working. See [IPv6 leaks](../ipv6-leaks.md).

## OPNsense: Unbound does most of the work

OPNsense ships Unbound with blocklist feeds built in, so for many households the resolver and the
router are the same box and there is nothing to redirect to.

### Built-in blocklist feeds

The bundled feeds include [oisd][oisd] and [HaGeZi][hagezi]. Those are good choices with a known
weakness for this project:

| Feed | Cadence | Strength | Weakness here |
| --- | --- | --- | --- |
| oisd | About hourly | Explicitly prioritises functionality over blocking, so it rarely breaks anything | Weaker on device-native telemetry, which is exactly what a television sends |
| HaGeZi | Several times daily | Best per-vendor work available. `native.lgwebos` 341 entries, `native.amazon` 369, `native.samsung` 199, `native.apple` 108, `native.roku` 72 | No native list for Google or Android TV, Vizio or Hisense |

Turn on oisd as your safe baseline, then add HaGeZi's device list for hardware you actually own.
HaGeZi's own guidance is worth following: the Light and Normal tiers carry only native trackers that do
not break things, Ultimate blocks everything and does break things, and Pro plus your device lists is
the recommendation. For the three vendors HaGeZi does not cover, use this project's generated lists in
[`blocklists/`](../../blocklists/), where every entry carries a flag for what it breaks.

### Per-network policies

Unbound on OPNsense supports multiple policies, so you can apply a harsher list to the network segment
your television lives on than to the one your work laptop lives on. That pairs well with VLAN
isolation, since you are already separating the segments.

### Query logging, and the performance warning that comes with it

Unbound has two settings, Log Queries and Log Replies. You need them for any of this to be
observable, and **OPNsense's own documentation warns that query logging makes the server significantly
slower.** That warning is theirs, not ours.

Consequences worth planning for:

- Turn logging on for a measurement window rather than permanently, unless you have headroom.
- Capture must start before the television boots. The IMC 2024 team found most DNS requests fire in
  the first seconds after activation, so a late start loses the hostname-to-address mapping for the
  whole session.
- If you are building a report, log for a defined scenario, export, then turn logging back down.

**To undo:** turn both settings off. Performance returns immediately. Existing log files stay on disk,
so delete them if you do not want them there.

### NAT redirect on OPNsense

A NAT redirect for port 53 is the recommended way to catch devices that ignore the resolver you
advertise, the same shape as the pfSense recipe above: exclude the resolver, redirect the rest.

**Our notes carry no OPNsense-specific recipe.** The verbatim material we have is the pfSense
three-rule description and the OpenWrt `uci` block. So take the concept from this page and the exact
field labels from OPNsense's own documentation, and keep the self-exclusion, because that is the step
that loops your network if you miss it.

## pfBlockerNG, for the addresses DNS cannot see

DNS filtering never sees a connection that skips the lookup. Two hardcoded LG destinations are on
record from a rooted OLED65G5WUA via the [Level1Techs wiki][l1t]: an OTA fallback at
`156.147.69.32:8080` and live telemetry at `54.186.247.229:443`. Only a firewall rule reaches those.

pfBlockerNG is the pfSense package for IP-level blocking. **Our notes do not record which actions it
supports**, so we are not going to list them, and this is one place where guessing at the difference
between two similarly named actions has real consequences. Read its own documentation.

Two cautions apply whatever tool you use, and they are the reason IP blocking is the last technique
rather than the first:

**Shared addresses.** Telemetry increasingly arrives from the same infrastructure as things you need.
Amazon metrics land on `d3p8zr0ffa9t17.cloudfront.net`, and `amazonadsi-a.akamaihd.net`, which breaks
app installs and updates if blocked, sits on comparable shared hosting. Block a whole ASN and you take
out Netflix, the app store and firmware updates with it.

**No observability.** A blocked DNS query leaves a log line with a hostname in it, so you can find the
entry that broke your Content Store and remove that one entry. A dropped packet to a numeric address
leaves a counter. Six weeks later, when an app stops loading, nothing connects the two.

So reserve IP rules for addresses you have captured yourself on a WAN-side packet capture. The two LG
addresses above exist because someone did exactly that.

## Verify it, including over IPv6

1. Create a record only your resolver knows, point a laptop at a public resolver, look it up.
2. Query a public resolver from a LAN host and confirm the query lands in your log.
3. Filter the log to the television, not just your laptop.
4. Packet-capture the LAN side for ports 53, 853 and UDP 443.
5. Packet-capture the WAN side, for numeric dials.
6. Repeat every step over IPv6.

Commands: [Verify it works](../verify-it-works.md).

If you built rule 3, step 3 is the one that will disappoint you, which is the whole argument for
avoiding it.

## Sources

- [LabZilla, force DNS to Pi-hole][labzilla]. The three-rule pfSense recipe.
- [RFC 8106][rfc8106], RDNSS and DNSSL in Router Advertisements.
- [oisd][oisd] and [HaGeZi][hagezi], the two feed families bundled with Unbound on OPNsense.
- [Level1Techs LG TV block guide][l1t], the source of both hardcoded addresses.

[labzilla]: https://labzilla.io/blog/force-dns-pihole
[rfc8106]: https://www.rfc-editor.org/rfc/rfc8106.html
[oisd]: https://oisd.nl/
[hagezi]: https://github.com/hagezi/dns-blocklists
[l1t]: https://forum.level1techs.com/t/lg-tv-block-mini-how-to/255178
