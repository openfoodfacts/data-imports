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
    def test_single_gtin(self):
        assert extract_gtins("3760000000001") == ["3760000000001"]

    def test_multiple_gtins_space_separated(self):
        result = extract_gtins("3760000000001 9876543210987")
        assert result == ["3760000000001", "9876543210987"]

    def test_empty_string(self):
        assert extract_gtins("") == []

    def test_none_input(self):
        assert extract_gtins(None) == []

    def test_non_numeric_filtered_out(self):
        assert extract_gtins("N/A") == []

    def test_mixed_numeric_and_text_filtered(self):
        result = extract_gtins("3760000000001 N/A")
        assert result == ["3760000000001"]

    def test_whitespace_only(self):
        assert extract_gtins("   ") == []

    def test_leading_trailing_whitespace_stripped(self):
        assert extract_gtins("  3760000000001  ") == ["3760000000001"]

    def test_three_gtins(self):
        result = extract_gtins("111 222 333")
        assert result == ["111", "222", "333"]


# ---------- build_off_row ----------

SAMPLE_RECORD = {
    "id_fiche": "abc123",
    "titre_du_rappel": "Rappel produit X",
    "nom_de_la_marque_du_produit": "TestBrand",
    "noms_des_modeles_ou_references": "Product X",
    "identification_des_produits": "Lot ABC",
    "gtin": "3760000000001",
    "categorie_de_produit": "Alimentation",
    "sous_categorie_de_produit": "Biscuits et gateaux",
    "date_de_publication": "2024-11-29",
    "lien_vers_la_fiche_rappelconso": "https://rappelconso.fr/abc123",
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
        assert row["rappelconso:fiche_id"] == "abc123"
        assert row["rappelconso:lien_fiche"] == "https://rappelconso.fr/abc123"

    def test_recall_data_excluded(self):
        """Recall-specific fields should not appear in the OFF row."""
        row = build_off_row(SAMPLE_RECORD, "3760000000001")
        assert "titre_du_rappel" not in row
        assert "date_de_publication" not in row

    def test_fallback_to_identification_when_no_model_name(self):
        record = {
            "nom_de_la_marque_du_produit": "Brand",
            "noms_des_modeles_ou_references": "",
            "identification_des_produits": "Fallback Name",
        }
        row = build_off_row(record, "123")
        assert row["product_name"] == "Fallback Name"

    def test_fallback_to_brand_when_no_name_fields(self):
        record = {
            "nom_de_la_marque_du_produit": "OnlyBrand",
            "noms_des_modeles_ou_references": "",
            "identification_des_produits": "",
        }
        row = build_off_row(record, "123")
        assert row["product_name"] == "OnlyBrand"

    def test_fallback_category_to_parent(self):
        record = {
            "nom_de_la_marque_du_produit": "Brand",
            "noms_des_modeles_ou_references": "Prod",
            "sous_categorie_de_produit": "",
            "categorie_de_produit": "Alimentation",
        }
        row = build_off_row(record, "123")
        assert row["categories"] == "Alimentation"

    def test_gtin_used_as_code(self):
        row = build_off_row(SAMPLE_RECORD, "9999999999999")
        assert row["code"] == "9999999999999"

    def test_whitespace_stripped_from_fields(self):
        record = {
            "nom_de_la_marque_du_produit": "  Brand  ",
            "noms_des_modeles_ou_references": "  Product  ",
            "sous_categorie_de_produit": "  Cat  ",
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
                "id_fiche": "001",
                "gtin": "",
                "nom_de_la_marque_du_produit": "Brand",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=False))
        assert rows == []

    def test_includes_records_with_valid_gtin(self):
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id_fiche": "001",
                "gtin": "3760000000001",
                "nom_de_la_marque_du_produit": "Brand",
                "noms_des_modeles_ou_references": "Product",
                "sous_categorie_de_produit": "Biscuits",
            },
        ]
        rows = list(process_recalls(mock_client, check_off=False))
        assert len(rows) == 1
        assert rows[0]["code"] == "3760000000001"

    def test_expands_multiple_gtins_per_record(self):
        mock_client = MagicMock()
        mock_client.fetch_all_recalls.return_value = [
            {
                "id_fiche": "001",
                "gtin": "1111111111111 2222222222222",
                "nom_de_la_marque_du_produit": "Brand",
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
                "id_fiche": "001",
                "gtin": "3760000000001",
                "nom_de_la_marque_du_produit": "Brand1",
            },
            {
                "id_fiche": "002",
                "gtin": "3760000000001",
                "nom_de_la_marque_du_produit": "Brand2",
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
                "id_fiche": "001",
                "gtin": "3760000000001",
                "nom_de_la_marque_du_produit": "Brand",
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
                "id_fiche": "001",
                "gtin": "3760000000001",
                "nom_de_la_marque_du_produit": "Brand",
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
                "id_fiche": "001",
                "gtin": "3760000000001",
                "nom_de_la_marque_du_produit": "Brand",
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
            since_date="2024-11-01", category="Alimentation"
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
