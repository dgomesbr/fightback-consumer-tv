## What this changes

<!-- One or two sentences. -->

## Type

- [ ] Corrects a menu path or instruction
- [ ] Adds or corrects endpoint data (`data/endpoints/`)
- [ ] Adds or corrects package data (`data/packages/`)
- [ ] New or expanded guide
- [ ] Collector, tooling or site
- [ ] Device report (`data/reports/`)

## Evidence

<!--
Every non-obvious claim needs a source. Vendor docs, an academic paper, an upstream project, or your
own testing. If it is your own testing, say which model and firmware.
-->

| Claim | Source |
| --- | --- |
|  |  |

## If you changed a menu path or an instruction

- **Model tested on:**
- **Firmware version:**
- **Country:**
- [ ] I performed these steps myself on that hardware
- [ ] I marked the path `verified` (only if you tested it) or `needs-confirmation`

## If you changed endpoint or package data

- [ ] Every new entry has a `source`
- [ ] Every new entry has a `breaks` value, including `unknown` where I do not know
- [ ] I have not added a domain that breaks a core device function to the core tier
- [ ] Package entries name the models they were tested on

## What this breaks

<!--
Required for anything touching guides or blocklists. If the answer is genuinely nothing, write
"nothing". If you do not know, write "unknown" and we will keep it out of the core tier.
-->

## Checks

- [ ] `python tools/build_blocklists.py --check` passes
- [ ] `python -m pytest collector/tests` passes, if I touched the collector
- [ ] `cd site && npm run build` passes, if I touched the site
- [ ] I have not added exploit code, root procedures, or anything that bypasses certificate pinning
- [ ] I have not committed a raw log file, packet capture, IP address, MAC address or network name
