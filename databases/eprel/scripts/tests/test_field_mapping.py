"""Tests for the EPREL field mapping module."""

from field_mapping import (
    SMARTPHONES_FIELD_MAP,
    OPF_FIELDS_NOT_IN_EPREL,
    get_opf_csv_headers,
    map_product_fields,
)


# Sample EPREL API product response (smartphone)
SAMPLE_EPREL_PRODUCT = {
    "supplierOrTrademark": "HMD",
    "modelIdentifier": "TA-1688",
    "eprelRegistrationNumber": 2238053,
    "deviceType": "SMARTPHONE",
    "energyClass": "A",
    "repairabilityClass": "A",
    "repairabilityIndex": 4.01,
    "onMarketStartDate": "2025-06-20",
    "guaranteeDuration": 36,
    "minYearsSoftwareUpdates": 5,
    "ratedBatteryCapacity": 4500,
    "batteryEndurancePerCycle": 2910,
    "batteryEnduranceInCycles": 8,
    "batteryCyclesFromPDF": 800,
    "batteryUserReplaceable": True,
    "chargerRequiredOutputPower": 33,
    "chargerReceptacleType": "USB_C",
    "operatingSystem": "ANDROID",
    "isFoldable": False,
    "ingressProtectionRating": "IP54",
    "ingressProtectionRatingSolid": "DUST_PROTECTED",
    "ingressProtectionRatingWater": "SPLASHING",
    "screenScratchResistance": "MOHS_8",
    "repeatedFreeFallReliabilityClass": "A",
    "fallsWithoutDefect": 270,
    "disassemblyDepthScore": 4.05,
    "fastenersScore": 5.0,
    "toolsScore": 4.0,
    "sparePartScore": "PRIORITY",
    "repairInfoScore": "NO_COST",
    "webLinkRepairInstructions": "https://www.hmd.com/en_int/self-repair",
    "webLinkInfoSparePartsAvailability": "https://www.hmd.com/en_int/self-repair",
}


class TestMapProductFields:
    def test_basic_mapping(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["brands"] == "HMD"
        assert result["manufacturer:reference_number"] == "TA-1688"
        assert result["eprel_id"] == 2238053
        assert result["energy_efficiency_class:eu"] == "A"
        assert result["repairability_class:eu"] == "A"
        assert result["repairability_index:eu"] == 4.01

    def test_release_date_mapped(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["release_date"] == "2025-06-20"

    def test_battery_fields(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["consumer_electronics:battery_capacity:mah"] == 4500
        assert result["battery_autonomy_per_cycle:eu:hours_min"] == 2910
        assert result["battery_lifespan_in_cycles:eu:higher_or_equal_to"] == 800
        assert result["consumer_electronics:battery_user_replaceable"] is True

    def test_os_and_charger(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["consumer_electronics:initial_operating_system"] == "ANDROID"
        assert result["consumer_electronics:charger_receptacle_type"] == "USB_C"
        assert result["consumer_electronics:charger_output_power:w"] == 33

    def test_ip_rating_parsed(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["ingress_protection_rating:ip"] == "IP54"
        assert result["ingress_protection_rating:ip:number"] == 54

    def test_ip_rating_ip68(self):
        product = {"ingressProtectionRating": "IP68",
                    "eprelRegistrationNumber": 1}
        result = map_product_fields(product)
        assert result["ingress_protection_rating:ip:number"] == 68

    def test_repairability_scores(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["repairability_score:eu:disassembly_depth"] == 4.05
        assert result["repairability_score:eu:fasteners"] == 5.0
        assert result["repairability_score:eu:tools"] == 4.0
        assert result["repairability_score:eu:spare_parts"] == "PRIORITY"
        assert result["repairability_score:eu:repair_info"] == "NO_COST"

    def test_repair_urls(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["consumer_electronics:repair_instructions:url"] == (
            "https://www.hmd.com/en_int/self-repair"
        )

    def test_ec_energy_label_url_generated(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert "ec_energy_label:url" in result
        assert "2238053" in result["ec_energy_label:url"]
        assert "smartphonestablets20231669" in result["ec_energy_label:url"]

    def test_ec_energy_label_svg_url_generated(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert "ec_energy_label:svg_url" in result
        assert result["ec_energy_label:svg_url"] == (
            "https://eprel.ec.europa.eu/labels/smartphonestablets20231669/"
            "Label_2238053.svg"
        )

    def test_fall_reliability(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["repeated_free_fall_reliability_class:eu"] == "A"
        assert result["consumer_electronics:falls_without_defect"] == 270

    def test_unknown_fields_prefixed(self):
        product = {
            "eprelRegistrationNumber": 1,
            "unknownField": "some_value",
        }
        result = map_product_fields(product)
        assert result["eprel:unknownField"] == "some_value"

    def test_empty_product(self):
        result = map_product_fields({})
        assert isinstance(result, dict)
        assert "ec_energy_label:url" not in result

    def test_foldable_flag(self):
        result = map_product_fields(SAMPLE_EPREL_PRODUCT)
        assert result["consumer_electronics:is_foldable"] is False

    def test_barcode_gtin_mapped_to_code(self):
        product = {"eprelRegistrationNumber": 1, "gtin": "5449000000996"}
        result = map_product_fields(product)
        assert result["code"] == "5449000000996"

    def test_barcode_ean_mapped_to_code(self):
        product = {"eprelRegistrationNumber": 1, "ean": "4006381333931"}
        result = map_product_fields(product)
        assert result["code"] == "4006381333931"

    def test_empty_barcode_not_set(self):
        product = {"eprelRegistrationNumber": 1, "gtin": ""}
        result = map_product_fields(product)
        assert "code" not in result

    def test_null_barcode_not_set(self):
        product = {"eprelRegistrationNumber": 1, "gtin": None}
        result = map_product_fields(product)
        assert "code" not in result

    def test_supplier_contact_fields(self):
        product = {
            "eprelRegistrationNumber": 1,
            "supplierName": "Acme Corp",
            "supplierAddress": "123 Street, Brussels",
            "supplierEmail": "info@acme.example",
            "supplierWebsite": "https://acme.example",
        }
        result = map_product_fields(product)
        assert result["supplier:name"] == "Acme Corp"
        assert result["supplier:address"] == "123 Street, Brussels"
        assert result["supplier:email"] == "info@acme.example"
        assert result["supplier:website"] == "https://acme.example"


class TestFieldMapCompleteness:
    def test_all_sample_fields_are_mapped(self):
        """Every field in the sample product should have a mapping."""
        for key in SAMPLE_EPREL_PRODUCT:
            assert key in SMARTPHONES_FIELD_MAP, (
                f"EPREL field '{key}' is not in SMARTPHONES_FIELD_MAP"
            )

    def test_no_duplicate_opf_names(self):
        """Each OPF field name should be unique (except 'code' which maps
        multiple barcode field variants)."""
        values = list(SMARTPHONES_FIELD_MAP.values())
        # "code" can appear multiple times (gtin, ean, barcode all -> code)
        non_code = [v for v in values if v != "code"]
        assert len(non_code) == len(set(non_code))


class TestGetOpfCsvHeaders:
    def test_returns_list(self):
        headers = get_opf_csv_headers()
        assert isinstance(headers, list)
        assert len(headers) > 0

    def test_includes_generated_fields(self):
        headers = get_opf_csv_headers()
        assert "ec_energy_label:url" in headers
        assert "ec_energy_label:svg_url" in headers
        assert "ingress_protection_rating:ip:number" in headers

    def test_includes_mapped_fields(self):
        headers = get_opf_csv_headers()
        assert "energy_efficiency_class:eu" in headers
        assert "repairability_class:eu" in headers
        assert "brands" in headers


class TestOPFFieldsNotInEPREL:
    def test_documented_missing_fields(self):
        """Fields listed as not in EPREL should not appear in the mapping."""
        mapped_values = set(SMARTPHONES_FIELD_MAP.values())
        for field in OPF_FIELDS_NOT_IN_EPREL:
            assert field not in mapped_values, (
                f"'{field}' is listed as not in EPREL but exists in mapping"
            )
