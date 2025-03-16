"""
Module for parsing ModularGrid rack URLs and extracting module information.
"""
import re
import requests
from bs4 import BeautifulSoup
import logging
from src.models import db, Module, ModuleConnection, ModuleControl, UserRack, RackModule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModularGridParser:
    """
    Parser for ModularGrid rack URLs to extract module information.
    """
    
    def __init__(self):
        """Initialize the ModularGrid parser."""
        self.base_url = "https://www.modulargrid.net"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def parse_url(self, url):
        """
        Parse a ModularGrid rack URL and extract module information.
        
        Args:
            url (str): ModularGrid rack URL
            
        Returns:
            dict: Rack information including modules
        """
        logger.info(f"Parsing ModularGrid URL: {url}")
        
        # Extract rack ID from URL
        rack_id_match = re.search(r'/racks/view/(\d+)', url)
        if not rack_id_match:
            raise ValueError("Invalid ModularGrid URL format. Expected format: https://www.modulargrid.net/e/racks/view/123456")
        
        rack_id = rack_id_match.group(1)
        logger.info(f"Extracted rack ID: {rack_id}")
        
        # Check if rack already exists in database
        existing_rack = UserRack.query.filter_by(modulargrid_id=rack_id).first()
        if existing_rack:
            logger.info(f"Rack {rack_id} already exists in database, returning cached data")
            return {
                "rack_id": existing_rack.id,
                "modulargrid_id": existing_rack.modulargrid_id,
                "rack_name": existing_rack.rack_name,
                "modules": [rm.module.to_dict() for rm in existing_rack.modules]
            }
        
        # For this mock implementation, we'll return some fake data
        # In a real implementation, this would scrape the ModularGrid page
        
        # Create a new rack in the database
        new_rack = UserRack(
            modulargrid_url=url,
            modulargrid_id=rack_id,
            rack_name=f"Rack {rack_id}"
        )
        db.session.add(new_rack)
        db.session.commit()
        
        # Get some modules from the database to add to the rack
        modules = Module.query.limit(5).all()
        
        # Add modules to the rack
        for i, module in enumerate(modules):
            rack_module = RackModule(
                rack_id=new_rack.id,
                module_id=module.id,
                position_x=i * module.hp_width,
                position_y=0
            )
            db.session.add(rack_module)
        
        db.session.commit()
        
        # Return rack information
        return {
            "rack_id": new_rack.id,
            "modulargrid_id": new_rack.modulargrid_id,
            "rack_name": new_rack.rack_name,
            "modules": [module.to_dict() for module in modules]
        }
    
    def _scrape_rack_page(self, url):
        """
        Scrape a ModularGrid rack page to extract module information.
        
        Args:
            url (str): ModularGrid rack URL
            
        Returns:
            dict: Rack information including modules
        """
        # In a real implementation, this would scrape the ModularGrid page
        # For this mock implementation, we'll return some fake data
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract rack name
            rack_name_elem = soup.select_one('h1.rack_title')
            rack_name = rack_name_elem.text.strip() if rack_name_elem else "Unnamed Rack"
            
            # Extract modules
            modules = []
            module_elems = soup.select('.module')
            
            for module_elem in module_elems:
                # Extract module information
                name_elem = module_elem.select_one('.module_name')
                manufacturer_elem = module_elem.select_one('.manufacturer')
                
                if name_elem and manufacturer_elem:
                    module_name = name_elem.text.strip()
                    manufacturer = manufacturer_elem.text.strip()
                    
                    # Extract module URL
                    module_url = None
                    link_elem = name_elem.select_one('a')
                    if link_elem and 'href' in link_elem.attrs:
                        module_url = self.base_url + link_elem['href']
                    
                    modules.append({
                        "name": module_name,
                        "manufacturer": manufacturer,
                        "url": module_url
                    })
            
            return {
                "rack_name": rack_name,
                "modules": modules
            }
            
        except Exception as e:
            logger.error(f"Error scraping ModularGrid page: {str(e)}")
            raise
    
    def _extract_module_details(self, module_url):
        """
        Extract detailed information about a module from its ModularGrid page.
        
        Args:
            module_url (str): ModularGrid module URL
            
        Returns:
            dict: Module details
        """
        # In a real implementation, this would scrape the ModularGrid module page
        # For this mock implementation, we'll return some fake data
        
        try:
            response = requests.get(module_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract module details
            name_elem = soup.select_one('h1.module_name')
            name = name_elem.text.strip() if name_elem else "Unknown Module"
            
            manufacturer_elem = soup.select_one('.manufacturer')
            manufacturer = manufacturer_elem.text.strip() if manufacturer_elem else "Unknown Manufacturer"
            
            # Extract HP width
            hp_width = None
            specs_elems = soup.select('.specs dt, .specs dd')
            for i in range(0, len(specs_elems), 2):
                if i + 1 < len(specs_elems) and 'Width' in specs_elems[i].text:
                    hp_width_text = specs_elems[i + 1].text.strip()
                    hp_width_match = re.search(r'(\d+)HP', hp_width_text)
                    if hp_width_match:
                        hp_width = int(hp_width_match.group(1))
                    break
            
            # Extract module type
            module_type = None
            type_elem = soup.select_one('.module_type')
            if type_elem:
                module_type = type_elem.text.strip()
            
            # Extract description
            description = None
            description_elem = soup.select_one('.description')
            if description_elem:
                description = description_elem.text.strip()
            
            # Extract manual URL
            manual_url = None
            links = soup.select('a')
            for link in links:
                if 'href' in link.attrs and 'manual' in link.text.lower():
                    manual_url = link['href']
                    if not manual_url.startswith('http'):
                        manual_url = self.base_url + manual_url
                    break
            
            return {
                "name": name,
                "manufacturer": manufacturer,
                "hp_width": hp_width,
                "module_type": module_type,
                "description": description,
                "manual_url": manual_url,
                "modulargrid_url": module_url
            }
            
        except Exception as e:
            logger.error(f"Error extracting module details: {str(e)}")
            raise
