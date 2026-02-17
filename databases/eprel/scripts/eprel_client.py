"""EPREL API client for fetching product data from the EU EPREL database.

The European Product Registry for Energy Labelling (EPREL) provides an API
to access energy labelling and technical data for products sold in the EU.

API base URL: https://eprel.ec.europa.eu/api/v1
Labels URL pattern: https://eprel.ec.europa.eu/labels/{category}/Label_{id}.svg
"""

import logging
import os
import re
import time
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)

EPREL_API_BASE_URL = "https://eprel.ec.europa.eu/api/v1"
EPREL_LABELS_BASE_URL = "https://eprel.ec.europa.eu/labels"
EPREL_QR_URL_PATTERN = re.compile(
    r"^https?://eprel\.ec\.europa\.eu/qr/(\d+)$"
)

# Product category paths as defined by the EPREL API
PRODUCT_CATEGORIES = {
    "airconditioners": "airconditioners",
    "dishwashers": "dishwashers",
    "displays": "displays",
    "driers": "driers",
    "lamps": "lamps",
    "lightsources": "lightsources",
    "localspaceheaters": "localspaceheaters",
    "ovens": "ovens",
    "professionalrefrigeratedstoragecabinets": (
        "professionalrefrigeratedstoragecabinets"
    ),
    "rangehoods": "rangehoods",
    "refrigeratingappliances": "refrigeratingappliances",
    "smartphones": "smartphonestablets20231669",
    "solidfuelboilers": "solidfuelboilers",
    "spaceheaters": "spaceheaters",
    "televisions": "televisions",
    "tyres": "tyres",
    "washerdriers": "washerdriers",
    "washingmachines": "washingmachines",
    "waterheaters": "waterheaters",
}

DEFAULT_PAGE_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
# EPREL API limit: 5 requests per second
MAX_REQUESTS_PER_SECOND = 5
MIN_REQUEST_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND


def extract_eprel_id(qr_url):
    """Extract the EPREL product ID from a QR code URL.

    Args:
        qr_url: Full URL string (e.g., "https://eprel.ec.europa.eu/qr/12345")

    Returns:
        The EPREL ID as a string, or None if the URL is invalid.
    """
    match = EPREL_QR_URL_PATTERN.match(qr_url)
    if match:
        return match.group(1)
    return None


class EPRELClient:
    """Client for interacting with the EPREL API.

    Args:
        api_key: Optional API key for authenticated requests.
        base_url: Base URL for the EPREL API.
        timeout: Request timeout in seconds.
    """

    def __init__(self, api_key=None, base_url=EPREL_API_BASE_URL, timeout=30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._last_request_time = 0.0
        self.session = requests.Session()
        if api_key:
            self.session.headers["x-api-key"] = api_key
        self.session.headers["Accept"] = "application/json"

    def _request(self, method, path, params=None):
        """Make an HTTP request to the EPREL API with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path relative to base URL.
            params: Query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: If the request fails after retries.
        """
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        last_exception = None

        for attempt in range(MAX_RETRIES):
            # Enforce rate limit: wait if needed
            elapsed = time.monotonic() - self._last_request_time
            if elapsed < MIN_REQUEST_INTERVAL:
                time.sleep(MIN_REQUEST_INTERVAL - elapsed)

            try:
                self._last_request_time = time.monotonic()
                response = self.session.request(
                    method, url, params=params, timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                last_exception = e
                if response.status_code == 429:
                    wait_time = RETRY_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(
                        "Rate limited (429). Retrying in %ds (attempt %d/%d)",
                        wait_time, attempt + 1, MAX_RETRIES,
                    )
                    time.sleep(wait_time)
                elif response.status_code >= 500:
                    wait_time = RETRY_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(
                        "Server error (%d). Retrying in %ds (attempt %d/%d)",
                        response.status_code, wait_time,
                        attempt + 1, MAX_RETRIES,
                    )
                    time.sleep(wait_time)
                else:
                    raise
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                wait_time = RETRY_DELAY_SECONDS * (2 ** attempt)
                logger.warning(
                    "Connection error. Retrying in %ds (attempt %d/%d)",
                    wait_time, attempt + 1, MAX_RETRIES,
                )
                time.sleep(wait_time)

        raise last_exception

    def get_product(self, category, eprel_id):
        """Fetch a single product by its EPREL ID and category.

        Args:
            category: Product category key (e.g., "smartphones").
            eprel_id: The EPREL registration number.

        Returns:
            Product data as a dictionary.

        Raises:
            ValueError: If the category is not recognized.
            requests.HTTPError: If the API request fails.
        """
        category_path = PRODUCT_CATEGORIES.get(category)
        if not category_path:
            raise ValueError(
                f"Unknown category '{category}'. "
                f"Available: {', '.join(sorted(PRODUCT_CATEGORIES.keys()))}"
            )
        path = f"{category_path}/{eprel_id}"
        return self._request("GET", path)

    def list_products(self, category, page=0, page_size=DEFAULT_PAGE_SIZE):
        """List products in a category with pagination.

        Args:
            category: Product category key (e.g., "smartphones").
            page: Page number (0-indexed).
            page_size: Number of results per page.

        Returns:
            A dictionary with product listing results including
            a 'hits' list and 'total' count.

        Raises:
            ValueError: If the category is not recognized.
            requests.HTTPError: If the API request fails.
        """
        category_path = PRODUCT_CATEGORIES.get(category)
        if not category_path:
            raise ValueError(
                f"Unknown category '{category}'. "
                f"Available: {', '.join(sorted(PRODUCT_CATEGORIES.keys()))}"
            )
        params = {
            "manufacturer": "",
            "tradeMark": "",
            "from": page * page_size,
            "size": page_size,
        }
        return self._request("GET", category_path, params=params)

    def fetch_all_products(self, category, max_pages=None,
                           page_size=DEFAULT_PAGE_SIZE):
        """Fetch all products in a category, handling pagination.

        Args:
            category: Product category key (e.g., "smartphones").
            max_pages: Maximum number of pages to fetch (None for all).
            page_size: Number of results per page.

        Yields:
            Product EPREL IDs from each page of results.
        """
        page = 0
        while True:
            if max_pages is not None and page >= max_pages:
                logger.info("Reached max_pages limit (%d)", max_pages)
                break

            logger.info(
                "Fetching page %d for category '%s'", page, category
            )
            result = self.list_products(
                category, page=page, page_size=page_size
            )

            hits = result.get("hits", [])
            if not hits:
                logger.info("No more results for category '%s'", category)
                break

            yield hits

            total = result.get("total", 0)
            fetched = (page + 1) * page_size
            if fetched >= total:
                logger.info(
                    "Fetched all %d products for category '%s'",
                    total, category,
                )
                break

            page += 1

    def close(self):
        """Close the underlying HTTP session."""
        self.session.close()

    @staticmethod
    def get_label_url(category, eprel_id):
        """Build the URL for a product's energy label SVG.

        Args:
            category: Product category key (e.g., "smartphones").
            eprel_id: The EPREL registration number.

        Returns:
            URL string for the label SVG.

        Raises:
            ValueError: If the category is not recognized.
        """
        category_path = PRODUCT_CATEGORIES.get(category)
        if not category_path:
            raise ValueError(
                f"Unknown category '{category}'. "
                f"Available: {', '.join(sorted(PRODUCT_CATEGORIES.keys()))}"
            )
        return (
            f"{EPREL_LABELS_BASE_URL}/{category_path}/"
            f"Label_{eprel_id}.svg"
        )

    def download_label(self, category, eprel_id, output_dir):
        """Download the energy label SVG for a product.

        Args:
            category: Product category key (e.g., "smartphones").
            eprel_id: The EPREL registration number.
            output_dir: Directory to save the SVG file.

        Returns:
            Path to the downloaded SVG file, or None if download failed.
        """
        url = self.get_label_url(category, eprel_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(
            output_dir, f"Label_{eprel_id}.svg"
        )

        # Enforce rate limit
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)

        try:
            self._last_request_time = time.monotonic()
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info("Downloaded label to %s", output_path)
            return output_path
        except requests.exceptions.RequestException:
            logger.warning(
                "Failed to download label for %s/%s", category, eprel_id
            )
            return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
