"""
Real integration test for ModularGrid parser functionality.
This test actually queries ModularGrid without using any mocked data.
"""
import unittest
import sys
import os
import logging
import time

# Add the parent directory to the path so we can import the src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modulargrid_parser import ModularGridParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestRealModularGridIntegration(unittest.TestCase):
    """Test cases for real ModularGrid integration without mocks."""

    def setUp(self):
        """Set up test fixtures."""
        # Create the parser instance
        self.parser = ModularGridParser()

        # Sample real ModularGrid URLs for testing
        # These are actual public racks from ModularGrid
        self.real_rack_urls = [
            "https://www.modulargrid.net/e/racks/view/1890752",  # Popular rack
            "https://www.modulargrid.net/e/racks/view/1890753",  # Another rack
        ]

    def test_real_rack_scraping(self):
        """Test scraping actual ModularGrid racks."""
        for url in self.real_rack_urls:
            logger.info(f"Testing real ModularGrid rack URL: {url}")

            try:
                # Call the _scrape_rack_page method directly to test scraping
                result = self.parser._scrape_rack_page(url)

                # Verify the result has the expected structure
                self.assertIn("rack_name", result)
                self.assertIn("modules", result)

                # Verify we got some modules
                self.assertGreater(len(result["modules"]), 0)

                # Log the results
                logger.info(f"Successfully scraped rack: {result['rack_name']}")
                logger.info(f"Found {len(result['modules'])} modules")

                # Verify module structure
                for module in result["modules"]:
                    self.assertIn("name", module)
                    self.assertIn("manufacturer", module)
                    logger.info(f"Module: {module['name']} by {module['manufacturer']}")

                # Add a small delay between requests to avoid rate limiting
                time.sleep(2)

            except Exception as e:
                self.fail(f"Failed to scrape real ModularGrid rack {url}: {str(e)}")

    def test_real_module_details_extraction(self):
        """Test extracting details from actual ModularGrid module pages."""
        try:
            # Use a direct module URL instead of trying to extract from rack
            # This ensures the test can run even if rack scraping isn't working
            module_url = "https://www.modulargrid.net/e/mutable-instruments-plaits"
            module_name = "Plaits"

            logger.info(f"Testing real module details extraction for: {module_name} at {module_url}")

            # Extract module details
            module_details = self.parser._extract_module_details(module_url)

            # Verify the result has the expected structure
            self.assertIn("name", module_details)
            self.assertIn("manufacturer", module_details)
            self.assertIn("hp_width", module_details)
            self.assertIn("module_type", module_details)
            self.assertIn("description", module_details)

            # Log the results
            logger.info(f"Successfully extracted details for module: {module_details['name']}")
            logger.info(f"Manufacturer: {module_details['manufacturer']}")
            logger.info(f"HP Width: {module_details['hp_width']}")
            logger.info(f"Type: {module_details['module_type']}")

            # Try a second module to ensure robustness
            module_url2 = "https://www.modulargrid.net/e/make-noise-maths"
            module_name2 = "Maths"

            logger.info(f"Testing real module details extraction for: {module_name2} at {module_url2}")

            # Extract module details
            module_details2 = self.parser._extract_module_details(module_url2)

            # Verify the result has the expected structure
            self.assertIn("name", module_details2)
            self.assertIn("manufacturer", module_details2)
            self.assertIn("hp_width", module_details2)

            # Log the results
            logger.info(f"Successfully extracted details for module: {module_details2['name']}")
            logger.info(f"Manufacturer: {module_details2['manufacturer']}")
            logger.info(f"HP Width: {module_details2['hp_width']}")

        except Exception as e:
            self.fail(f"Failed to extract real module details: {str(e)}")

    def test_full_parse_url_integration(self):
        """Test the full parse_url method with a real ModularGrid URL."""
        # This test will need database access, so we'll mock the database operations
        # but still use real HTTP requests to ModularGrid

        from unittest.mock import patch, MagicMock

        # Create mock database objects
        mock_db = MagicMock()
        mock_user_rack = MagicMock()
        mock_module = MagicMock()
        mock_rack_module = MagicMock()

        # Configure the mocks
        mock_db.session = MagicMock()
        mock_user_rack.query.filter_by.return_value.first.return_value = None
        new_rack = MagicMock()
        new_rack.id = 1
        mock_user_rack.return_value = new_rack

        # Patch the database-related imports
        with patch('src.modulargrid_parser.db', mock_db), \
             patch('src.modulargrid_parser.UserRack', mock_user_rack), \
             patch('src.modulargrid_parser.Module', mock_module), \
             patch('src.modulargrid_parser.RackModule', mock_rack_module):

            try:
                # Call the parse_url method with a real URL
                url = self.real_rack_urls[0]
                logger.info(f"Testing full parse_url integration with: {url}")

                result = self.parser.parse_url(url)

                # Verify the result has the expected structure
                self.assertIn("rack_id", result)
                self.assertIn("modulargrid_id", result)
                self.assertIn("rack_name", result)
                self.assertIn("modules", result)

                # Log the results
                logger.info(f"Successfully parsed rack: {result['rack_name']}")
                logger.info(f"Found {len(result['modules'])} modules")

            except Exception as e:
                self.fail(f"Failed to parse real ModularGrid URL {url}: {str(e)}")

if __name__ == '__main__':
    unittest.main()
