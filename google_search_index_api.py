import os
import pickle
import time
import requests
import xml.etree.ElementTree as ET
import socket
import sys
import logging
import backoff
from requests.exceptions import RequestException
from typing import List, Dict, Any

### Install the following packages in PyCharm terminal:
### pip install google-auth-oauthlib google-auth google-api-python-client requests backoff
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("google_indexing.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class GoogleIndexingAPI:
    """Class for handling Google Search Indexing API"""

    def __init__(self, client_secret_file: str, index_type: int = 1):
        """
        Initialize GoogleIndexingAPI class

        Args:
            client_secret_file: Google API client secret file path
            index_type: Index type (0: delete index, 1: register index)
        """
        self.client_secret_file = client_secret_file
        self.index_type = index_type  # 0: delete index / 1: register index
        self.work_dir = "./"
        self.scopes = ["https://www.googleapis.com/auth/indexing"]
        self.token_file_path = os.path.join(self.work_dir, "auto_token.pickle")
        self.service = None
        self.success_count = 0
        self.error_count = 0

    def authenticate(self) -> bool:
        """
        Perform Google API authentication and initialize service.

        Returns:
            bool: Authentication success status
        """
        try:
            logger.info("Starting Google API authentication...")

            # Delete existing token file (for fresh authentication)
            if os.path.exists(self.token_file_path):
                os.remove(self.token_file_path)
                logger.info("Deleted existing token file.")

            # Set OAUTHLIB_INSECURE_TRANSPORT (for local development)
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

            # Configure authentication flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_file, scopes=self.scopes
            )

            print("=" * 80)
            print("Starting Google OAuth authentication.")
            print("Your browser will open automatically shortly.")
            print(
                "Please log in with your Google account and authorize the application."
            )
            print("=" * 80)

            # Try multiple ports
            ports_to_try = [3000, 8080, 8081, 8082, 0]  # 0 = auto-find available port

            for port in ports_to_try:
                try:
                    logger.info(f"Attempting to start local server on port {port}...")

                    if port == 0:
                        # Auto-find available port
                        creds = flow.run_local_server(
                            port=0, access_type="offline", prompt="consent"
                        )
                    else:
                        # Use specific port
                        creds = flow.run_local_server(
                            port=port, access_type="offline", prompt="consent"
                        )

                    logger.info("Authentication completed successfully!")
                    break

                except OSError as e:
                    if "Address already in use" in str(e) or "WinError 10048" in str(e):
                        logger.warning(
                            f"Port {port} is already in use. Trying another port..."
                        )
                        continue
                    else:
                        logger.error(f"Error on port {port}: {e}")
                        continue
                except Exception as e:
                    logger.error(f"Authentication failed on port {port}: {e}")
                    continue
            else:
                # Failed on all ports
                logger.error("Authentication failed on all ports.")
                logger.error(
                    "Please verify the following redirect URIs are configured in Google Cloud Console:"
                )
                logger.error("- http://localhost:3000")
                logger.error("- http://localhost:8080")
                logger.error("- http://localhost:8081")
                logger.error("- http://localhost:8082")
                return False

            # Save token
            with open(self.token_file_path, "wb") as token:
                pickle.dump(creds, token)
            logger.info("Authentication token saved to file.")

            # Initialize service
            self.service = build("indexing", "v3", credentials=creds)
            logger.info(
                "Google API authentication and service initialization completed"
            )
            return True

        except Exception as e:
            logger.error(f"Error occurred during authentication: {e}")
            return False

    @backoff.on_exception(
        backoff.expo,
        (HttpError, socket.error, OSError, ConnectionError),
        max_tries=3,
        giveup=lambda e: isinstance(e, HttpError)
        and e.resp.status >= 400
        and e.resp.status != 429,
    )
    def notify_url_updated(self, url: str) -> Dict[str, Any]:
        """
        Request to register or delete URL in Google Search index.

        Args:
            url: URL to register/delete in index

        Returns:
            Dict: API response result
        """
        if not self.service:
            logger.error(
                "API service is not initialized. Please call authenticate() method first."
            )
            return {"error": "Service not initialized"}

        try:
            index_type = "URL_DELETED" if self.index_type == 0 else "URL_UPDATED"
            body = {"url": url, "type": index_type}
            response = self.service.urlNotifications().publish(body=body).execute()
            self.success_count += 1
            return response
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                logger.warning(
                    f"API rate limit exceeded. Waiting 60 seconds before retry."
                )
                time.sleep(60)
                return self.notify_url_updated(url)
            elif e.resp.status >= 400:
                logger.error(f"API error ({e.resp.status}): {e}")
                self.error_count += 1
                return {"error": f"HTTP Error {e.resp.status}: {str(e)}"}
        except (socket.error, OSError) as e:
            logger.error(f"Network error: {e}. Retrying...")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.error_count += 1
            return {"error": str(e)}


class SitemapProcessor:
    """Class for processing sitemaps and extracting URLs"""

    def __init__(self, sitemap_url: str):
        """
        Initialize SitemapProcessor class

        Args:
            sitemap_url: Sitemap URL to process
        """
        self.sitemap_url = sitemap_url

    def extract_urls(self) -> List[str]:
        """
        Extract URL list from sitemap.

        Returns:
            List[str]: List of extracted URLs
        """
        try:
            logger.info(f"Fetching data from sitemap URL: {self.sitemap_url}")
            response = requests.get(self.sitemap_url, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Handle XML namespaces
            namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Extract URLs
            urls = []
            # Handle regular sitemap format
            for url_element in root.findall(".//ns:url", namespaces):
                loc_element = url_element.find("ns:loc", namespaces)
                if loc_element is not None and loc_element.text:
                    urls.append(loc_element.text)

            # Handle sitemap index format
            if not urls:
                for sitemap_element in root.findall(".//ns:sitemap", namespaces):
                    loc_element = sitemap_element.find("ns:loc", namespaces)
                    if loc_element is not None and loc_element.text:
                        logger.info(
                            f"Sub-sitemap found: {loc_element.text}, processing..."
                        )
                        sub_processor = SitemapProcessor(loc_element.text)
                        urls.extend(sub_processor.extract_urls())

            logger.info(f"Extracted {len(urls)} URLs from sitemap.")
            return urls

        except RequestException as e:
            logger.error(f"Network error occurred while accessing sitemap: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            logger.error("Please check if the sitemap format is correct.")
            return []
        except Exception as e:
            logger.error(f"Error occurred while extracting URLs from sitemap: {e}")
            return []


class IndexingManager:
    """Class for managing URL index registration/deletion operations"""

    def __init__(
        self,
        sitemap_url: str,
        client_secret_file: str,
        index_type: int = 1,
        daily_limit: int = 200,
    ):
        """
        Initialize IndexingManager class

        Args:
            sitemap_url: Sitemap URL
            client_secret_file: Google API client secret file path
            index_type: Index type (0: delete index, 1: register index)
            daily_limit: Daily processing limit
        """
        self.sitemap_url = sitemap_url
        self.client_secret_file = client_secret_file
        self.index_type = index_type
        self.daily_limit = daily_limit
        self.sitemap_processor = SitemapProcessor(sitemap_url)
        self.indexing_api = GoogleIndexingAPI(client_secret_file, index_type)

    def run(self) -> bool:
        """
        Execute indexing operation.

        Returns:
            bool: Operation success status
        """
        try:
            # 1. API authentication
            if not self.indexing_api.authenticate():
                logger.error("Google API authentication failed.")
                return False

            # 2. Extract URLs from sitemap
            urls_to_index = self.sitemap_processor.extract_urls()
            if not urls_to_index:
                logger.error("Could not extract URLs from sitemap.")
                return False

            # 3. Display extracted URL list
            logger.info("Extracted URL list (max 10 displayed):")
            for idx, url in enumerate(urls_to_index[:10], 1):
                logger.info(f"{idx}. {url}")
            if len(urls_to_index) > 10:
                logger.info(f"... and {len(urls_to_index) - 10} more")

            # 4. Handle daily limit
            urls_to_process = urls_to_index[: self.daily_limit]
            if len(urls_to_index) > self.daily_limit:
                logger.warning(
                    f"Warning: Processing only {self.daily_limit} URLs out of {len(urls_to_index)} total URLs due to daily limit."
                )

            # 5. Execute indexing operation
            logger.info("\nStarting index registration with Google Search Console...\n")
            for idx, url in enumerate(urls_to_process, 1):
                try:
                    logger.info(f"[{idx}/{len(urls_to_process)}] Processing: {url}")
                    response = self.indexing_api.notify_url_updated(url)

                    if "error" in response:
                        logger.error(f"Error: {response['error']}")
                    else:
                        logger.info(f"Result: {response}")

                    # Delay to prevent API rate limiting
                    time.sleep(1)

                except KeyboardInterrupt:
                    logger.warning("\nProgram interrupted by user.")
                    break
                except Exception as e:
                    logger.error(f"Error occurred while processing URL: {e}")
                    # Continue with non-fatal errors
                    continue

            # 6. Result summary
            self._print_summary()
            return True

        except KeyboardInterrupt:
            logger.warning("\nProgram interrupted by user.")
            self._print_summary()
            return False
        except Exception as e:
            logger.error(f"Error occurred during operation: {e}")
            return False

    def _print_summary(self):
        """Print operation result summary."""
        logger.info("\n=== Processing Result Summary ===")
        logger.info(
            f"Total processed URLs: {self.indexing_api.success_count + self.indexing_api.error_count}"
        )
        logger.info(f"Successful: {self.indexing_api.success_count}")
        logger.info(f"Failed: {self.indexing_api.error_count}")
        logger.info("\nAll URL processing completed.")


def main():
    """Main function"""
    # Default configuration values
    sitemap_url = "https://textmachine.org/sitemap.xml"
    client_secret_file = "client_secret_1092233429048-mkdns68ootdslvpm8gupah7udl1bb08u.apps.googleusercontent.com.json"
    index_type = 1  # 1: register index, 0: delete index
    daily_limit = 800  # Daily processing limit

    logger.info("=== Google Search Console Indexing Tool ===")
    logger.info(f"Sitemap URL: {sitemap_url}")
    logger.info(
        f"Operation type: {'Index registration' if index_type == 1 else 'Index deletion'}"
    )
    logger.info(f"Daily limit: {daily_limit}")

    # Check client secret file
    if not os.path.exists(client_secret_file):
        logger.error(f"Error: Client secret file not found: {client_secret_file}")
        sys.exit(1)

    # Create and run indexing manager
    manager = IndexingManager(
        sitemap_url=sitemap_url,
        client_secret_file=client_secret_file,
        index_type=index_type,
        daily_limit=daily_limit,
    )

    success = manager.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
