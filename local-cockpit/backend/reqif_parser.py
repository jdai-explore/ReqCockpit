#!/usr/bin/env python3
"""
ReqIF Parser Module

A comprehensive ReqIF (Requirements Interchange Format) parser that maintains the original
file structure without artificial field mapping. This implementation is optimized for
handling various ReqIF file versions and includes robust error handling and namespace support.

Key Features:
- Preserves original ReqIF structure and attributes
- Handles both .reqif and .reqifz (zipped) file formats
- Supports XML namespaces and various ReqIF versions
- Extracts and resolves references between requirements
- Provides detailed parsing statistics and diagnostics
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Callable
import os
import zipfile
import tempfile
import shutil
import re
import html


class ReqIFParser:
    """
    A robust parser for ReqIF (Requirements Interchange Format) files.

    This parser is designed to maintain the original structure of ReqIF files while providing
    convenient access to requirements data. It handles various ReqIF versions, namespaces,
    and complex reference structures.

    Attributes:
        root_namespace (str): The root XML namespace of the parsed ReqIF file
        namespace_uri (str): The full namespace URI for ReqIF elements
        ns_prefix (str): The namespace prefix used in the XML (default: 'reqif')
        attribute_definitions (dict): Maps attribute definition IDs to their properties
        spec_object_types (dict): Maps specification object type IDs to their definitions
        enumeration_definitions (dict): Maps enumeration type IDs to their definitions
        enum_values (dict): Maps enumeration value IDs to their human-readable names
        stats (dict): Tracks parsing statistics and metrics
    """

    def __init__(self):
        # Namespace handling
        self.root_namespace = None
        self.namespace_uri = None
        self.ns_prefix = "reqif"

        # Comprehensive catalogs
        self.attribute_definitions = {}      # ID -> definition info
        self.spec_object_types = {}         # ID -> type info
        self.enumeration_definitions = {}   # ID -> enum info
        self.enum_values = {}               # ID -> human readable name

        # Statistics for debugging
        self.stats = {
            'elements_found': {},
            'definitions_cataloged': 0,
            'types_cataloged': 0,
            'spec_objects_processed': 0,
            'successful_resolutions': 0,
            'content_extractions': 0
        }

    def parse_multiple_files(self, file_paths: List[str], progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Parse multiple ReqIF files with progress reporting and error collection.

        Args:
            file_paths: A list of paths to ReqIF files or archives.
            progress_callback: A function to call with progress updates.
                               It receives (current_index, total_files, file_path).

        Returns:
            A dictionary containing results and errors.
            {
                'results': { 'file_path_1': [req1, req2], ... },
                'errors': { 'file_path_2': 'Error message', ... },
                'summary': { 'total_files': X, 'successful': Y, 'failed': Z }
            }
        """
        results = {}
        errors = {}
        total_files = len(file_paths)

        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(i, total_files, file_path)

            try:
                requirements = self.parse_file(file_path)
                results[file_path] = requirements
            except Exception as e:
                errors[file_path] = str(e)

        if progress_callback:
            progress_callback(total_files, total_files, "Completed")

        summary = {
            'total_files': total_files,
            'successful': len(results),
            'failed': len(errors)
        }

        return {
            'results': results,
            'errors': errors,
            'summary': summary
        }

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse ReqIF file with enhanced namespace handling and content extraction

        Args:
            file_path: Path to the ReqIF file or ReqIF archive

        Returns:
            List of requirement dictionaries with only actual ReqIF content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ReqIF file not found: {file_path}")

        # Reset state for new parsing
        self._reset_parser_state()

        temp_dir_to_clean = None
        try:
            # Handle ReqIFZ archives
            if file_path.lower().endswith('.reqifz'):
                actual_file_path, temp_dir_to_clean = self._extract_reqifz(file_path)
            else:
                actual_file_path = file_path

            # Parse XML and setup namespace handling
            tree = ET.parse(actual_file_path)
            root = tree.getroot()

            # Setup robust namespace handling
            self._setup_namespace_handling(root)

            # Build comprehensive definition catalogs
            self._build_comprehensive_catalogs(root)

            # Extract SPEC-OBJECTs with enhanced resolution
            requirements = self._extract_spec_objects_enhanced(root)

            return requirements

        except Exception as e:
            raise RuntimeError(f"Failed to parse ReqIF file: {str(e)}")
        finally:
            if temp_dir_to_clean:
                shutil.rmtree(temp_dir_to_clean, ignore_errors=True)

    def _reset_parser_state(self):
        """Reset all parser state for new file"""
        self.root_namespace = None
        self.namespace_uri = None
        self.attribute_definitions.clear()
        self.spec_object_types.clear()
        self.enumeration_definitions.clear()
        self.enum_values.clear()

        self.stats = {
            'elements_found': {},
            'definitions_cataloged': 0,
            'types_cataloged': 0,
            'spec_objects_processed': 0,
            'successful_resolutions': 0,
            'content_extractions': 0
        }

    def _extract_reqifz(self, file_path: str) -> (str, str):
        """Extract ReqIFZ archive and return path to main ReqIF file and temp dir"""
        temp_dir = tempfile.mkdtemp()

        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find largest .reqif file
            reqif_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.reqif'):
                        full_path = os.path.join(root, file)
                        size = os.path.getsize(full_path)
                        reqif_files.append((full_path, size))

            if not reqif_files:
                raise ValueError("No .reqif files found in archive")

            # Return path to largest file
            main_reqif = max(reqif_files, key=lambda x: x[1])[0]
            return main_reqif, temp_dir

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

    def _setup_namespace_handling(self, root):
        """Setup robust namespace handling for ReqIF files with full namespace URIs"""
        # Extract namespace from root tag
        if '}' in root.tag:
            self.namespace_uri = root.tag.split('}')[0][1:]  # Remove { }
            self.root_namespace = f"{{{self.namespace_uri}}}"

            # Register namespace for XPath queries
            try:
                ET.register_namespace(self.ns_prefix, self.namespace_uri)
            except:
                pass  # Ignore registration errors
        else:
            self.root_namespace = ""
            self.namespace_uri = None

    def _build_comprehensive_catalogs(self, root):
        """Build comprehensive catalogs with namespace awareness"""
        # Build attribute definition catalog
        self._build_attribute_definition_catalog(root)

        # Build enumeration catalog
        self._build_enumeration_catalog(root)

        # Build spec object type catalog
        self._build_spec_object_type_catalog(root)

        # Update statistics
        self.stats['definitions_cataloged'] = len(self.attribute_definitions)
        self.stats['types_cataloged'] = len(self.spec_object_types)

    def _build_attribute_definition_catalog(self, root):
        """
        Build a comprehensive catalog of all attribute definitions in the ReqIF file.

        This method processes all attribute definition types (string, xhtml, enum, etc.)
        and stores their metadata for later reference during requirement processing.

        Args:
            root: The root element of the parsed ReqIF XML document

        Side Effects:
            Populates self.attribute_definitions with all found attribute definitions
            Updates self.stats with element count information
        """
        # List of all possible attribute definition types in ReqIF standard
        definition_types = [
            'ATTRIBUTE-DEFINITION-STRING',      # Simple string attributes
            'ATTRIBUTE-DEFINITION-XHTML',       # Rich text content
            'ATTRIBUTE-DEFINITION-ENUMERATION', # Enumerated values
            'ATTRIBUTE-DEFINITION-INTEGER',     # Integer numbers
            'ATTRIBUTE-DEFINITION-REAL',        # Floating point numbers
            'ATTRIBUTE-DEFINITION-DATE',        # Date values
            'ATTRIBUTE-DEFINITION-BOOLEAN'      # True/False values
        ]

        for def_type in definition_types:
            elements = self._find_elements_namespace_aware(root, def_type)
            self.stats['elements_found'][def_type] = len(elements)

            for elem in elements:
                identifier = self._extract_identifier(elem)
                if identifier:
                    long_name = self._extract_long_name(elem) or identifier

                    # Store attribute definition with normalized data type and reference to original element
                    self.attribute_definitions[identifier] = {
                        'identifier': identifier,  # Unique identifier of the attribute
                        'long_name': long_name,    # Human-readable name
                        'data_type': def_type.replace('ATTRIBUTE-DEFINITION-', '').lower(),  # Normalized type
                        'element': elem            # Reference to original XML element
                    }

    def _build_enumeration_catalog(self, root):
        """Build enumeration catalog with namespace awareness"""
        enum_defs = self._find_elements_namespace_aware(root, 'DATATYPE-DEFINITION-ENUMERATION')

        for enum_def in enum_defs:
            enum_id = self._extract_identifier(enum_def)
            if not enum_id:
                continue

            enum_name = self._extract_long_name(enum_def) or enum_id

            self.enumeration_definitions[enum_id] = {
                'identifier': enum_id,
                'long_name': enum_name,
                'values': {}
            }

            # Find enum values with namespace awareness
            enum_values = self._find_elements_namespace_aware(enum_def, 'SPECIFIED-VALUES')

            for val in enum_values:
                # Find ENUM-VALUE elements
                enum_value_elements = self._find_elements_namespace_aware(val, 'ENUM-VALUE')
                for enum_value in enum_value_elements:
                    val_id = self._extract_identifier(enum_value)
                    val_name = self._extract_long_name(enum_value) or val_id

                    if val_id:
                        self.enum_values[val_id] = val_name
                        self.enumeration_definitions[enum_id]['values'][val_id] = val_name

    def _build_spec_object_type_catalog(self, root):
        """Build spec object type catalog with namespace awareness"""
        spec_types = self._find_elements_namespace_aware(root, 'SPEC-OBJECT-TYPE')

        for spec_type in spec_types:
            type_id = self._extract_identifier(spec_type)
            if not type_id:
                continue

            type_name = self._extract_long_name(spec_type) or type_id

            self.spec_object_types[type_id] = {
                'identifier': type_id,
                'long_name': type_name,
                'element': spec_type
            }

    def _extract_spec_objects_enhanced(self, root) -> List[Dict[str, Any]]:
        """Extract SPEC-OBJECTs with enhanced resolution"""
        spec_objects = self._find_elements_namespace_aware(root, 'SPEC-OBJECT')
        self.stats['elements_found']['SPEC-OBJECT'] = len(spec_objects)

        requirements = []

        for i, spec_obj in enumerate(spec_objects):
            try:
                requirement = self._process_single_spec_object(spec_obj, i)
                if requirement:
                    requirements.append(requirement)
                    self.stats['successful_resolutions'] += 1

                self.stats['spec_objects_processed'] += 1

            except Exception:
                # Skip problematic spec objects but continue processing
                continue

        return requirements

    def _process_single_spec_object(self, spec_obj, index: int) -> Optional[Dict[str, Any]]:
        """Process a single SPEC-OBJECT with NO artificial field mapping"""
        # Extract basic info
        req_id = self._extract_identifier(spec_obj) or f"REQ_{index}"
        req_identifier = self._extract_identifier(spec_obj)

        # Initialize requirement with ONLY actual ReqIF data
        requirement = {
            'id': req_id,
            'attributes': {},
            'raw_attributes': {}
        }

        # Add identifier only if it exists and is different from id
        if req_identifier and req_identifier != req_id:
            requirement['identifier'] = req_identifier

        # Resolve type reference (only if exists)
        type_ref = self._extract_type_reference_enhanced(spec_obj)
        if type_ref and type_ref in self.spec_object_types:
            requirement['type'] = self.spec_object_types[type_ref]['long_name']
        elif type_ref:
            requirement['type'] = type_ref

        # Extract attribute values (the core ReqIF data)
        self._extract_attribute_values_enhanced(spec_obj, requirement)

        # Create content hash for comparison
        requirement['content'] = self._create_content_hash(requirement)

        return requirement

    def _extract_type_reference_enhanced(self, spec_obj) -> Optional[str]:
        """Extract type reference with namespace awareness"""
        type_elem = self._find_child_element_namespace_aware(spec_obj, 'TYPE')
        if type_elem is not None:
            return (type_elem.get('SPEC-OBJECT-TYPE-REF') or
                   type_elem.get('spec-object-type-ref'))
        return None

    def _extract_attribute_values_enhanced(self, spec_obj, requirement: Dict[str, Any]):
        """Enhanced attribute value extraction with namespace awareness"""
        # Find VALUES container with namespace awareness
        values_elem = self._find_child_element_namespace_aware(spec_obj, 'VALUES')
        if values_elem is None:
            return

        # Find all attribute value types
        value_types = [
            'ATTRIBUTE-VALUE-STRING',
            'ATTRIBUTE-VALUE-XHTML',
            'ATTRIBUTE-VALUE-ENUMERATION',
            'ATTRIBUTE-VALUE-INTEGER',
            'ATTRIBUTE-VALUE-REAL',
            'ATTRIBUTE-VALUE-DATE',
            'ATTRIBUTE-VALUE-BOOLEAN'
        ]

        for value_type in value_types:
            attr_values = self._find_elements_namespace_aware(values_elem, value_type)

            for attr_value_elem in attr_values:
                self._process_single_attribute_value(attr_value_elem, value_type, requirement)

    def _process_single_attribute_value(self, attr_value_elem, value_type: str, requirement: Dict[str, Any]):
        """Process a single attribute value with enhanced content extraction"""
        # Get attribute definition reference
        attr_def_ref = self._extract_attribute_definition_ref_enhanced(attr_value_elem)

        if not attr_def_ref:
            return

        # Get attribute definition
        attr_def = self.attribute_definitions.get(attr_def_ref)

        # Extract content using multiple strategies
        if attr_def and attr_def['data_type'] == 'enumeration':
            content = self._extract_enumeration_content_enhanced(attr_value_elem)
        else:
            content = self._extract_content_enhanced(attr_value_elem, value_type)

        if not content:
            return

        # Store raw content (using definition reference)
        requirement['raw_attributes'][attr_def_ref] = content

        # Get human-readable attribute name
        attr_name = attr_def.get('long_name', attr_def_ref) if attr_def else attr_def_ref

        # Store with human-readable name
        requirement['attributes'][attr_name] = content

        self.stats['content_extractions'] += 1

    def _extract_attribute_definition_ref_enhanced(self, attr_value_elem) -> Optional[str]:
        """Extract attribute definition reference with enhanced methods"""
        # Method 1: Direct attribute
        attr_def_ref = (attr_value_elem.get('ATTRIBUTE-DEFINITION-REF') or
                       attr_value_elem.get('attribute-definition-ref'))
        if attr_def_ref:
            return attr_def_ref

        # Method 2: DEFINITION child element with namespace awareness
        def_elem = self._find_child_element_namespace_aware(attr_value_elem, 'DEFINITION')
        if def_elem is not None:
            # Look for various reference element types
            ref_types = [
                'ATTRIBUTE-DEFINITION-STRING-REF',
                'ATTRIBUTE-DEFINITION-XHTML-REF',
                'ATTRIBUTE-DEFINITION-ENUMERATION-REF',
                'ATTRIBUTE-DEFINITION-INTEGER-REF',
                'ATTRIBUTE-DEFINITION-REAL-REF',
                'ATTRIBUTE-DEFINITION-DATE-REF',
                'ATTRIBUTE-DEFINITION-BOOLEAN-REF'
            ]

            for ref_type in ref_types:
                ref_elem = self._find_child_element_namespace_aware(def_elem, ref_type)
                if ref_elem is not None and ref_elem.text:
                    return ref_elem.text.strip()

        return None

    def _extract_content_enhanced(self, attr_value_elem, value_type: str) -> str:
        """Enhanced content extraction addressing THE-VALUE issues"""
        if 'STRING' in value_type:
            return self._extract_string_content_enhanced(attr_value_elem)
        elif 'XHTML' in value_type:
            return self._extract_xhtml_content_enhanced(attr_value_elem)
        elif 'ENUMERATION' in value_type:
            return self._extract_enumeration_content_enhanced(attr_value_elem)
        elif value_type in ['ATTRIBUTE-VALUE-INTEGER', 'ATTRIBUTE-VALUE-REAL', 'ATTRIBUTE-VALUE-DATE']:
            return self._extract_numeric_content_enhanced(attr_value_elem)
        elif 'BOOLEAN' in value_type:
            return self._extract_boolean_content_enhanced(attr_value_elem)
        else:
            return self._extract_generic_content_enhanced(attr_value_elem)

    def _extract_string_content_enhanced(self, elem) -> str:
        """Extract STRING content with multiple strategies"""
        # Strategy 1: THE-VALUE attribute
        the_value = elem.get('THE-VALUE') or elem.get('the-value')
        if the_value:
            return str(the_value)

        # Strategy 2: THE-VALUE child element with namespace awareness
        the_value_elem = self._find_child_element_namespace_aware(elem, 'THE-VALUE')
        if the_value_elem is not None:
            return self._extract_all_text_enhanced(the_value_elem)

        # Strategy 3: Direct text content
        if elem.text:
            return elem.text.strip()

        return ''

    def _extract_xhtml_content_enhanced(self, elem) -> str:
        """Extract XHTML content with namespace-aware THE-VALUE finding"""
        # Strategy 1: Find THE-VALUE child with namespace awareness
        the_value_elem = self._find_child_element_namespace_aware(elem, 'THE-VALUE')
        if the_value_elem is not None:
            return self._extract_all_text_enhanced(the_value_elem)

        # Strategy 2: Extract all text content
        all_text = self._extract_all_text_enhanced(elem)

        # Clean up - remove reference IDs that appear at the start
        if all_text.startswith('_'):
            # Remove leading reference ID
            parts = all_text.split(' ', 1)
            if len(parts) > 1:
                return parts[1]

        return all_text

    def _extract_enumeration_content_enhanced(self, elem) -> str:
        """Extract enumeration content with namespace awareness"""
        # Strategy 1: Find ENUM-VALUE-REF elements in a VALUES container
        values_container = self._find_child_element_namespace_aware(elem, 'VALUES')
        if values_container is not None:
            enum_refs = self._find_elements_namespace_aware(values_container, 'ENUM-VALUE-REF')
            if enum_refs:
                enum_value_id = enum_refs[0].text.strip()
                return self.enum_values.get(enum_value_id, enum_value_id)

        # Strategy 2: Look for a THE-VALUE attribute directly on the element
        the_value = elem.get('THE-VALUE') or elem.get('the-value')
        if the_value:
            return self.enum_values.get(the_value, the_value)

        return ''

    def _extract_numeric_content_enhanced(self, elem) -> str:
        """Extract numeric content (integer, real, date)"""
        # THE-VALUE attribute
        the_value = elem.get('THE-VALUE') or elem.get('the-value')
        if the_value is not None:
            return str(the_value)

        # THE-VALUE child element
        the_value_elem = self._find_child_element_namespace_aware(elem, 'THE-VALUE')
        if the_value_elem is not None and the_value_elem.text:
            return the_value_elem.text

        return ''

    def _extract_boolean_content_enhanced(self, elem) -> str:
        """Extract boolean content with human-readable conversion"""
        value = self._extract_numeric_content_enhanced(elem)
        if value.lower() in ['true', '1', 'yes']:
            return 'Yes'
        elif value.lower() in ['false', '0', 'no']:
            return 'No'
        return value

    def _extract_generic_content_enhanced(self, elem) -> str:
        """Generic content extraction for unknown types"""
        return (elem.get('THE-VALUE') or
                elem.get('the-value') or
                self._extract_all_text_enhanced(elem))

    def _extract_all_text_enhanced(self, element) -> str:
        """Extract all text content recursively with better cleanup"""
        if element is None:
            return ''

        texts = []

        # Add element's direct text
        if element.text:
            texts.append(element.text.strip())

        # Process all children recursively
        for child in element:
            child_text = self._extract_all_text_enhanced(child)
            if child_text:
                texts.append(child_text)

            # Add tail text
            if child.tail:
                texts.append(child.tail.strip())

        # Join and clean up
        full_text = ' '.join(texts)

        # Enhanced cleanup
        full_text = re.sub(r'\s+', ' ', full_text)  # Multiple spaces to single
        full_text = html.unescape(full_text)        # Decode HTML entities

        return full_text.strip()

    def _create_content_hash(self, req: Dict[str, Any]) -> str:
        """Create a content string for comparison purposes using only actual fields"""
        parts = []

        # Add ID (always present)
        if req.get('id'):
            parts.append(f"ID:{req['id']}")

        # Add identifier if different from id
        if req.get('identifier') and req.get('identifier') != req.get('id'):
            parts.append(f"IDENTIFIER:{req['identifier']}")

        # Add type if present
        if req.get('type'):
            parts.append(f"TYPE:{req['type']}")

        # Add attributes (limit to avoid huge hashes)
        attr_count = 0
        for attr_name, attr_value in req.get('attributes', {}).items():
            if attr_value and attr_count < 10:  # Limit to first 10 meaningful attributes
                parts.append(f"{attr_name}:{attr_value}")
                attr_count += 1

        return '||'.join(parts)

    # Core utility methods with namespace awareness
    def _find_elements_namespace_aware(self, parent, element_name: str) -> List:
        """Find elements with robust namespace awareness"""
        found_elements = []

        # Strategy 1: Namespace-aware search
        if self.namespace_uri:
            try:
                namespaced_name = f"{{{self.namespace_uri}}}{element_name}"
                elements = parent.findall(f".//{namespaced_name}")
                if elements:
                    return elements
            except:
                pass

        # Strategy 2: XPath with registered namespace
        if self.namespace_uri:
            try:
                elements = parent.findall(f".//{self.ns_prefix}:{element_name}",
                                        {self.ns_prefix: self.namespace_uri})
                if elements:
                    return elements
            except:
                pass

        # Strategy 3: Pattern matching (fallback)
        try:
            for elem in parent.iter():
                if element_name in elem.tag:
                    found_elements.append(elem)
            if found_elements:
                return found_elements
        except:
            pass

        return found_elements

    def _find_child_element_namespace_aware(self, parent, element_name: str):
        """Find direct child element with namespace awareness"""
        # Strategy 1: Direct namespace-aware search
        if self.namespace_uri:
            namespaced_name = f"{{{self.namespace_uri}}}{element_name}"
            child = parent.find(namespaced_name)
            if child is not None:
                return child

        # Strategy 2: Pattern matching in direct children
        for child in parent:
            if element_name in child.tag:
                return child

        # Strategy 3: Recursive search
        found = parent.find(f".//{element_name}")
        if found is not None:
            return found

        # Strategy 4: Namespace-aware recursive
        if self.namespace_uri:
            namespaced_name = f"{{{self.namespace_uri}}}{element_name}"
            found = parent.find(f".//{namespaced_name}")
            if found is not None:
                return found

        return None

    def _extract_identifier(self, element) -> Optional[str]:
        """Extract identifier with multiple fallback patterns"""
        return (element.get('IDENTIFIER') or
                element.get('identifier') or
                element.get('ID') or
                element.get('id'))

    def _extract_long_name(self, element) -> Optional[str]:
        """Extract long name with multiple fallback patterns"""
        return (element.get('LONG-NAME') or
                element.get('long-name') or
                element.get('NAME') or
                element.get('name'))

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive information about a ReqIF file"""
        try:
            requirements = self.parse_file(file_path)

            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_type': 'ReqIFZ' if file_path.lower().endswith('.reqifz') else 'ReqIF',
                'file_size': os.path.getsize(file_path),
                'requirement_count': len(requirements),
                'parsing_success': True,
                'namespace_used': self.namespace_uri,
                'definitions_found': self.stats['definitions_cataloged'],
                'content_extractions': self.stats['content_extractions']
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'error': str(e),
                'parsing_success': False
            }

    def get_debug_info(self) -> Dict[str, Any]:
        """Get detailed debug information from the last parse operation"""
        return {
            'parsing_summary': self.stats.copy(),
            'namespace_info': {
                'namespace_uri': self.namespace_uri,
                'root_namespace': self.root_namespace
            },
            'catalog_sizes': {
                'attribute_definitions': len(self.attribute_definitions),
                'spec_object_types': len(self.spec_object_types),
                'enumeration_definitions': len(self.enumeration_definitions),
                'enum_values': len(self.enum_values)
            }
        }


# Example usage
if __name__ == "__main__":
    print("Enhanced ReqIF Parser - No Artificial Field Mapping Version")
    print("Features: Namespace-aware parsing, authentic content extraction, no field mapping")

    # Example usage:
    # parser = ReqIFParser()
    # requirements = parser.parse_file("example.reqif")
    # print(f"Parsed {len(requirements)} requirements")
    # print("Actual fields found:", set().union(*(req.keys() for req in requirements)))
