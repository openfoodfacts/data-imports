"""Tests for the Rappel Conso API client module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from rappelconso_client import (
    FOOD_CATEGORY,
    MAX_PAGE_SIZE,
    RAPPELCONSO_API_BASE_URL,
    RappelConsoClient,
)


class TestRappelConsoClient:
    def test_init_default(self):
        client = RappelConsoClient()
        assert client.base_url == RAPPELCONSO_API_BASE_URL
        assert client.timeout == 30
        client.close()

    def test_init_custom_url(self):
        client = RappelConsoClient(base_url="https://example.com/api")
        assert client.base_url == "https://example.com/api"
        client.close()

    def test_context_manager(self):
        with RappelConsoClient() as client:
            assert client is not None

    def test_food_category_constant(self):
        assert FOOD_CATEGORY == "Alimentation"

    def test_max_page_size(self):
        assert MAX_PAGE_SIZE == 100


class TestRappelConsoClientRequests:
    """Tests that mock HTTP requests."""

    @patch("rappelconso_client.requests.Session")
    def test_fetch_recalls_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_count": 2,
            "results": [
                {
                    "id_fiche": "001",
                    "nom_de_la_marque_du_produit": "TestBrand",
                    "gtin": "3760000000001",
                    "categorie_de_produit": "Alimentation",
                    "date_de_publication": "2024-11-29",
                },
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        with RappelConsoClient() as client:
            result = client.fetch_recalls()

        assert result["total_count"] == 2
        assert len(result["results"]) == 1
        assert result["results"][0]["id_fiche"] == "001"

    @patch("rappelconso_client.requests.Session")
    def test_fetch_recalls_with_date_filter(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_count": 0, "results": []}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        with RappelConsoClient() as client:
            client.fetch_recalls(
                since_date="2024-11-01", category="Alimentation"
            )

        call_kwargs = mock_session.get.call_args
        params = call_kwargs[1]["params"]
        assert 'date_de_publication >= "2024-11-01"' in params["where"]
        assert 'categorie_de_produit = "Alimentation"' in params["where"]

    @patch("rappelconso_client.requests.Session")
    def test_fetch_recalls_date_object(self, mock_session_cls):
        """fetch_recalls accepts a date object for since_date."""
        import datetime

        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_count": 0, "results": []}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        with RappelConsoClient() as client:
            client.fetch_recalls(
                since_date=datetime.date(2024, 11, 1)
            )

        call_kwargs = mock_session.get.call_args
        params = call_kwargs[1]["params"]
        assert 'date_de_publication >= "2024-11-01"' in params["where"]

    @patch("rappelconso_client.requests.Session")
    def test_fetch_recalls_no_filters(self, mock_session_cls):
        """fetch_recalls with no filters sends no 'where' param."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_count": 0, "results": []}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        with RappelConsoClient() as client:
            client.fetch_recalls()

        call_kwargs = mock_session.get.call_args
        params = call_kwargs[1]["params"]
        assert "where" not in params

    @patch("rappelconso_client.requests.Session")
    def test_fetch_recalls_limit_capped_at_max(self, mock_session_cls):
        """Limit is capped at MAX_PAGE_SIZE even if higher value given."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_count": 0, "results": []}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        with RappelConsoClient() as client:
            client.fetch_recalls(limit=9999)

        call_kwargs = mock_session.get.call_args
        params = call_kwargs[1]["params"]
        assert params["limit"] == MAX_PAGE_SIZE

    @patch("rappelconso_client.requests.Session")
    def test_fetch_all_recalls_pagination(self, mock_session_cls):
        """fetch_all_recalls handles multi-page results."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        page1 = MagicMock()
        page1.status_code = 200
        page1.json.return_value = {
            "total_count": 3,
            "results": [{"id_fiche": "001"}, {"id_fiche": "002"}],
        }
        page1.raise_for_status.return_value = None

        page2 = MagicMock()
        page2.status_code = 200
        page2.json.return_value = {
            "total_count": 3,
            "results": [{"id_fiche": "003"}],
        }
        page2.raise_for_status.return_value = None

        mock_session.get.side_effect = [page1, page2]

        with RappelConsoClient() as client:
            records = list(client.fetch_all_recalls())

        assert len(records) == 3
        assert records[0]["id_fiche"] == "001"
        assert records[2]["id_fiche"] == "003"

    @patch("rappelconso_client.requests.Session")
    def test_fetch_all_recalls_empty_results(self, mock_session_cls):
        """fetch_all_recalls returns empty list when no records found."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_count": 0, "results": []}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        with RappelConsoClient() as client:
            records = list(client.fetch_all_recalls())

        assert records == []

    @patch("rappelconso_client.requests.Session")
    def test_fetch_recalls_server_error_retries(self, mock_session_cls):
        """Retries on 500 server errors."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        error_response = MagicMock()
        error_response.status_code = 500
        http_error = requests.HTTPError(response=error_response)
        error_response.raise_for_status.side_effect = http_error

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"total_count": 0, "results": []}
        success_response.raise_for_status.return_value = None

        mock_session.get.side_effect = [
            error_response, success_response
        ]

        with RappelConsoClient() as client:
            result = client.fetch_recalls()

        assert result["total_count"] == 0
        assert mock_session.get.call_count == 2

    @patch("rappelconso_client.requests.Session")
    def test_fetch_recalls_404_raises_immediately(self, mock_session_cls):
        """Non-retryable HTTP errors (e.g. 404) are raised immediately."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            response=mock_response
        )
        mock_session.get.return_value = mock_response

        with RappelConsoClient() as client:
            with pytest.raises(requests.HTTPError):
                client.fetch_recalls()

        assert mock_session.get.call_count == 1
