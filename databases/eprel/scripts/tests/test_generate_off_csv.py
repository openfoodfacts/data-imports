"""Tests for the OFF core CSV generation module."""

from generate_off_csv import (
    OFF_CORE_HEADERS,
    convert_to_off_row,
    _build_barcode,
    _build_categories,
    _build_labels,
    _build_product_name,
)


SAMPLE_OPF_ROW = {
    "brands": "HMD",
    "manufacturer:reference_number": "TA-1688",
    "eprel_id": "2238053",
    "device_type": "SMARTPHONE",
    "energy_efficiency_class:eu": "A",
    "repairability_class:eu": "A",
    "repairability_index:eu": "4.01",
    "consumer_electronics:battery_capacity:mah": "4500",
    "consumer_electronics:initial_operating_system": "ANDROID",
    "ingress_protection_rating:ip:number": "54",
    "repeated_free_fall_reliability_class:eu": "A",
    "ec_energy_label:url": (
        "https://eprel.ec.europa.eu/screen/product/"
        "smartphonestablets20231669/2238053?navigatingfrom=qr"
    ),
    "ec_energy_label:svg_url": (
        "https://eprel.ec.europa.eu/labels/smartphonestablets20231669/"
        "Label_2238053.svg"
    ),
    "release_date": "2025-06-20",
}


class TestBuildBarcode:
    def test_placeholder_from_eprel_id(self):
        assert _build_barcode({"eprel_id": "2238053"}) == "eprel_2238053"

    def test_real_barcode_if_present(self):
        row = {"eprel_id": "123", "code": "5449000000996"}
        assert _build_barcode(row) == "5449000000996"

    def test_gtin_field(self):
        row = {"eprel_id": "123", "gtin": "5449000000996"}
        assert _build_barcode(row) == "5449000000996"

    def test_empty_eprel_id(self):
        assert _build_barcode({}) == ""


class TestBuildProductName:
    def test_brand_and_model(self):
        assert _build_product_name(SAMPLE_OPF_ROW) == "HMD TA-1688"

    def test_brand_only(self):
        row = {"brands": "Samsung"}
        assert _build_product_name(row) == "Samsung"

    def test_model_only(self):
        row = {"manufacturer:reference_number": "SM-S928B"}
        assert _build_product_name(row) == "SM-S928B"

    def test_empty(self):
        assert _build_product_name({}) == ""


class TestBuildCategories:
    def test_smartphone_android(self):
        result = _build_categories(SAMPLE_OPF_ROW)
        assert "Smartphones" in result
        assert "Android smartphones" in result

    def test_smartphone_ios(self):
        row = {
            "device_type": "SMARTPHONE",
            "consumer_electronics:initial_operating_system": "iOS",
        }
        result = _build_categories(row)
        assert "Smartphones" in result
        assert "iOS smartphones" in result

    def test_empty(self):
        assert _build_categories({}) == "Electronics"


class TestBuildLabels:
    def test_energy_and_repairability(self):
        result = _build_labels(SAMPLE_OPF_ROW)
        assert "eu:energy-labelling" in result
        assert "eu:energy-class-a" in result
        assert "eu:repairability-class-a" in result

    def test_energy_class_b(self):
        row = {"energy_efficiency_class:eu": "B"}
        result = _build_labels(row)
        assert "eu:energy-class-b" in result

    def test_empty(self):
        result = _build_labels({})
        assert result == "eu:energy-labelling"


class TestConvertToOffRow:
    def test_has_all_core_headers(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        for header in OFF_CORE_HEADERS:
            assert header in result

    def test_barcode_is_placeholder(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert result["code"] == "eprel_2238053"

    def test_product_name(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert result["product_name"] == "HMD TA-1688"

    def test_brands(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert result["brands"] == "HMD"

    def test_categories(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert "Smartphones" in result["categories"]

    def test_labels(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert "eu:energy-labelling" in result["labels"]
        assert "eu:energy-class-a" in result["labels"]

    def test_energy_class_preserved(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert result["energy_efficiency_class:eu"] == "A"

    def test_release_date_preserved(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert result["release_date"] == "2025-06-20"

    def test_svg_url_preserved(self):
        result = convert_to_off_row(SAMPLE_OPF_ROW)
        assert "Label_2238053.svg" in result["ec_energy_label:svg_url"]
