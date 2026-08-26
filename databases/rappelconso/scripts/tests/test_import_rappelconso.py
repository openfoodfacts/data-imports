"""Tests for the Rappel Conso import module."""

import csv
import io
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from import_rappelconso import (
    OFF_CSV_HEADERS,
    build_off_row,
    check_off_product_exists,
    extract_gtins,
    process_recalls,
    save_csv,
)


# ---------- extract_gtins ----------

class TestExtractGtins:
    def test_single_gtin_in_list(self):
        # Standard food record: [GTIN, lot, date_type, date_start, date_end]
        result = extract_gtins(["3760000000001", "lot123", "dlc", "2025-01-01", ""])
        assert result == ["3760000000001"]

    def test_multiple_gtins_pipe_prefixed(self):
        # Multi-GTIN record: subsequent GTINs are "|GTIN" prefixed
        result = extract_gtins([
            "1111111111111", "tous les lots", "non concerné", "",
            "|2222222222222", "tous les lots", "non concerné", "",
        ])
        assert result == ["1111111111111", "2222222222222"]

    def test_empty_first_gtin_skipped(self):
        # Record with no GTIN (empty string at index 0)
        result = extract_gtins(["", "lot123", "dlc", "2025-01-01", ""])
        assert result == []

    def test_pipe_separator_without_gtin_skipped(self):
        # Multi-group record where groups have no GTIN: "|" standalone
        result = extract_gtins([
            "", "l0237", "date limite de consommation", "2020-11-12",
            "|", "l0240", "date limite de consommation", "2020-11-15",
        ])
        assert result == []

    def test_none_input(self):
        assert extract_gtins(None) == []

    def test_empty_list(self):
        assert extract_gtins([]) == []

    def test_gtin_too_short_skipped(self):
        # Less than 8 digits is not a valid GTIN
        result = extract_gtins(["1234567", "lot", "non concerné", ""])
        assert result == []

    def test_gtin_too_long_skipped(self):
        # More than 14 digits is not a valid GTIN
        result = extract_gtins(["123456789012345", "lot", "non concerné", ""])
        assert result == []

    def test_alphanumeric_lot_not_extracted(self):
        # Lot numbers like "cgr42" or "l0237" are not all-digit, so filtered
        result = extract_gtins(["3440432025078", "cgr42", "dlc", "2026-03-06", ""])
        assert result == ["3440432025078"]

    def test_three_gtins(self):
        result = extract_gtins([
            "3564709006031", "v028", "ddm", "2021-04-04", "",
            "|3250390398028", "v029", "dlc", "2021-04-03", "",
            "|3440432025078", "v030", "dlc", "2026-03-06", "",
        ])
        assert result == ["3564709006031", "3250390398028", "3440432025078"]

    def test_eight_digit_ean8_accepted(self):
        # EAN-8 barcodes have 8 digits
        result = extract_gtins(["12345678", "lot", "non concerné", ""])
        assert result == ["12345678"]


# ---------- build_off_row ----------

SAMPLE_RECORD = {
    "id": 21381,
    "numero_fiche": "2026-02-0250",
    "marque_produit": "TestBrand",
    "modeles_ou_references": "Product X model",
    "libelle": "Product X",
    "identification_produits": [
        "3760000000001", "lot42", "date limite de consommation", "2025-01-01", ""
    ],
    "categorie_produit": "alimentation",
    "sous_categorie_produit": "Biscuits et gateaux",
    "date_publication": "2024-11-29",
    "lien_vers_la_fiche_rappel": "https://rappel.conso.gouv.fr/fiche-rappel/21381/interne",
}


class TestBuildOffRow:
    def test_basic_row_fields(self):
        row = build_off_row(SAMPLE_RECORD, "3760000000001")
        assert row["code"] == "3760000000001"
        assert row["brands"] == "TestBrand"
        assert row["product_name"] == "Product X"
        assert row["categories"] == "Biscuits et gateaux"
        assert row["countries"] == "France"
        assert row["source"] == "Rappel Conso"
        assert row["rappelconso:fiche_id"] == "21381"
        assert row["rappelconso:lien_fiche"] == (
            "https://rappel.conso.gouv.fr/fiche-rappel/21381/interne"
        )

    def test_recall_data_excluded(self):
        """Recall-specific fields should not appear in the OFF row."""
        row = build_off_row(SAMPLE_RECORD, "3760000000001")
        assert "motif_rappel" not in row
        assert "date_publication" not in row

    def test_libelle_preferred_over_modeles(self):
        """libelle is used as product_name before modeles_ou_references."""
        record = {
            "marque_produit": "Brand",
            "libelle": "Clean Title",
            "modeles_ou_references": "Long technical reference",
        }
        row = build_off_row(record, "123")
        assert row["product_name"] == "Clean Title"

    def test_fallback_to_modeles_when_no_libelle(self):
        record = {
            "marque_produit": "Brand",
            "libelle": "",
            "modeles_ou_references": "Reference Name",
        }
        row = build_off_row(record, "123")
        assert row["product_name"] == "Reference Name"

    def test_fallback_to_brand_when_no_name_fields(self):
        record = {
            "marque_produit": "OnlyBrand",
            "libelle": "",
            "modeles_ou_references": "",
        }
        row = build_off_row(record, "123")
        assert row["product_name"] == "OnlyBrand"

    def test_fallback_category_to_parent(self):
        record = {
            "marque_produit": "Brand",
            "libelle": "Prod",
            "sous_categorie_produit": "",
            "categorie_produit": "alimentation",
        }
        row = build_off_row(record, "123")
        assert row["categories"] == "alimentation"

    def test_gtin_used_as_code(self):
        row = build_off_row(SAMPLE_RECORD, "9999999999999")
        assert row["code"] == "9999999999999"

    def test_whitespace_stripped_from_fields(self):
        record = {
            "marque_produit": "  Brand  ",
            "libelle": "  Product  ",
            "sous_categorie_produit": "  Cat  ",
        }
        row = build_off_row(record, "123")
        assert row["brands"] == "Brand"
        assert row["product_name"] == "Product"
        assert row["categories"] == "Cat"

    def test_missing_optional_fields_default_to_empty(self):
        row = build_off_row({}, "123")
        assert row["brands"] == ""
        assert row["rappelconso:fiche_id"] == ""
        assert row["rappelconso:lien_fiche"] == ""


# ---------- check_off_product_exists ----------

class TestCheckOffProductExists:
    @patch("import_rappelconso.requests")
    def test_product_exists(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {"code": "3760000000001"},
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        assert check_off_product_exists("3760000000001") is True

    @patch("import_rappelconso.requests")
    def test_product_not_found_status_zero(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 0}
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        assert check_off_product_exists("9999999999999") is False

    @patch("import_rappelconso.requests")
    def test_product_not_found_404(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response

        assert check_off_product_exists("9999999999999") is False

    @patch("import_rappelconso.requests")
    def test_network_error_returns_none(self, mock_requests):
        import requests as real_requests
        mock_requests.get.side_effect = (
            real_requests.exceptions.ConnectionError("Connection refused")
        )
        mock_requests.exceptions = real_requests.exceptions
        result = check_off_product_exists("3760000000001")
        assert result is None

    def test_uses_provided_session(self):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 1}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        result = check_off_product_exists("123", session=mock_session)
        assert result is True
        assert mock_session.get.called


# ---------- process_recalls ----------

class TestProcessRecalls:
    def test_skips_records_without_gtin(self):
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id": 1,
                "identification_produits": ["", "lot123", "non concerné", ""],
                "marque_produit": "Brand",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=False))
        assert rows == []

    def test_includes_records_with_valid_gtin(self):
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id": 1,
                "identification_produits": [
                    "3760000000001", "lot", "dlc", "2025-01-01", ""
                ],
                "marque_produit": "Brand",
                "libelle": "Product",
                "sous_categorie_produit": "Biscuits",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=False))
        assert len(rows) == 1
        assert rows[0]["code"] == "3760000000001"

    def test_expands_multiple_gtins_per_record(self):
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id": 1,
                "identification_produits": [
                    "1111111111111", "lots", "non concerné", "",
                    "|2222222222222", "lots", "non concerné", "",
                ],
                "marque_produit": "Brand",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=False))
        assert len(rows) == 2
        codes = {r["code"] for r in rows}
        assert codes == {"1111111111111", "2222222222222"}

    def test_deduplicates_gtins_across_records(self):
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id": 1,
                "identification_produits": ["3760000000001", "lot", "dlc", ""],
                "marque_produit": "Brand1",
            },
            {
                "id": 2,
                "identification_produits": ["3760000000001", "lot", "dlc", ""],
                "marque_produit": "Brand2",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=False))
        assert len(rows) == 1

    @patch("import_rappelconso.check_off_product_exists")
    def test_skips_existing_off_products(self, mock_check):
        mock_check.return_value = True
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id": 1,
                "identification_produits": ["3760000000001", "lot", "dlc", ""],
                "marque_produit": "Brand",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=True))
        assert rows == []
        mock_check.assert_called_once_with("3760000000001", session=None)

    @patch("import_rappelconso.check_off_product_exists")
    def test_includes_new_off_products(self, mock_check):
        mock_check.return_value = False
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id": 1,
                "identification_produits": ["3760000000001", "lot", "dlc", ""],
                "marque_produit": "Brand",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=True))
        assert len(rows) == 1

    @patch("import_rappelconso.check_off_product_exists")
    def test_skips_on_off_check_failure(self, mock_check):
        mock_check.return_value = None  # check failed
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id": 1,
                "identification_produits": ["3760000000001", "lot", "dlc", ""],
                "marque_produit": "Brand",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=True))
        assert rows == []

    def test_passes_since_date_to_client(self):
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = []
        list(process_recalls(mock_client, since_date="2024-11-01",
                             check_off=False))
        mock_client.fetch_all_recalls.assert_called_once_with(
            since_date="2024-11-01", category="alimentation"
        )


# ---------- save_csv ----------

class TestSaveCsv:
    def test_writes_headers_and_rows(self):
        rows = [
            {
                "code": "3760000000001",
                "product_name": "Product X",
                "brands": "Brand",
                "categories": "Biscuits",
                "countries": "France",
                "source": "Rappel Conso",
                "rappelconso:fiche_id": "abc123",
                "rappelconso:lien_fiche": "https://example.com",
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_output.csv")
            count = save_csv(rows, output_path)

            assert count == 1
            assert os.path.exists(output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                written_rows = list(reader)

            assert len(written_rows) == 1
            assert written_rows[0]["code"] == "3760000000001"
            assert written_rows[0]["brands"] == "Brand"

    def test_writes_correct_headers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_headers.csv")
            save_csv([], output_path)

            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)

            assert headers == OFF_CSV_HEADERS

    def test_returns_row_count(self):
        rows = [
            {"code": "1", "product_name": "A", "brands": "", "categories": "",
             "countries": "", "source": "", "rappelconso:fiche_id": "",
             "rappelconso:lien_fiche": ""},
            {"code": "2", "product_name": "B", "brands": "", "categories": "",
             "countries": "", "source": "", "rappelconso:fiche_id": "",
             "rappelconso:lien_fiche": ""},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_count.csv")
            count = save_csv(rows, output_path)
        assert count == 2

    def test_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir", "output.csv")
            save_csv([], output_path)
            assert os.path.exists(output_path)
