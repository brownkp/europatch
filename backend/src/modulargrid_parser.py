"""
Module for parsing ModularGrid rack URLs and extracting module information.
"""
import re
import requests
import json
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

        # Scrape the ModularGrid page to get rack information
        try:
            # Construct the full URL if needed
            if not url.startswith('http'):
                url = f"{self.base_url}/e/racks/view/{rack_id}"

            # Scrape the rack page
            rack_data = self._scrape_rack_page(url)

            # Create a new rack in the database
            new_rack = UserRack(
                modulargrid_url=url,
                modulargrid_id=rack_id,
                rack_name=rack_data["rack_name"]
            )
            db.session.add(new_rack)
            db.session.commit()

            # Process each module from the scraped data
            modules_data = []
            for module_info in rack_data["modules"]:
                # Check if module already exists in database by name and manufacturer
                existing_module = Module.query.filter_by(
                    name=module_info["name"],
                    manufacturer=module_info["manufacturer"]
                ).first()

                if existing_module:
                    module = existing_module
                else:
                    # If module has a URL, extract detailed information
                    module_details = {}
                    if module_info.get("url"):
                        try:
                            module_details = self._extract_module_details(module_info["url"])
                        except Exception as e:
                            logger.warning(f"Error extracting details for module {module_info['name']}: {str(e)}")

                    # Create new module with available information
                    module = Module(
                        name=module_info["name"],
                        manufacturer=module_info["manufacturer"],
                        module_type=module_details.get("module_type", "Unknown"),
                        hp_width=module_details.get("hp_width", 10),  # Default to 10HP if unknown
                        description=module_details.get("description", f"{module_info['name']} by {module_info['manufacturer']}"),
                        manual_url=module_details.get("manual_url"),
                        modulargrid_url=module_info.get("url")
                    )
                    db.session.add(module)
                    db.session.commit()

                # Add module to rack
                position_x = len(modules_data) * (module.hp_width or 10)  # Use module width or default to 10HP
                rack_module = RackModule(
                    rack_id=new_rack.id,
                    module_id=module.id,
                    position_x=position_x,
                    position_y=0
                )
                db.session.add(rack_module)

                modules_data.append(module)

            db.session.commit()

            # Return rack information
            return {
                "rack_id": new_rack.id,
                "modulargrid_id": new_rack.modulargrid_id,
                "rack_name": new_rack.rack_name,
                "modules": [module.to_dict() for module in modules_data]
            }

        except Exception as e:
            # Log the error and roll back any database changes
            logger.error(f"Error parsing ModularGrid URL: {str(e)}")
            db.session.rollback()

            # If scraping fails, create a rack with default modules as fallback
            logger.info("Falling back to default modules")

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

            # If no modules exist in the database, create some default ones
            if not modules:
                default_modules = []

                for mod_data in default_modules:
                    module = Module(
                        name=mod_data["name"],
                        manufacturer=mod_data["manufacturer"],
                        module_type=mod_data["type"],
                        hp_width=mod_data["hp"],
                        description=mod_data["description"]
                    )
                    db.session.add(module)
                    modules.append(module)

                db.session.commit()

            # Add modules to the rack
            for i, module in enumerate(modules):
                rack_module = RackModule(
                    rack_id=new_rack.id,
                    module_id=module.id,
                    position_x=i * (module.hp_width or 10),
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
        try:
            logger.info(f"Scraping ModularGrid page: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract rack name
            rack_name_elem = soup.select_one('h1.rack_title')
            if not rack_name_elem:
                rack_name_elem = soup.select_one('title')
            rack_name = rack_name_elem.text.strip() if rack_name_elem else "Unnamed Rack"

            # Clean up rack name if needed
            if "ModularGrid Rack" in rack_name:
                rack_name = rack_name.replace("ModularGrid Rack", "").strip()

            # Extract modules using JSON data
            modules = []

            try:
                # Find the script tag with the JSON data
                json_script = soup.find('script', {'type': 'application/json', 'data-mg-json': 'rtd'})

                if json_script:
                    logger.info("Found JSON data in the page")
                    # Parse the JSON data
                    rack_data = json.loads(json_script.text)

                    # Extract modules from the JSON data based on the provided structure
                    if 'rack' in rack_data and 'Module' in rack_data['rack']:
                        module_list = rack_data['rack']['Module']
                        logger.info(f"Found {len(module_list)} modules in JSON data")

                        for module_data in module_list:
                            module_name = module_data.get('name', 'Unknown Module')

                            # Get manufacturer from Vendor object if available
                            manufacturer = "Unknown Manufacturer"
                            if 'Vendor' in module_data and 'name' in module_data['Vendor']:
                                manufacturer = module_data['Vendor']['name']

                            # Construct module URL if we have an ID and slug
                            module_url = None
                            if 'id' in module_data and 'slug' in module_data:
                                module_url = f"{self.base_url}/e/modules/view/{module_data['id']}/{module_data['slug']}"

                            # Extract all available fields
                            module_info = {
                                "name": module_name,
                                "manufacturer": manufacturer,
                                "url": module_url,
                                "id": module_data.get('id'),
                                "slug": module_data.get('slug'),
                                "hp_width": module_data.get('te'),
                                "description": module_data.get('description'),
                                "depth": module_data.get('depth'),
                                "price_eur": module_data.get('price_eur'),
                                "price_usd": module_data.get('price_usd'),
                                "price_base": module_data.get('price_base'),
                                "current_5v": module_data.get('current5v'),
                                "current_plus": module_data.get('current_plus'),
                                "current_min": module_data.get('current_min'),
                                "is_passive": module_data.get('is_passive'),
                                "is_1u": module_data.get('is_1u'),
                                "module_type": module_data.get('description', '').split(' ', 1)[0] if module_data.get('description') else 'Unknown'
                            }

                            # Add position information if available
                            if 'ModulesRack' in module_data:
                                module_info.update({
                                    "position_row": module_data['ModulesRack'].get('row'),
                                    "position_col": module_data['ModulesRack'].get('col'),
                                    "orientation": module_data['ModulesRack'].get('orientation')
                                })

                            # Add image information if available
                            if 'Version' in module_data and len(module_data['Version']) > 0:
                                first_version = module_data['Version'][0]
                                if 'imageid' in first_version and 'imagehash' in first_version:
                                    module_info["image_url"] = f"{self.base_url}/images/modules/large/{first_version['imageid']}.jpg"

                            modules.append(module_info)
                    else:
                        logger.warning("No modules found in JSON data")
                else:
                    logger.warning("No JSON data found in the page, falling back to HTML parsing")
                    # Fall back to the original HTML parsing method if JSON data is not available

                    # Try different selectors for modules as the site structure might change
                    module_selectors = ['.module', '.modules .module-item', '.modules-list .module']
                    module_elems = []

                    for selector in module_selectors:
                        module_elems = soup.select(selector)
                        if module_elems:
                            logger.info(f"Found {len(module_elems)} modules using selector: {selector}")
                            break

                    # If no modules found with selectors, try a more generic approach
                    if not module_elems:
                        logger.info("No modules found with standard selectors, trying alternative approach")
                        # Look for divs with manufacturer and module name patterns
                        potential_modules = soup.find_all(['div', 'li'], class_=lambda c: c and ('module' in c.lower()))
                        module_elems = [m for m in potential_modules if m.find(text=lambda t: t and len(t.strip()) > 0)]

                    logger.info(f"Found {len(module_elems)} potential modules")

                    for module_elem in module_elems:
                        # Try different selectors for module name and manufacturer
                        name_elem = None
                        manufacturer_elem = None

                        # Try different selectors for module name
                        for name_selector in ['.module_name', '.name', 'h3', 'h4', 'strong']:
                            name_elem = module_elem.select_one(name_selector)
                            if name_elem and name_elem.text.strip():
                                break

                        # Try different selectors for manufacturer
                        for mfg_selector in ['.manufacturer', '.brand', '.maker', 'em', 'span']:
                            manufacturer_elem = module_elem.select_one(mfg_selector)
                            if manufacturer_elem and manufacturer_elem.text.strip():
                                break

                        # If we couldn't find structured elements, try to extract from text
                        if not name_elem or not manufacturer_elem:
                            text = module_elem.get_text(separator=' ', strip=True)
                            if ' by ' in text:
                                parts = text.split(' by ', 1)
                                module_name = parts[0].strip()
                                manufacturer = parts[1].strip()
                            else:
                                # Make a best guess
                                words = text.split()
                                if len(words) >= 2:
                                    manufacturer = words[0]
                                    module_name = ' '.join(words[1:])
                                else:
                                    module_name = text
                                    manufacturer = "Unknown"
                        else:
                            module_name = name_elem.text.strip()
                            manufacturer = manufacturer_elem.text.strip()

                        # Extract module URL if available
                        module_url = None
                        link_elem = module_elem.find('a')
                        if link_elem and 'href' in link_elem.attrs:
                            href = link_elem['href']
                            if href.startswith('/'):
                                module_url = self.base_url + href
                            elif href.startswith('http'):
                                module_url = href

                        # Only add if we have at least a name
                        if module_name:
                            modules.append({
                                "name": module_name,
                                "manufacturer": manufacturer,
                                "url": module_url
                            })
            except Exception as e:
                logger.error(f"Error extracting modules from JSON: {str(e)}")
                logger.info("Falling back to HTML parsing method")

                # Fall back to the original HTML parsing method
                # Try different selectors for modules as the site structure might change
                module_selectors = ['.module', '.modules .module-item', '.modules-list .module']
                module_elems = []

                for selector in module_selectors:
                    module_elems = soup.select(selector)
                    if module_elems:
                        logger.info(f"Found {len(module_elems)} modules using selector: {selector}")
                        break

                # If no modules found with selectors, try a more generic approach
                if not module_elems:
                    logger.info("No modules found with standard selectors, trying alternative approach")
                    # Look for divs with manufacturer and module name patterns
                    potential_modules = soup.find_all(['div', 'li'], class_=lambda c: c and ('module' in c.lower()))
                    module_elems = [m for m in potential_modules if m.find(text=lambda t: t and len(t.strip()) > 0)]

                logger.info(f"Found {len(module_elems)} potential modules")

                for module_elem in module_elems:
                    # Process each module element as in the original code
                    name_elem = None
                    manufacturer_elem = None

                    # Try different selectors for module name
                    for name_selector in ['.module_name', '.name', 'h3', 'h4', 'strong']:
                        name_elem = module_elem.select_one(name_selector)
                        if name_elem and name_elem.text.strip():
                            break

                    # Try different selectors for manufacturer
                    for mfg_selector in ['.manufacturer', '.brand', '.maker', 'em', 'span']:
                        manufacturer_elem = module_elem.select_one(mfg_selector)
                        if manufacturer_elem and manufacturer_elem.text.strip():
                            break

                    # Extract name and manufacturer
                    if not name_elem or not manufacturer_elem:
                        text = module_elem.get_text(separator=' ', strip=True)
                        if ' by ' in text:
                            parts = text.split(' by ', 1)
                            module_name = parts[0].strip()
                            manufacturer = parts[1].strip()
                        else:
                            # Make a best guess
                            words = text.split()
                            if len(words) >= 2:
                                manufacturer = words[0]
                                module_name = ' '.join(words[1:])
                            else:
                                module_name = text
                                manufacturer = "Unknown"
                    else:
                        module_name = name_elem.text.strip()
                        manufacturer = manufacturer_elem.text.strip()

                    # Extract module URL if available
                    module_url = None
                    link_elem = module_elem.find('a')
                    if link_elem and 'href' in link_elem.attrs:
                        href = link_elem['href']
                        if href.startswith('/'):
                            module_url = self.base_url + href
                        elif href.startswith('http'):
                            module_url = href

                    # Only add if we have at least a name
                    if module_name:
                        modules.append({
                            "name": module_name,
                            "manufacturer": manufacturer,
                            "url": module_url
                        })

            logger.info(f"Successfully extracted {len(modules)} modules from rack")

            # If we couldn't find any modules, raise an exception
            if not modules:
                raise ValueError("No modules found in the ModularGrid rack")

            return {
                "rack_name": rack_name,
                "modules": modules
            }

        except Exception as e:
            logger.error(f"Error scraping ModularGrid page: {str(e)}")
            # Create a fallback response with default modules
            return {
                "rack_name": f"Error scraping ModularGrid page: {str(e)}",
                "modules": []
            }

    def _extract_module_details(self, module_url):
        """
        Extract detailed information about a module from its ModularGrid page.

        Args:
            module_url (str): ModularGrid module URL

        Returns:
            dict: Module details
        """
        try:
            logger.info(f"Extracting details from module page: {module_url}")
            response = requests.get(module_url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract module details with multiple selector attempts
            # Extract module name
            name = "Unknown Module"
            for name_selector in ['h1.module_name', 'h1.name', 'h1', '.module-header h2', 'title']:
                name_elem = soup.select_one(name_selector)
                if name_elem and name_elem.text.strip():
                    name = name_elem.text.strip()
                    # Clean up name if it contains "ModularGrid"
                    if "ModularGrid" in name:
                        name = re.sub(r'ModularGrid.*?:', '', name).strip()
                    break

            # Extract manufacturer
            manufacturer = "Unknown Manufacturer"
            for mfg_selector in ['.manufacturer', '.brand', '.maker', '.module-header .company', 'h2.manufacturer']:
                manufacturer_elem = soup.select_one(mfg_selector)
                if manufacturer_elem and manufacturer_elem.text.strip():
                    manufacturer = manufacturer_elem.text.strip()
                    break

            # Extract HP width with multiple approaches
            hp_width = None

            # Approach 1: Look for specs table
            specs_selectors = ['.specs dt, .specs dd', '.specifications dt, .specifications dd', '.module-specs dt, .module-specs dd']
            for selector in specs_selectors:
                specs_elems = soup.select(selector)
                if specs_elems:
                    for i in range(0, len(specs_elems), 2):
                        if i + 1 < len(specs_elems) and ('Width' in specs_elems[i].text or 'HP' in specs_elems[i].text):
                            hp_width_text = specs_elems[i + 1].text.strip()
                            hp_width_match = re.search(r'(\d+)\s*HP', hp_width_text, re.IGNORECASE)
                            if hp_width_match:
                                hp_width = int(hp_width_match.group(1))
                                break
                    if hp_width:
                        break

            # Approach 2: Look for HP in any text
            if not hp_width:
                hp_pattern = re.compile(r'(\d+)\s*HP', re.IGNORECASE)
                for elem in soup.find_all(['p', 'div', 'span', 'li']):
                    if 'width' in elem.text.lower() or 'hp' in elem.text.lower():
                        match = hp_pattern.search(elem.text)
                        if match:
                            hp_width = int(match.group(1))
                            break

            # Default HP if not found
            if not hp_width:
                hp_width = 10  # Default to 10HP if not found

            # Extract module type
            module_type = "Unknown"
            type_selectors = ['.module_type', '.type', '.category', '.module-category']
            for selector in type_selectors:
                type_elem = soup.select_one(selector)
                if type_elem and type_elem.text.strip():
                    module_type = type_elem.text.strip()
                    break

            # If no specific type element found, try to infer from page content
            if module_type == "Unknown":
                type_keywords = {
                    "Oscillator": ["vco", "oscillator", "sound generator"],
                    "Filter": ["vcf", "filter", "lowpass", "highpass", "bandpass"],
                    "Envelope": ["envelope", "adsr", "eg", "envelope generator"],
                    "LFO": ["lfo", "low frequency"],
                    "VCA": ["vca", "amplifier"],
                    "Sequencer": ["sequencer", "sequence", "step sequencer"],
                    "Utility": ["utility", "attenuator", "mixer", "multiple"],
                    "Effect": ["effect", "reverb", "delay", "chorus", "flanger"]
                }

                page_text = soup.get_text().lower()
                for type_name, keywords in type_keywords.items():
                    if any(keyword in page_text for keyword in keywords):
                        module_type = type_name
                        break

            # Extract description
            description = None
            description_selectors = ['.description', '.module-description', '.product-description', '.about']
            for selector in description_selectors:
                description_elem = soup.select_one(selector)
                if description_elem and description_elem.text.strip():
                    description = description_elem.text.strip()
                    break

            # If no description found, use a generic one
            if not description:
                description = f"{name} by {manufacturer}"

            # Extract manual URL
            manual_url = None
            # Look for links containing "manual" or "documentation"
            manual_keywords = ["manual", "documentation", "guide", "instructions", "pdf"]
            links = soup.find_all('a')
            for link in links:
                link_text = link.text.lower()
                if 'href' in link.attrs and any(keyword in link_text for keyword in manual_keywords):
                    manual_url = link['href']
                    if not manual_url.startswith('http'):
                        manual_url = self.base_url + manual_url
                    break

            # Extract image URL
            image_url = None
            image_selectors = ['.module-image img', '.product-image img', '.main-image img', '.module img']
            for selector in image_selectors:
                img_elem = soup.select_one(selector)
                if img_elem and 'src' in img_elem.attrs:
                    image_url = img_elem['src']
                    if not image_url.startswith('http'):
                        image_url = self.base_url + image_url
                    break

            return {
                "name": name,
                "manufacturer": manufacturer,
                "hp_width": hp_width,
                "module_type": module_type,
                "description": description,
                "manual_url": manual_url,
                "image_url": image_url,
                "modulargrid_url": module_url
            }

        except Exception as e:
            logger.error(f"Error extracting module details: {str(e)}")
            # Return basic information instead of raising an exception
            return {
                "name": "Unknown Module",
                "manufacturer": "Unknown Manufacturer",
                "hp_width": 10,  # Default to 10HP
                "module_type": "Unknown",
                "description": "Module information could not be retrieved",
                "manual_url": None,
                "image_url": None,
                "modulargrid_url": module_url
            }
