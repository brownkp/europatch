"""
Integration tests for the ModularGrid parser functionality.
"""
import unittest
import sys
import os
import logging
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup

# Add the parent directory to the path so we can import the src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modulargrid_parser import ModularGridParser
from src.models import db, Module, UserRack, RackModule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestModularGridParser(unittest.TestCase):
    """Test cases for the ModularGridParser class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database session
        self.db_mock = MagicMock()
        self.db_mock.session = MagicMock()
        self.db_mock.session.commit = MagicMock()
        self.db_mock.session.rollback = MagicMock()

        # Create the parser instance
        self.parser = ModularGridParser()

        # Sample ModularGrid URLs for testing
        self.valid_urls = [
            "https://www.modulargrid.net/e/racks/view/123456",
            "https://www.modulargrid.net/e/racks/view/987654",
            "https://modulargrid.net/e/racks/view/555555",
            "/e/racks/view/111111"  # Relative URL
        ]

        self.invalid_urls = [
            "https://www.modulargrid.net/e/modules/view/123",
            "https://www.example.com/rack/123456",
            "invalid_url",
            ""
        ]

    @patch('src.modulargrid_parser.db')
    @patch('src.modulargrid_parser.UserRack')
    @patch('src.modulargrid_parser.Module')
    @patch('src.modulargrid_parser.RackModule')
    def test_parse_url_valid_format(self, mock_rack_module, mock_module, mock_user_rack, mock_db):
        """Test parsing a URL with valid format."""
        # Setup mocks
        mock_db.session = self.db_mock.session
        mock_user_rack.query.filter_by.return_value.first.return_value = None

        # Mock the _scrape_rack_page method to avoid actual HTTP requests
        with patch.object(self.parser, '_scrape_rack_page') as mock_scrape:
            mock_scrape.return_value = {
                "rack_name": "Test Rack",
                "modules": [
                    {"name": "Test Module 1", "manufacturer": "Test Manufacturer 1", "url": None},
                    {"name": "Test Module 2", "manufacturer": "Test Manufacturer 2", "url": None}
                ]
            }

            # Test with each valid URL
            for url in self.valid_urls:
                result = self.parser.parse_url(url)

                # Verify the result has the expected structure
                self.assertIn("rack_id", result)
                self.assertIn("modulargrid_id", result)
                self.assertIn("rack_name", result)
                self.assertIn("modules", result)

                # Verify the scrape method was called
                mock_scrape.assert_called()

    @patch('src.modulargrid_parser.db')
    def test_parse_url_invalid_format(self, mock_db):
        """Test parsing a URL with invalid format."""
        # Setup mocks
        mock_db.session = self.db_mock.session

        # Test with each invalid URL
        for url in self.invalid_urls:
            with self.assertRaises(ValueError):
                self.parser.parse_url(url)

    @patch('requests.get')
    def test_scrape_rack_page_success(self, mock_get):
        """Test successful scraping of a rack page."""
        # Create a mock response with sample HTML
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Test Rack - ModularGrid</title></head>
            <body>
                <h1 class="rack_title">Test Rack</h1>
                <div class="module">
                    <div class="module_name">Module 1</div>
                    <div class="manufacturer">Manufacturer 1</div>
                    <a href="/e/modules/view/1">Details</a>
                </div>
                <div class="module">
                    <div class="module_name">Module 2</div>
                    <div class="manufacturer">Manufacturer 2</div>
                    <a href="/e/modules/view/2">Details</a>
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        result = self.parser._scrape_rack_page("https://www.modulargrid.net/e/racks/view/123456")

        # Verify the result
        self.assertEqual(result["rack_name"], "Test Rack")
        self.assertEqual(len(result["modules"]), 2)
        self.assertEqual(result["modules"][0]["name"], "Module 1")
        self.assertEqual(result["modules"][0]["manufacturer"], "Manufacturer 1")
        self.assertEqual(result["modules"][1]["name"], "Module 2")
        self.assertEqual(result["modules"][1]["manufacturer"], "Manufacturer 2")

    @patch('requests.get')
    def test_scrape_rack_page_alternative_selectors(self, mock_get):
        """Test scraping with alternative selectors when standard ones fail."""
        # Create a mock response with different HTML structure
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Alternative Rack - ModularGrid</title></head>
            <body>
                <div class="modules-list">
                    <div class="module-item">
                        <h3>Alt Module 1</h3>
                        <span class="brand">Alt Manufacturer 1</span>
                    </div>
                    <div class="module-item">
                        <h3>Alt Module 2</h3>
                        <span class="brand">Alt Manufacturer 2</span>
                    </div>
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        result = self.parser._scrape_rack_page("https://www.modulargrid.net/e/racks/view/123456")

        # Verify the result contains modules despite different HTML structure
        self.assertIn("modules", result)
        self.assertGreater(len(result["modules"]), 0)

    @patch('requests.get')
    def test_scrape_rack_page_error_handling(self, mock_get):
        """Test error handling during rack page scraping."""
        # Make the request raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        # Call the method
        result = self.parser._scrape_rack_page("https://www.modulargrid.net/e/racks/view/123456")

        # Verify we get fallback data
        self.assertEqual(result["rack_name"], "Fallback Rack")
        self.assertEqual(len(result["modules"]), 3)  # Should have our 3 default modules
        self.assertEqual(result["modules"][0]["name"], "Plaits")
        self.assertEqual(result["modules"][1]["name"], "Rings")
        self.assertEqual(result["modules"][2]["name"], "Clouds")

    @patch('requests.get')
    def test_extract_module_details_success(self, mock_get):
        """Test successful extraction of module details."""
        # Create a mock response with sample HTML
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Test Module - ModularGrid</title></head>
            <body>
                <h1 class="module_name">Test Module</h1>
                <div class="manufacturer">Test Manufacturer</div>
                <div class="module_type">Oscillator</div>
                <div class="specs">
                    <dt>Width</dt>
                    <dd>12HP</dd>
                </div>
                <div class="description">This is a test module description.</div>
                <a href="/manual/test_module.pdf">Manual</a>
                <div class="module-image">
                    <img src="/images/test_module.jpg" />
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        result = self.parser._extract_module_details("https://www.modulargrid.net/e/modules/view/123")

        # Verify the result
        self.assertEqual(result["name"], "Test Module")
        self.assertEqual(result["manufacturer"], "Test Manufacturer")
        self.assertEqual(result["module_type"], "Oscillator")
        self.assertEqual(result["hp_width"], 12)
        self.assertEqual(result["description"], "This is a test module description.")
        self.assertIn("manual_url", result)
        self.assertIn("image_url", result)

    @patch('requests.get')
    def test_extract_module_details_alternative_selectors(self, mock_get):
        """Test module details extraction with alternative selectors."""
        # Create a mock response with different HTML structure
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Alt Module - ModularGrid</title></head>
            <body>
                <h1>Alt Module</h1>
                <div class="brand">Alt Manufacturer</div>
                <div class="category">Filter</div>
                <p>Width: 8HP</p>
                <div class="module-description">Alternative module description.</div>
                <a href="/docs/alt_module_guide.pdf">Documentation</a>
                <div class="product-image">
                    <img src="/images/alt_module.jpg" />
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        result = self.parser._extract_module_details("https://www.modulargrid.net/e/modules/view/456")

        # Verify the result contains details despite different HTML structure
        self.assertEqual(result["name"], "Alt Module")
        self.assertEqual(result["manufacturer"], "Alt Manufacturer")
        self.assertEqual(result["module_type"], "Filter")
        self.assertEqual(result["hp_width"], 8)
        self.assertEqual(result["description"], "Alternative module description.")

    @patch('requests.get')
    def test_extract_module_details_error_handling(self, mock_get):
        """Test error handling during module details extraction."""
        # Make the request raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        # Call the method
        result = self.parser._extract_module_details("https://www.modulargrid.net/e/modules/view/789")

        # Verify we get default values
        self.assertEqual(result["name"], "Unknown Module")
        self.assertEqual(result["manufacturer"], "Unknown Manufacturer")
        self.assertEqual(result["module_type"], "Unknown")
        self.assertEqual(result["hp_width"], 10)  # Default HP
        self.assertEqual(result["description"], "Module information could not be retrieved")
        self.assertIsNone(result["manual_url"])
        self.assertIsNone(result["image_url"])

    @patch('src.modulargrid_parser.db')
    @patch('src.modulargrid_parser.UserRack')
    @patch('src.modulargrid_parser.Module')
    @patch('src.modulargrid_parser.RackModule')
    @patch('requests.get')
    def test_integration_parse_url_to_database(self, mock_get, mock_rack_module, mock_module, mock_user_rack, mock_db):
        """Test the full integration from parsing URL to database storage."""
        # Setup mocks
        mock_db.session = self.db_mock.session
        mock_user_rack.query.filter_by.return_value.first.return_value = None

        # Create a new rack instance
        new_rack = MagicMock()
        new_rack.id = 1
        mock_user_rack.return_value = new_rack

        # Create module instances
        module1 = MagicMock()
        module1.id = 1
        module1.hp_width = 12
        module1.to_dict.return_value = {"id": 1, "name": "Module 1"}

        module2 = MagicMock()
        module2.id = 2
        module2.hp_width = 8
        module2.to_dict.return_value = {"id": 2, "name": "Module 2"}

        # Setup module query results
        mock_module.query.filter_by.return_value.first.side_effect = [None, None]  # No existing modules
        mock_module.return_value = module1  # First new module

        # Mock the _scrape_rack_page method
        with patch.object(self.parser, '_scrape_rack_page') as mock_scrape:
            mock_scrape.return_value = {
                "rack_name": "Integration Test Rack",
                "modules": [
                    {"name": "Module 1", "manufacturer": "Manufacturer 1",
                     "url": "https://www.modulargrid.net/e/modules/view/1"},
                    {"name": "Module 2", "manufacturer": "Manufacturer 2",
                     "url": "https://www.modulargrid.net/e/modules/view/2"}
                ]
            }

            # Mock the _extract_module_details method
            with patch.object(self.parser, '_extract_module_details') as mock_extract:
                mock_extract.side_effect = [
                    {
                        "name": "Module 1",
                        "manufacturer": "Manufacturer 1",
                        "hp_width": 12,
                        "module_type": "Oscillator",
                        "description": "Test description 1",
                        "manual_url": None,
                        "image_url": None,
                        "modulargrid_url": "https://www.modulargrid.net/e/modules/view/1"
                    },
                    {
                        "name": "Module 2",
                        "manufacturer": "Manufacturer 2",
                        "hp_width": 8,
                        "module_type": "Filter",
                        "description": "Test description 2",
                        "manual_url": None,
                        "image_url": None,
                        "modulargrid_url": "https://www.modulargrid.net/e/modules/view/2"
                    }
                ]

                # Call the method
                result = self.parser.parse_url("https://www.modulargrid.net/e/racks/view/123456")

                # Verify the result
                self.assertEqual(result["rack_id"], 1)
                self.assertEqual(result["rack_name"], "Integration Test Rack")

                # Verify database operations
                self.assertEqual(mock_db.session.commit.call_count, 3)  # Multiple commits expected

                # Verify module creation
                mock_module.assert_called()

                # Verify rack module creation
                mock_rack_module.assert_called()


if __name__ == '__main__':
    unittest.main()
