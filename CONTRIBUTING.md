# Contributing

You do not need to be a programmer. The most valuable contributions to this project are corrections
from people who own the hardware.

## The fastest way to help

**Tell us when a menu path is wrong.** Vendors move settings between firmware versions and between
regions. A guide that sends someone to a menu that does not exist on their model loses them for good.
If the path in our guide does not match your TV, [open a bug
report](../../issues/new?template=bug_report.yml) with your model number and firmware version, and
what you actually saw. That takes two minutes and fixes the guide for everyone with that model.

**Confirm a path that already works.** Every menu path in our guides is marked either `verified` or
`needs-confirmation`. Turning one into the other is a real contribution. Say which model and firmware
you checked on.

## Ways to contribute, easiest first

### 1. Report what your TV contacts

You need a filtering resolver already running: Pi-hole, AdGuard Home or a NextDNS account. If you do
not have one, [set one up](guides/choose-a-resolver.md) first, since it helps you either way.

```bash
python collector/router/fightback.py --source pihole --device "LG OLED C3" --preview
```

The tool reads your query log, strips everything identifying, and prints the exact file it would
send. Read it. If you are happy, add `--submit` and it opens a pull request.

Nothing leaves your machine until you ask it to. Local-only is the default. See
[PRIVACY.md](PRIVACY.md) for the field-by-field list of what we collect and what we refuse to.

If you would rather not use the command line, use the [device report
form](../../issues/new?template=device_report.yml) instead.

### 2. Add or correct endpoint data

The blocklists are generated. Do not edit files in `blocklists/`, they are overwritten. Edit
`data/endpoints/<vendor>.yml` instead:

```yaml
- domain: acr-eu-prd.samsungcloud.tv
  purpose: acr
  safe_to_block: true
  breaks: null
  source: https://arxiv.org/html/2409.06203v1
  verified: 2026-09-08
```

Every entry needs a `source`. A forum post is an acceptable source if you label it as one. Your own
packet capture is an acceptable source if you say which model and firmware.

**The `breaks` field matters more than the domain.** A blocklist that kills someone's Netflix does
more harm than good. If blocking a domain breaks something, say what and on which model. If you do
not know, put `breaks: unknown` and we will leave it out of the core tier.

### 3. Add or correct a package entry

`data/packages/<platform>.yml` records which preinstalled apps are safe to disable, per model. This
is the part of the project with no good equivalent elsewhere, because the community lists contradict
each other. One TCL toolkit lists `com.google.android.tvrecommendations` as a safe first removal. A
Sony guide lists the same package as causing a boot loop. Both may be right for their hardware.

So every entry is scoped to models it was tested on:

```yaml
- package: tv.samba.ssm
  label: Samba TV
  purpose: acr
  platforms: [google-tv, android-tv]
  tested_on: ["Sony XR-55A80J / Android 10"]
  safe: true
  breaks: null
  source: https://github.com/ironshadow786786-boop/sony-google-tv-debloat
```

Never add a package you have not disabled yourself, or that a linked source does not vouch for on a
named model.

### 4. Write or fix a guide

Guides live in `guides/` as plain Markdown so they read on GitHub and render on the site from the
same file. Vendor pages follow [the template](guides/vendors/_TEMPLATE.md). Do not invent a new
structure, because readers move between brands and relearning the layout each time costs them.

## House rules

**Cite everything non-obvious.** A claim with no source gets removed, however true it sounds. If you
cannot find a source, mark it `UNVERIFIED` and say how you learned it.

**Never publish a step you have not performed.** Especially anything that could brick hardware.

**Do not add exploit code, and do not add root procedures.** Tier 4 explains what root achieves and
links to the upstream project. Reproducing exploit steps here changes what this repository is. See
[LEGAL.md](LEGAL.md).

**Be honest about breakage.** Every instruction states what stops working and how to undo it. A guide
that only lists benefits is not finished.

**No numbers without a source.** We deliberately do not publish three figures that circulate widely
and that nobody has been able to source: the 50-hour webOS developer session, the two-to-three month
Tizen certificate expiry, and the claim that firmware updates silently re-enable content recognition.
If you can source one, that is a great pull request.

## Writing style

Plain language. A reader who has never opened a terminal should be able to follow Tier 0 and Tier 1.

- Say what breaks before you say what to click.
- Use the exact words on the screen, in the order the menus appear.
- Give the model and firmware a path was checked on.
- Prefer a table to a paragraph when comparing options.
- Skip the enthusiasm. Facts and numbers carry it.

## Pull requests

Small and single-purpose. One vendor, one router, one bug.

CI runs on every pull request:

| Check | What fails it |
| --- | --- |
| `validate-reports` | A report that breaks the schema, or contains a MAC address, IP address or unredacted high-entropy hostname |
| `build-blocklists` | Generator output differs from what is committed, or a core-tier list contains a do-not-block domain |
| `link-check` | A dead link in any guide |
| `site` | The Astro build fails |

Run the checks locally first:

```bash
python -m pytest collector/tests
python tools/build_blocklists.py --check
cd site && npm ci && npm run build
```

## Code of conduct

[Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Be decent to people who are new to this. Most of them
arrived here because they read a news story and got worried, not because they enjoy networking.

## Security

Found a vulnerability in a TV? Do not open an issue. Read [SECURITY.md](SECURITY.md).
