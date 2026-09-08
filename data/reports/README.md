# Reports

Crowdsourced device reports land here, one JSON file per report, grouped by vendor.

Nothing is merged without passing `tools/validate_reports.py`, which runs in CI and checks both
the schema and the redaction rules. A report containing an address, a MAC, a serial number or an
unredacted identifier fails the build.

## Contributing one

Read [CONTRIBUTING.md](../../CONTRIBUTING.md). The short version:

```bash
python collector/router/fightback.py \
  --source adguard-file --log /opt/AdGuardHome/data/querylog.json \
  --device 192.168.1.42 --vendor lg --model "LG OLED C3" \
  --platform webos --os-major 8 --region GB --acr optout --preview
```

Nothing is transmitted until you add `--submit`, and the tool prints the exact file first.

## What is published

A row becomes part of the public dataset only once five separate contributors have reported it,
and only when it also spans at least two countries or two firmware versions. Until then it stays
quarantined and only the count is visible. See [PRIVACY.md](../../PRIVACY.md).

## What must never be committed here

Raw query logs. Packet captures. Anything containing an IP address, a MAC address, a serial
number, a network name, or the hostname of another device on your network. CI rejects all of
these, and the collector never produces them.
