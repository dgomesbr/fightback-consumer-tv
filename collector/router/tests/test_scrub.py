"""Tests for the redaction rules.

These are the tests that matter most in the project. A bug here is a privacy incident, not a
defect, so the cases are written as claims about behaviour rather than as coverage.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from collector.router import scrub  # noqa: E402


class TestIdentifierRedaction:
    """A hostname must not be able to carry a household identifier into the dataset."""

    def test_uuid_subdomain_is_redacted(self):
        got = scrub.normalise("3f2504e0-4f89-11d3-9a0c-0305e82c3301.metrics.example.com")
        assert got.fqdn_template == "{id}.metrics.example.com"
        assert got.redacted_label_count == 1
        assert got.leaked_identifier is True

    def test_long_hex_blob_is_redacted(self):
        got = scrub.normalise("a1b2c3d4e5f60718.telemetry.example.net")
        assert got.fqdn_template == "{id}.telemetry.example.net"

    def test_sony_per_device_hex_prefix_is_removed(self):
        """Perflyst records this exact shape on Sony sets, which is why it is a test.

        Note what happens: the identifier is the deepest label, so depth truncation removes
        it before the identifier classifier ever sees it. The requirement is that the hex
        string does not reach the output, not that it becomes {id} specifically.
        """
        host = "ad8641f3cff742de893d919add74c2bb.ssm1.internet.sony.tv"
        got = scrub.normalise(host)
        assert "ad8641f3cff742de893d919add74c2bb" not in got.fqdn_template
        assert got.fqdn_template == "*.ssm{n}.internet.sony.tv"
        assert got.redacted_label_count >= 1
        assert got.registrable_domain == "sony.tv"

    def test_truncation_keeps_the_labels_nearest_the_domain(self):
        """Truncation must discard the most specific labels, not the structural ones.

        Identifiers sit at the left, deepest end of a name. Keeping the two labels closest
        to the registrable domain preserves the vendor's structure and throws away the part
        most likely to be unique to one household.
        """
        got = scrub.normalise("secret.aic.cdpsvc.lgtvcommon.com")
        assert got.fqdn_template == "*.aic.cdpsvc.lgtvcommon.com"
        assert "secret" not in got.fqdn_template

    def test_label_over_twenty_chars_is_redacted(self):
        got = scrub.normalise("thisisaverylonglabelindeed.example.com")
        assert got.fqdn_template == "{id}.example.com"

    def test_many_digits_is_redacted(self):
        got = scrub.normalise("0077777700140002.myhomescreen.tv")
        assert got.fqdn_template == "{id}.myhomescreen.tv"

    @pytest.mark.parametrize(
        "host",
        [
            "5f2b8c1e9a7d4e3f.example.com",
            "aGVsbG93b3JsZDEyMzQ1Njc4.example.com",
            "abcdef0123456789abcdef.example.com",
        ],
    )
    def test_identifier_shapes(self, host):
        assert "{id}" in scrub.normalise(host).fqdn_template


class TestShardNormalisation:
    """A numeric suffix is server structure, not identity, and must survive as {n}.

    This distinction is what let the IMC 2024 authors reason about a vendor's regional server
    layout without publishing anything about a household. Collapsing it to {id} would throw
    away real signal for no privacy gain.
    """

    def test_alphonso_regional_shard(self):
        got = scrub.normalise("eu-acr3.alphonso.tv")
        assert got.fqdn_template == "eu-acr{n}.alphonso.tv"
        assert got.redacted_label_count == 0
        assert got.leaked_identifier is False

    def test_samsung_acr_zero(self):
        assert scrub.normalise("acr0.samsungcloudsolution.com").fqdn_template == (
            "acr{n}.samsungcloudsolution.com"
        )

    def test_samsung_update_host_double_digit(self):
        assert scrub.normalise("otnprd11.samsungcloudsolution.net").fqdn_template == (
            "otnprd{n}.samsungcloudsolution.net"
        )

    def test_sony_ssm_shard(self):
        assert scrub.normalise("ssm2.internet.sony.tv").fqdn_template == "ssm{n}.internet.sony.tv"

    def test_hyphenated_shard_keeps_the_hyphen(self):
        assert scrub.normalise("log-1.samsungacr.com").fqdn_template == "log-{n}.samsungacr.com"


class TestOrdinaryNamesSurvive:
    """Redaction that eats real hostnames would make the dataset useless."""

    @pytest.mark.parametrize(
        "host,expected",
        [
            ("ad.lgsmartad.com", "ad.lgsmartad.com"),
            ("cdpbeacon.lgtvcommon.com", "cdpbeacon.lgtvcommon.com"),
            ("ngfts.lge.com", "ngfts.lge.com"),
            ("time.samsungcloudsolution.com", "time.samsungcloudsolution.com"),
            ("scribe.logs.roku.com", "scribe.logs.roku.com"),
            ("device-metrics-us.amazon.com", "device-metrics-us.amazon.com"),
            ("googleads.g.doubleclick.net", "googleads.g.doubleclick.net"),
            ("tv-analytics-events.apple.com", "tv-analytics-events.apple.com"),
        ],
    )
    def test_known_endpoints_are_unchanged(self, host, expected):
        got = scrub.normalise(host)
        assert got.fqdn_template == expected
        assert got.redacted_label_count == 0


class TestTruncation:
    def test_deep_names_collapse_to_two_labels(self):
        got = scrub.normalise("deep.nested.path.of.labels.example.org")
        assert got.fqdn_template == "*.of.labels.example.org"
        assert got.original_label_count == 7
        # Three labels were discarded: deep, nested and path.
        assert got.redacted_label_count == 3

    def test_two_labels_above_the_domain_are_kept(self):
        got = scrub.normalise("aic.cdpsvc.lgtvcommon.com")
        assert got.fqdn_template == "aic.cdpsvc.lgtvcommon.com"


class TestRegistrableDomain:
    @pytest.mark.parametrize(
        "host,expected",
        [
            ("ad.lgsmartad.com", "lgsmartad.com"),
            ("infolink.pavv.co.kr", "pavv.co.kr"),
            ("something.example.co.uk", "example.co.uk"),
            ("d3p8zr0ffa9t17.cloudfront.net", "d3p8zr0ffa9t17.cloudfront.net"),
            ("mobileanalytics.us-east-1.amazonaws.com", "us-east-1.amazonaws.com"),
            ("eu-acr3.alphonso.tv", "alphonso.tv"),
        ],
    )
    def test_suffix_handling(self, host, expected):
        assert scrub.normalise(host).registrable_domain == expected


class TestRejected:
    """Things that are not vendor endpoints must never enter a report."""

    @pytest.mark.parametrize(
        "value",
        [
            "192.168.1.1",
            "10.0.0.42",
            "2001:db8::1",
            "lg-tv.local",
            "printer.lan",
            "nas.home",
            "1.0.0.127.in-addr.arpa",
            "localhost",
            "",
            "   ",
            "not a hostname",
            "http://example.com/path",
        ],
    )
    def test_rejected(self, value):
        assert scrub.normalise(value) is None

    def test_port_is_stripped(self):
        assert scrub.normalise("example.com:8080").registrable_domain == "example.com"


class TestFreeTextScrubbing:
    def test_removes_addresses_and_identifiers(self):
        text = (
            "My TV at 192.168.1.42 with MAC aa:bb:cc:dd:ee:ff kept calling "
            "home, see http://example.com/x, mail me at a@b.com"
        )
        out = scrub.scrub_text(text)
        assert "192.168.1.42" not in out
        assert "aa:bb:cc:dd:ee:ff" not in out
        assert "a@b.com" not in out
        assert "example.com/x" not in out
        assert "kept calling" in out

    def test_length_is_capped(self):
        assert len(scrub.scrub_text("x" * 5000)) == 280

    def test_detects_identifiers_for_ci(self):
        found = scrub.contains_identifier("client 10.1.2.3 mac de:ad:be:ef:00:01")
        assert "IPv4 address" in found
        assert "MAC address" in found

    def test_clean_text_passes(self):
        assert scrub.contains_identifier("The TV contacted an ad endpoint while idle.") == []


class TestEntropy:
    def test_random_scores_higher_than_words(self):
        assert scrub.shannon_entropy("a1b2c3d4e5f60718") > scrub.shannon_entropy("telemetry")

    def test_empty_is_zero(self):
        assert scrub.shannon_entropy("") == 0.0
