"""Rappel Conso API client.

Fetches product recall data from the French government's Rappel Conso database,
available via data.economie.gouv.fr (OpenDataSoft API v2.1).

Dataset: rappelconso-v2-gtin-espaces
API docs: https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/
"""

import logging
import time

import requests

logger = logging.getLogger(__name__)

RAPPELCONSO_API_BASE_URL = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets"
    "/rappelconso-v2-gtin-espaces"
)

# Food product category in Rappel Conso (lowercase as returned by the API)
FOOD_CATEGORY = "alimentation"

# Maximum records per API request (OpenDataSoft limit)
MAX_PAGE_SIZE = 100

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


class RappelConsoClient:
    """Client for fetching recall data from the Rappel Conso API.

    Args:
        base_url: Base URL for the Rappel Conso dataset API.
        timeout: Request timeout in seconds.
    """

    def __init__(self, base_url=RAPPELCONSO_API_BASE_URL, timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"

    def _request(self, params=None):
        """Make a GET request to the records endpoint with retry logic.

        Args:
            params: Query parameters dict.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: If the request fails after retries.
        """
        url = f"{self.base_url}/records"
        last_exception = None

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url, params=params, timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                last_exception = e
                if response.status_code >= 500:
                    wait = RETRY_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(
                        "Server error (%d). Retrying in %ds (attempt %d/%d).",
                        response.status_code, wait, attempt + 1, MAX_RETRIES,
                    )
                    time.sleep(wait)
                else:
                    raise
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                wait = RETRY_DELAY_SECONDS * (2 ** attempt)
                logger.warning(
                    "Connection error. Retrying in %ds (attempt %d/%d).",
                    wait, attempt + 1, MAX_RETRIES,
                )
                time.sleep(wait)

        raise last_exception

    def fetch_recalls(self, since_date=None, category=None,
                      limit=MAX_PAGE_SIZE, offset=0):
        """Fetch recall records from the API.

        Args:
            since_date: Only fetch records published on or after this date.
                May be a date object or ISO date string (YYYY-MM-DD).
            category: Filter by product category (e.g., "Alimentation").
            limit: Number of records per page (max 100).
            offset: Pagination offset.

        Returns:
            Dict with 'total_count' and 'results' keys.
        """
        params = {
            "limit": min(limit, MAX_PAGE_SIZE),
            "offset": offset,
            "order_by": "date_publication desc",
        }

        filters = []
        if since_date:
            if hasattr(since_date, "isoformat"):
                since_date = since_date.isoformat()
            filters.append(f'date_publication >= "{since_date}"')
        if category:
            filters.append(f'categorie_produit = "{category}"')

        if filters:
            params["where"] = " AND ".join(filters)

        return self._request(params=params)

    def fetch_all_recalls(self, since_date=None, category=None):
        """Fetch all recall records, handling pagination automatically.

        Args:
            since_date: Only fetch records published on or after this date.
            category: Filter by product category.

        Yields:
            Individual recall record dicts.
        """
        offset = 0
        total = None

        while True:
            result = self.fetch_recalls(
                since_date=since_date,
                category=category,
                limit=MAX_PAGE_SIZE,
                offset=offset,
            )

            if total is None:
                total = result.get("total_count", 0)
                logger.info("Total records: %d", total)

            records = result.get("results", [])
            if not records:
                break

            yield from records

            offset += len(records)
            if offset >= total:
                break

    def close(self):
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
