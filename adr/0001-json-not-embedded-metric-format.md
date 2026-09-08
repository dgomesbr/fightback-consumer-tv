# 0001. Reports are newline-delimited JSON, not Embedded Metric Format

**Status:** accepted, 2026-09-08

## Context

The original brief asked for reports in AWS CloudWatch Embedded Metric Format, so that submitted
observations could feed dashboards directly.

## Decision

Reports are one JSON object per line, validated against a versioned JSON Schema. The Embedded
Metric Format stays available as an optional projection for our own operational dashboards, using
only bounded dimensions.

## Why

**The cost model is the wrong shape for this data.** The format's own specification warns that
high-cardinality dimensions create one billable custom metric per unique dimension combination.
Domain names are the entire point of this dataset. A modest projection of 20 vendors by 50 model
families by 200 hostnames is 200,000 combinations, which at the published rate of $0.30 per metric
for the first 10,000 and $0.10 thereafter comes to roughly $22,000 per month. That is not an edge
case, it is the core of the product.

**A hostname cannot be a metric.** Metric targets must be numeric or an array of numerics. Our
primary observation is a string, so at best it becomes a dimension, which is the expensive path, or
a property, at which point the format is doing nothing for us.

**Nesting is forbidden.** Target values cannot be nested, and a report is intrinsically nested: a
device object and an observations array. Flattening it to satisfy the format is lossy and hostile
to versioning.

**Delivery is at-least-once with acknowledged duplicates.** Acceptable for operational counters.
Not acceptable for an evidence corpus where "how many households saw this domain" is the headline
number and also the publish gate.

## What we do instead

Newline-delimited JSON on the wire. Per-line validation, so one bad record does not poison a batch.
Streaming server-side validation with bounded memory. Native compatibility with Athena, DuckDB and
Parquet for the published mirror.

The dashboard idea survives. An ingest-side emitter can write one Embedded Metric Format document
per batch rather than per observation, with dimensions limited to schema version and vendor, both
of which are bounded. Hostnames go in properties, never dimensions. Cost stays in the tens of
dollars and we get alarms on rejection rates and schema drift.

## Consequences

We do not get metrics for free from the submission format. We do get a wire format that costs
nothing to accept, is auditable in a pull request diff, and can be published as a dataset without
transformation.
