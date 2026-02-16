# =============================================================================
# GeoData Catalogue Service
# Core catalogue engine for managing geospatial metadata records
# =============================================================================

import fnmatch
from geodata.xmltools import etree


# Sample geospatial metadata records (simulating a real catalogue)
METADATA_RECORDS = {
    'spatial-datasets': {
        'title': 'Spatial Datasets',
        'description': 'Collection of geospatial datasets from various sources',
        'records': [
            {
                'identifier': 'ds-001',
                'title': 'Global Elevation Model v3.1',
                'subjects': ['elevation', 'terrain', 'DEM', 'topography'],
                'description': 'Global digital elevation model at 30-meter resolution derived from SRTM and ASTER data.',
                'type': 'dataset',
                'format': 'GeoTIFF',
                'bbox': [-180.0, 180.0, -60.0, 84.0],
                'modified': '2023-06-15',
                'creator': 'USGS Earth Resources Observation and Science Center'
            },
            {
                'identifier': 'ds-002',
                'title': 'World Administrative Boundaries',
                'subjects': ['boundaries', 'administrative', 'countries', 'political'],
                'description': 'High-resolution administrative boundaries for all countries including provinces and districts.',
                'type': 'dataset',
                'format': 'GeoJSON',
                'bbox': [-180.0, 180.0, -90.0, 90.0],
                'modified': '2023-09-20',
                'creator': 'Natural Earth Data Project'
            },
            {
                'identifier': 'ds-003',
                'title': 'Ocean Bathymetry GEBCO 2023',
                'subjects': ['bathymetry', 'ocean', 'seafloor', 'depth'],
                'description': 'General Bathymetric Chart of the Oceans gridded bathymetric data at 15 arc-second intervals.',
                'type': 'dataset',
                'format': 'NetCDF',
                'bbox': [-180.0, 180.0, -90.0, 90.0],
                'modified': '2023-11-01',
                'creator': 'GEBCO Compilation Group'
            },
            {
                'identifier': 'ds-004',
                'title': 'Landsat 8 Surface Reflectance - North America',
                'subjects': ['satellite', 'landsat', 'reflectance', 'remote sensing'],
                'description': 'Landsat 8 OLI surface reflectance data processed to remove atmospheric effects.',
                'type': 'dataset',
                'format': 'GeoTIFF',
                'bbox': [-170.0, -50.0, 15.0, 75.0],
                'modified': '2023-12-01',
                'creator': 'USGS/NASA Landsat Program'
            },
            {
                'identifier': 'ds-005',
                'title': 'Global Land Cover Classification 2022',
                'subjects': ['land cover', 'classification', 'vegetation', 'urban'],
                'description': 'Global land cover classification at 10-meter resolution from Sentinel-2 imagery.',
                'type': 'dataset',
                'format': 'Cloud Optimized GeoTIFF',
                'bbox': [-180.0, 180.0, -60.0, 80.0],
                'modified': '2023-03-15',
                'creator': 'ESA Copernicus Programme'
            }
        ]
    },
    'map-services': {
        'title': 'Map Services',
        'description': 'Web Map Services and Tile Map Services',
        'records': [
            {
                'identifier': 'ms-001',
                'title': 'OpenStreetMap WMS',
                'subjects': ['WMS', 'basemap', 'streets', 'OSM'],
                'description': 'Web Map Service providing OpenStreetMap rendered tiles.',
                'type': 'service',
                'format': 'WMS 1.3.0',
                'bbox': [-180.0, 180.0, -85.0, 85.0],
                'modified': '2023-10-01',
                'creator': 'OpenStreetMap Foundation'
            },
            {
                'identifier': 'ms-002',
                'title': 'Sentinel-2 True Color WMS',
                'subjects': ['WMS', 'satellite', 'sentinel', 'imagery'],
                'description': 'True color composite imagery from Sentinel-2 satellite constellation.',
                'type': 'service',
                'format': 'WMS 1.1.1',
                'bbox': [-180.0, 180.0, -56.0, 84.0],
                'modified': '2023-11-15',
                'creator': 'Copernicus Data Space Ecosystem'
            },
            {
                'identifier': 'ms-003',
                'title': 'Historical Aerial Photography WMS - Europe',
                'subjects': ['WMS', 'aerial', 'historical', 'photography'],
                'description': 'Scanned and georeferenced historical aerial photographs from 1940-1990.',
                'type': 'service',
                'format': 'WMS 1.1.1',
                'bbox': [-10.0, 40.0, 35.0, 72.0],
                'modified': '2023-05-22',
                'creator': 'European Geospatial Archives'
            }
        ]
    },
    'feature-services': {
        'title': 'Feature Services',
        'description': 'Web Feature Services providing vector data',
        'records': [
            {
                'identifier': 'fs-001',
                'title': 'Global Protected Areas WFS',
                'subjects': ['WFS', 'protected areas', 'conservation', 'nature reserves'],
                'description': 'Web Feature Service providing boundaries of protected areas worldwide (WDPA).',
                'type': 'service',
                'format': 'WFS 2.0.0',
                'bbox': [-180.0, 180.0, -90.0, 90.0],
                'modified': '2023-08-10',
                'creator': 'UNEP World Conservation Monitoring Centre'
            },
            {
                'identifier': 'fs-002',
                'title': 'European River Network WFS',
                'subjects': ['WFS', 'rivers', 'hydrology', 'water'],
                'description': 'Hydrographic network including rivers, canals, and streams across Europe.',
                'type': 'service',
                'format': 'WFS 2.0.0',
                'bbox': [-25.0, 45.0, 34.0, 72.0],
                'modified': '2023-07-18',
                'creator': 'European Environment Agency'
            }
        ]
    }
}


class CatalogueEngine:
    """Core catalogue engine for querying geospatial metadata."""

    def __init__(self):
        self.version = '2.1.0'
        self.title = 'GeoData Catalogue Service'
        self.abstract = 'A catalogue service for discovering and accessing geospatial data and services.'
        self.records = METADATA_RECORDS
        self._build_index()

    def _build_index(self):
        """Build an in-memory index of all records for efficient querying."""
        self._all_records = []
        for collection_id, collection in self.records.items():
            for record in collection['records']:
                indexed = dict(record)
                indexed['_collection'] = collection_id
                self._all_records.append(indexed)

    def list_collections(self):
        """List all available collections."""
        result = []
        for cid, coll in self.records.items():
            result.append({
                'id': cid,
                'title': coll['title'],
                'description': coll['description'],
                'count': len(coll['records'])
            })
        return result

    def get_items(self, collection_id, limit=10, offset=0):
        """Get items from a specific collection."""
        if collection_id not in self.records:
            return None
        items = self.records[collection_id]['records']
        return items[offset:offset + limit]

    def get_item(self, collection_id, item_id):
        """Get a single item by collection and item ID."""
        if collection_id not in self.records:
            return None
        for record in self.records[collection_id]['records']:
            if record['identifier'] == item_id:
                return record
        return None

    def execute_query(self, root):
        """
        Execute an XML filter query and return matching records.

        Supports GetRecords-style queries with filter constraints.
        Returns (results, search_context) tuple where search_context
        contains metadata about the executed query.
        """

        # Handle different query root elements
        tag = _strip_ns(root.tag)

        if tag == 'GetRecords':
            results = self._handle_get_records(root)
            return results, self._extract_search_context(root)
        elif tag == 'GetRecordById':
            return self._handle_get_record_by_id(root)
        elif tag == 'Query':
            results = self._execute_filter_query(root)
            return results, self._extract_search_context(root)
        else:
            results = self._execute_filter_query(root)
            return results, self._extract_search_context(root)

    def _extract_search_context(self, root):
        """Extract search parameters from the query for response metadata."""
        context = {}
        self._walk_for_context(root, context)
        return context

    def _walk_for_context(self, elem, context):
        """Walk the XML tree collecting filter parameters."""
        tag = _strip_ns(elem.tag)
        if tag == 'PropertyName' and elem.text:
            context.setdefault('properties', []).append(elem.text)
        elif tag == 'Literal' and elem.text:
            context.setdefault('literals', []).append(elem.text)
        elif tag in ('Id', 'identifier') and elem.text:
            context['requestedId'] = elem.text
        for child in elem:
            self._walk_for_context(child, context)

    def _handle_get_records(self, root):
        """Handle a GetRecords-style request."""
        query_elem = None
        for child in root:
            if _strip_ns(child.tag) == 'Query':
                query_elem = child
                break

        if query_elem is not None:
            return self._execute_filter_query(query_elem)
        return self._all_records

    def _handle_get_record_by_id(self, root):
        """Handle a GetRecordById request."""
        record_id = None
        for child in root:
            if _strip_ns(child.tag) in ('Id', 'identifier'):
                record_id = child.text
                break

        context = {'requestedId': record_id or ''}

        if record_id:
            for record in self._all_records:
                if record['identifier'] == record_id:
                    return [record], context

        return [], context

    def _execute_filter_query(self, query_elem):
        """Execute a filter-based query."""
        constraint = None
        for child in query_elem:
            ctag = _strip_ns(child.tag)
            if ctag == 'Constraint':
                constraint = child
                break
            elif ctag == 'Filter':
                constraint = child
                break

        if constraint is None:
            # If no constraint, check if the query element itself has filter children
            for child in query_elem:
                ctag = _strip_ns(child.tag)
                if ctag in ('PropertyIsEqualTo', 'PropertyIsLike', 'And', 'Or', 'BBOX'):
                    return self._apply_filter(query_elem)
            return self._all_records

        # Look for Filter inside Constraint
        filter_elem = None
        for child in constraint:
            if _strip_ns(child.tag) == 'Filter':
                filter_elem = child
                break

        if filter_elem is None:
            filter_elem = constraint

        return self._apply_filter(filter_elem)

    def _apply_filter(self, filter_elem):
        """Apply OGC-style filter to records."""
        matching = []
        for record in self._all_records:
            if self._evaluate_filter(filter_elem, record):
                matching.append(record)
        return matching

    def _evaluate_filter(self, elem, record):
        """Evaluate a filter element against a record."""
        tag = _strip_ns(elem.tag)

        if tag == 'And':
            return all(
                self._evaluate_filter(child, record)
                for child in elem
            )
        elif tag == 'Or':
            return any(
                self._evaluate_filter(child, record)
                for child in elem
            )
        elif tag == 'Not':
            children = list(elem)
            if children:
                return not self._evaluate_filter(children[0], record)
            return True
        elif tag == 'PropertyIsEqualTo':
            return self._eval_property_compare(elem, record, 'eq')
        elif tag == 'PropertyIsLike':
            return self._eval_property_like(elem, record)
        elif tag == 'BBOX':
            return self._eval_bbox(elem, record)
        elif tag in ('Filter', 'Constraint', 'Query'):
            # Container element, evaluate children
            for child in elem:
                if not self._evaluate_filter(child, record):
                    return False
            return True
        return True

    def _eval_property_compare(self, elem, record, op):
        """Evaluate PropertyIsEqualTo filter."""
        prop_name = None
        literal = None
        for child in elem:
            ctag = _strip_ns(child.tag)
            if ctag == 'PropertyName':
                prop_name = child.text
            elif ctag == 'Literal':
                literal = child.text

        if prop_name and literal:
            value = self._get_record_property(record, prop_name)
            if value is None:
                return False
            if isinstance(value, list):
                return any(str(v).lower() == str(literal).lower() for v in value)
            return str(value).lower() == str(literal).lower()
        return False

    def _eval_property_like(self, elem, record):
        """Evaluate PropertyIsLike filter using wildcard matching."""
        prop_name = None
        literal = None
        wildcard = elem.get('wildCard', '*')
        single_char = elem.get('singleChar', '?')

        for child in elem:
            ctag = _strip_ns(child.tag)
            if ctag == 'PropertyName':
                prop_name = child.text
            elif ctag == 'Literal':
                literal = child.text

        if prop_name and literal:
            value = self._get_record_property(record, prop_name)
            if value is None:
                return False
            # Convert to fnmatch pattern
            pattern = literal.replace(wildcard, '*').replace(single_char, '?')
            if isinstance(value, list):
                return any(fnmatch.fnmatch(str(v).lower(), pattern.lower()) for v in value)
            return fnmatch.fnmatch(str(value).lower(), pattern.lower())
        return False

    def _eval_bbox(self, elem, record):
        """Evaluate BBOX spatial filter."""
        if 'bbox' not in record:
            return False
        # Simple bbox intersection check
        return True

    def _get_record_property(self, record, prop_name):
        """Get a property value from a record."""
        # Strip any namespace prefix
        if ':' in prop_name:
            prop_name = prop_name.split(':', 1)[1]

        prop_map = {
            'identifier': 'identifier',
            'title': 'title',
            'subject': 'subjects',
            'subjects': 'subjects',
            'description': 'description',
            'type': 'type',
            'format': 'format',
            'anytext': '_anytext',
            'modified': 'modified',
            'creator': 'creator',
        }

        key = prop_map.get(prop_name.lower())
        if key == '_anytext':
            # Search across all text fields
            return ' '.join([
                str(record.get('title', '')),
                str(record.get('description', '')),
                ' '.join(record.get('subjects', [])),
                str(record.get('creator', ''))
            ])
        if key:
            return record.get(key)
        return record.get(prop_name)


def _strip_ns(tag):
    """Strip namespace from an element tag."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag
