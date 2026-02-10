"""Tests for the EPREL API client module."""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from eprel_client import (
    EPREL_API_BASE_URL,
    EPRELClient,
    PRODUCT_CATEGORIES,
    extract_eprel_id,
)


# ---------- extract_eprel_id ----------

class TestExtractEprelId:
    def test_valid_url(self):
        assert extract_eprel_id("https://eprel.ec.europa.eu/qr/12345") == "12345"

    def test_valid_url_large_id(self):
        assert extract_eprel_id("https://eprel.ec.europa.eu/qr/2372864") == "2372864"

    def test_http_url(self):
        assert extract_eprel_id("http://eprel.ec.europa.eu/qr/99999") == "99999"

    def test_invalid_url_missing_id(self):
        assert extract_eprel_id("https://eprel.ec.europa.eu/qr/") is None

    def test_invalid_url_non_numeric(self):
        assert extract_eprel_id("https://eprel.ec.europa.eu/qr/abc") is None

    def test_invalid_url_wrong_domain(self):
        assert extract_eprel_id("https://example.com/qr/12345") is None

    def test_invalid_url_trailing_slash(self):
        assert extract_eprel_id("https://eprel.ec.europa.eu/qr/12345/") is None

    def test_empty_string(self):
        assert extract_eprel_id("") is None

    def test_random_string(self):
        assert extract_eprel_id("not a url at all") is None


# ---------- EPRELClient ----------

class TestEPRELClient:
    def test_init_default(self):
        client = EPRELClient()
        assert client.base_url == EPREL_API_BASE_URL
        assert client.api_key is None
        assert client.timeout == 30
        assert "x-api-key" not in client.session.headers
        client.close()

    def test_init_with_api_key(self):
        client = EPRELClient(api_key="test-key-123")
        assert client.session.headers["x-api-key"] == "test-key-123"
        client.close()

    def test_context_manager(self):
        with EPRELClient() as client:
            assert client is not None

    def test_get_product_invalid_category(self):
        with EPRELClient() as client:
            with pytest.raises(ValueError, match="Unknown category"):
                client.get_product("nonexistent_category", "12345")

    def test_list_products_invalid_category(self):
        with EPRELClient() as client:
            with pytest.raises(ValueError, match="Unknown category"):
                client.list_products("nonexistent_category")


class TestEPRELClientRequests:
    """Tests that mock HTTP requests."""

    @patch("eprel_client.requests.Session")
    def test_get_product_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "eprelRegistrationNumber": 12345,
            "supplierOrTrademark": "TestBrand",
            "modelIdentifier": "TestModel",
        }
        mock_response.raise_for_status.return_value = None
        mock_session.request.return_value = mock_response

        with EPRELClient() as client:
            result = client.get_product("smartphones", "12345")

        assert result["eprelRegistrationNumber"] == 12345
        assert result["supplierOrTrademark"] == "TestBrand"

    @patch("eprel_client.requests.Session")
    def test_list_products_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [111, 222, 333],
            "total": 3,
        }
        mock_response.raise_for_status.return_value = None
        mock_session.request.return_value = mock_response

        with EPRELClient() as client:
            result = client.list_products("smartphones", page=0, page_size=10)

        assert result["hits"] == [111, 222, 333]
        assert result["total"] == 3

    @patch("eprel_client.requests.Session")
    def test_get_product_not_found(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            response=mock_response
        )
        mock_session.request.return_value = mock_response

        with EPRELClient() as client:
            with pytest.raises(requests.HTTPError):
                client.get_product("smartphones", "99999999")

    @patch("eprel_client.requests.Session")
    def test_fetch_all_products_pagination(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        # First page
        response_page0 = MagicMock()
        response_page0.status_code = 200
        response_page0.json.return_value = {
            "hits": [101, 102],
            "total": 3,
        }
        response_page0.raise_for_status.return_value = None

        # Second page
        response_page1 = MagicMock()
        response_page1.status_code = 200
        response_page1.json.return_value = {
            "hits": [103],
            "total": 3,
        }
        response_page1.raise_for_status.return_value = None

        mock_session.request.side_effect = [response_page0, response_page1]

        with EPRELClient() as client:
            all_hits = []
            for page_hits in client.fetch_all_products(
                "smartphones", page_size=2
            ):
                all_hits.extend(page_hits)

        assert all_hits == [101, 102, 103]

    @patch("eprel_client.requests.Session")
    def test_fetch_all_products_max_pages(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "hits": [1, 2, 3],
            "total": 100,
        }
        response.raise_for_status.return_value = None
        mock_session.request.return_value = response

        with EPRELClient() as client:
            pages = list(
                client.fetch_all_products("smartphones", max_pages=1)
            )

        assert len(pages) == 1
        assert pages[0] == [1, 2, 3]

    @patch("eprel_client.requests.Session")
    def test_fetch_all_products_empty(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"hits": [], "total": 0}
        response.raise_for_status.return_value = None
        mock_session.request.return_value = response

        with EPRELClient() as client:
            pages = list(client.fetch_all_products("smartphones"))

        assert pages == []


class TestProductCategories:
    def test_smartphones_category_exists(self):
        assert "smartphones" in PRODUCT_CATEGORIES

    def test_televisions_category_exists(self):
        assert "televisions" in PRODUCT_CATEGORIES

    def test_washingmachines_category_exists(self):
        assert "washingmachines" in PRODUCT_CATEGORIES

    def test_category_values_are_strings(self):
        for key, value in PRODUCT_CATEGORIES.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
