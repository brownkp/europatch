import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class ModularGridParser:
    """
    Parser for ModularGrid rack URLs to extract module information
    """
    
    def __init__(self, db_connector=None):
        """
        Initialize the ModularGrid parser
        
        Args:
            db_connector: Optional database connector for caching module data
        """
        self.base_url = "https://www.modulargrid.net"
        self.db_connector = db_connector
    
    def parse_rack_url(self, url):
        """
        Parse a ModularGrid rack URL and extract module information
        
        Args:
            url (str): ModularGrid rack URL
            
        Returns:
            dict: Parsed rack information
            
        Raises:
            ValueError: If URL is invalid
            Exception: If request fails
        """
        # Extract rack ID from URL
        match = re.search(r'modulargrid\.net/e/racks/view/(\d+)', url)
        if not match:
            raise ValueError("Invalid ModularGrid URL")
        
        rack_id = match.group(1)
        
        # Fetch rack page
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch ModularGrid rack: {response.status_code}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract rack name
        rack_name = soup.select_one('h1.rack_title')
        rack_name = rack_name.text.strip() if rack_name else f"Rack {rack_id}"
        
        # Extract modules
        modules = []
        module_elements = soup.select('.module')
        
        for element in module_elements:
            module_data = self._parse_module_element(element)
            if module_data:
                # Cache module data in database if connector is available
                if self.db_connector:
                    cached_module = self.db_connector.cache_module_data(module_data)
                    modules.append(cached_module)
                else:
                    modules.append(module_data)
        
        return {
            'rack_id': rack_id,
            'rack_name': rack_name,
            'modulargrid_url': url,
            'modules': modules
        }
    
    def _parse_module_element(self, element):
        """
        Parse a module element from ModularGrid HTML
        
        Args:
            element: BeautifulSoup element representing a module
            
        Returns:
            dict: Module data or None if parsing fails
        """
        # Extract module information
        module_name_elem = element.select_one('.module_name')
        manufacturer_elem = element.select_one('.manufacturer')
        
        if not module_name_elem or not manufacturer_elem:
            return None
        
        module_name = module_name_elem.text.strip()
        manufacturer = manufacturer_elem.text.strip()
        
        # Extract HP width
        hp_width = element.get('data-hp')
        hp_width = int(hp_width) if hp_width and hp_width.isdigit() else None
        
        # Extract position
        position_x = element.get('data-col')
        position_y = element.get('data-row')
        position_x = int(position_x) if position_x and position_x.isdigit() else 0
        position_y = int(position_y) if position_y and position_y.isdigit() else 0
        
        # Extract image URL
        image_elem = element.select_one('img')
        image_url = image_elem.get('src') if image_elem else None
        if image_url and not image_url.startswith('http'):
            image_url = f"{self.base_url}{image_url}"
        
        # Extract module URL
        module_url_elem = element.select_one('a.module_url')
        module_url = module_url_elem.get('href') if module_url_elem else None
        if module_url and not module_url.startswith('http'):
            module_url = f"{self.base_url}{module_url}"
        
        # Determine module type
        module_type = self._determine_module_type(element, module_name)
        
        return {
            'name': module_name,
            'manufacturer': manufacturer,
            'hp_width': hp_width,
            'module_type': module_type,
            'image_url': image_url,
            'modulargrid_url': module_url,
            'position_x': position_x,
            'position_y': position_y,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    def _determine_module_type(self, element, module_name):
        """
        Determine module type based on class or name
        
        Args:
            element: BeautifulSoup element representing a module
            module_name (str): Name of the module
            
        Returns:
            str: Module type
        """
        module_name_lower = module_name.lower()
        element_classes = element.get('class', [])
        
        # Check element classes first
        if 'vco' in element_classes or 'oscillator' in element_classes:
            return 'VCO'
        elif 'vcf' in element_classes or 'filter' in element_classes:
            return 'VCF'
        elif 'vca' in element_classes or 'amplifier' in element_classes:
            return 'VCA'
        elif 'envelope' in element_classes or 'adsr' in element_classes:
            return 'Envelope'
        elif 'lfo' in element_classes:
            return 'LFO'
        elif 'sequencer' in element_classes:
            return 'Sequencer'
        elif 'effect' in element_classes or 'fx' in element_classes:
            return 'Effect'
        elif 'mixer' in element_classes:
            return 'Mixer'
        elif 'utility' in element_classes:
            return 'Utility'
        
        # Then check module name
        if 'vco' in module_name_lower or 'oscillator' in module_name_lower:
            return 'VCO'
        elif 'vcf' in module_name_lower or 'filter' in module_name_lower:
            return 'VCF'
        elif 'vca' in module_name_lower or 'amplifier' in module_name_lower:
            return 'VCA'
        elif 'envelope' in module_name_lower or 'adsr' in module_name_lower:
            return 'Envelope'
        elif 'lfo' in module_name_lower:
            return 'LFO'
        elif 'sequencer' in module_name_lower:
            return 'Sequencer'
        elif 'effect' in module_name_lower or 'fx' in module_name_lower or 'reverb' in module_name_lower or 'delay' in module_name_lower:
            return 'Effect'
        elif 'mixer' in module_name_lower:
            return 'Mixer'
        elif 'utility' in module_name_lower or 'mult' in module_name_lower or 'attenuator' in module_name_lower:
            return 'Utility'
        else:
            return 'Other'


# Example usage
if __name__ == "__main__":
    parser = ModularGridParser()
    try:
        rack_data = parser.parse_rack_url("https://www.modulargrid.net/e/racks/view/123456")
        print(f"Rack: {rack_data['rack_name']}")
        print(f"Modules found: {len(rack_data['modules'])}")
        
        for module in rack_data['modules']:
            print(f"- {module['manufacturer']} {module['name']} ({module['module_type']}, {module['hp_width']}HP)")
    except Exception as e:
        print(f"Error: {e}")
