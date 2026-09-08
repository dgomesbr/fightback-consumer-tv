---
title: Blocky
kind: resolver
hosted: false
per_client_policy: yes
query_log_export: yes
api: yes
updated: 2026-09-08
---

# Blocky

A DNS proxy with blocking, written in Go and shipped as a single binary. Pick it when you want the
query log in a database you can query rather than in a web interface you have to click through.

**Suits:** anyone who already runs Postgres, MariaDB or Grafana, and anyone planning to contribute
reports to this project regularly.
**Does not suit:** a first-time setup. There is no graphical installer and configuration is a YAML
file. [AdGuard Home](adguard-home.md) is the better starting point.

## Why it is here

Every resolver in this section blocks. What separates Blocky is what it does with the record
afterwards. Its own documentation describes logging queries per day and per client to CSV, or to
MySQL, MariaDB, PostgreSQL or Timescale, alongside REST endpoints, Prometheus metrics and prepared
Grafana dashboards.[^1]

That matters for two things this project cares about. Contributing a report becomes a query rather
than a log export. And answering a question like "did this endpoint stop being contacted after I
changed that setting" is a `WHERE` clause instead of scrolling.

It also states that it collects no user data, telemetry or statistics of its own.[^1] Worth noting
in a tool you are installing to stop other software reporting on you.

## What it gives you

| | |
| --- | --- |
| Per-client policy | Yes, by client group. The documentation gives kids and smart home devices as the examples. |
| Blocking by | Allowlists and denylists per group, regular expressions, CNAME inspection, and blocking by IP address |
| Query log | CSV, or directly into MySQL, MariaDB, PostgreSQL or Timescale |
| Metrics | Prometheus, with prepared Grafana dashboards |
| API | REST endpoints, plus a command line client |
| Upstream | DNS-over-HTTPS, DNS-over-TLS, DNS-over-QUIC, and HTTP/3 |
| Deployment | Single Go binary |

## Setting it up

Blocky's own documentation is the reference, and this project does not reproduce configuration it
has not tested. Read [the configuration guide][^1] and come back for the parts specific to
televisions.

What to do once it is answering queries:

1. **Point your devices at it.** Advertise it through DHCP option 6 and redirect outbound port 53
   so the devices that ignore option 6 have no alternative. Both steps are in
   [router enforcement](../router-enforcement.md), and neither is optional if you own hardware that
   hardcodes its own resolver.
2. **Give the television its own client group.** Then you can apply the aggressive tier to the TV
   and leave the rest of the house on the core tier, which is the main reason to run your own
   resolver rather than using a filtered public one.
3. **Add the lists.** Start with our core tier and the specific list for your brand, plus the
   do-not-block allowlist. See [choosing a resolver](../choose-a-resolver.md) for how ours relate to
   HaGeZi's, which cover more domains and which we build on rather than duplicate.

```
https://raw.githubusercontent.com/dgomesbr/fightback-consumer-tv/main/blocklists/domains/fightback-tv-core.txt
https://raw.githubusercontent.com/dgomesbr/fightback-consumer-tv/main/blocklists/allowlist/fightback-tv-do-not-block.txt
```

The allowlist matters as much as the blocklist. Several widely used lists include domains that break
app stores, firmware updates or the programme guide, and loading the allowlist alongside them is the
cheapest protection against that.

## Keep the client address

If you configure the database sink, resist the urge to route queries through a network address
translation rule that rewrites the source. Some router recipes do this, and it makes your resolver
see the router instead of the television. You lose per-device attribution, which is the field that
makes the log worth keeping. The [pfSense and OPNsense guide](../routers/pfsense-opnsense.md)
explains where that happens and how to avoid it.

## Contributing from the database

Once the log is in a database, a report is a query away. The collector reads query logs directly, and
Blocky is not one of its built-in sources yet, so export the hostnames and counts for your
television and feed them in:

```bash
python collector/router/fightback.py \
  --source domains-file --log tv-hostnames.txt \
  --vendor lg --model "LG OLED C3" --platform webos \
  --os-major 8 --region GB --acr optout --scenario idle \
  --preview
```

One hostname per line, an optional count after it. The tool strips identifiers, rounds timestamps to
the hour, and shows you the file before anything is sent.

A native Blocky source for the collector is an open request. If you run Blocky and would like to
write it, [say so](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=feature_request.yml).

## What we have not verified

This page is built from Blocky's own documentation rather than from running it. The feature list is
what the project claims, and the claims are specific enough to be checkable, but nobody here has
confirmed the database sink or the Grafana dashboards on a live installation. If you have, that is a
useful correction.

The exact configuration syntax is deliberately absent for the same reason. Publishing untested
resolver configuration is how people end up with a house that has no working DNS.

## Sources

[^1]: Blocky documentation, <https://0xerr0r.github.io/blocky/latest/>
