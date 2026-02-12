# -*- coding: utf-8 -*-
# =============================================================================
# GeoNode Catalogue Service - Metadata Discovery Portal
# =============================================================================

import os
import uuid
import logging
from io import BytesIO
from datetime import datetime, timezone
from urllib.parse import urlencode

from flask import Flask, request, Response, render_template, abort
from owslib_compat.etree import etree
from owslib_compat.namespaces import Namespaces

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('geonode.catalogue')

# ============================================================================
# OGC Namespace configuration
# ============================================================================

ns = Namespaces()
NAMESPACES = {
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'ogc': 'http://www.opengis.net/ogc',
    'ows': 'http://www.opengis.net/ows',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xsd': 'http://www.w3.org/2001/XMLSchema',
}

SCHEMA = 'http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd'

# ============================================================================
# Sample metadata records (GeoNode catalogue entries)
# ============================================================================

METADATA_RECORDS = {
    'rec-001': {
        'identifier': 'rec-001',
        'title': 'Global Administrative Boundaries',
        'abstract': 'Administrative boundary polygons for all countries, sourced from Natural Earth.',
        'type': 'dataset',
        'format': 'application/gml+xml',
        'subject': ['boundaries', 'administrative', 'global'],
        'date': '2023-06-15',
        'bbox': {'west': -180.0, 'east': 180.0, 'south': -90.0, 'north': 90.0},
        'crs': 'EPSG:4326',
        'creator': 'Natural Earth Data',
        'publisher': 'GeoNode Portal',
        'language': 'eng',
    },
    'rec-002': {
        'identifier': 'rec-002',
        'title': 'Digital Elevation Model - SRTM 30m',
        'abstract': 'Shuttle Radar Topography Mission 30-meter resolution DEM.',
        'type': 'dataset',
        'format': 'image/tiff',
        'subject': ['elevation', 'terrain', 'DEM', 'SRTM'],
        'date': '2022-11-01',
        'bbox': {'west': -180.0, 'east': 180.0, 'south': -60.0, 'north': 60.0},
        'crs': 'EPSG:4326',
        'creator': 'NASA/USGS',
        'publisher': 'GeoNode Portal',
        'language': 'eng',
    },
    'rec-003': {
        'identifier': 'rec-003',
        'title': 'OpenStreetMap Land Use Classification',
        'abstract': 'Land use and land cover classification derived from OpenStreetMap.',
        'type': 'dataset',
        'format': 'application/gml+xml',
        'subject': ['landuse', 'landcover', 'classification', 'OSM'],
        'date': '2023-09-20',
        'bbox': {'west': -10.0, 'east': 35.0, 'south': 35.0, 'north': 72.0},
        'crs': 'EPSG:3857',
        'creator': 'OpenStreetMap Contributors',
        'publisher': 'GeoNode Portal',
        'language': 'eng',
    },
    'rec-004': {
        'identifier': 'rec-004',
        'title': 'Sea Surface Temperature - Monthly Averages',
        'abstract': 'Monthly averaged sea surface temperature data from NOAA satellites.',
        'type': 'dataset',
        'format': 'application/netcdf',
        'subject': ['ocean', 'temperature', 'SST', 'climate'],
        'date': '2024-01-10',
        'bbox': {'west': -180.0, 'east': 180.0, 'south': -90.0, 'north': 90.0},
        'crs': 'EPSG:4326',
        'creator': 'NOAA',
        'publisher': 'GeoNode Portal',
        'language': 'eng',
    },
    'rec-005': {
        'identifier': 'rec-005',
        'title': 'Urban Infrastructure Network - Water Supply',
        'abstract': 'Water supply network infrastructure for metropolitan areas.',
        'type': 'dataset',
        'format': 'application/gml+xml',
        'subject': ['infrastructure', 'water', 'urban', 'network'],
        'date': '2023-04-22',
        'bbox': {'west': -74.3, 'east': -73.7, 'south': 40.4, 'north': 40.9},
        'crs': 'EPSG:4326',
        'creator': 'NYC Open Data',
        'publisher': 'GeoNode Portal',
        'language': 'eng',
    },
}


# ============================================================================
# CSW Response builders
# ============================================================================

def build_capabilities_xml():
    """Build GetCapabilities response XML."""
    root = etree.Element('{%s}Capabilities' % NAMESPACES['csw'], nsmap=NAMESPACES)
    root.set('version', '2.0.2')

    # ServiceIdentification
    si = etree.SubElement(root, '{%s}ServiceIdentification' % NAMESPACES['ows'])
    etree.SubElement(si, '{%s}Title' % NAMESPACES['ows']).text = 'GeoNode CSW'
    etree.SubElement(si, '{%s}Abstract' % NAMESPACES['ows']).text = \
        'GeoNode Catalogue Service for spatial data discovery'
    etree.SubElement(si, '{%s}ServiceType' % NAMESPACES['ows']).text = 'CSW'
    etree.SubElement(si, '{%s}ServiceTypeVersion' % NAMESPACES['ows']).text = '2.0.2'

    # OperationsMetadata
    om = etree.SubElement(root, '{%s}OperationsMetadata' % NAMESPACES['ows'])
    for op_name in ['GetCapabilities', 'GetRecords', 'GetRecordById', 'Transaction']:
        op = etree.SubElement(om, '{%s}Operation' % NAMESPACES['ows'])
        op.set('name', op_name)
        dcp = etree.SubElement(op, '{%s}DCP' % NAMESPACES['ows'])
        http = etree.SubElement(dcp, '{%s}HTTP' % NAMESPACES['ows'])
        get = etree.SubElement(http, '{%s}Get' % NAMESPACES['ows'])
        get.set('{http://www.w3.org/1999/xlink}href', '/csw')
        post = etree.SubElement(http, '{%s}Post' % NAMESPACES['ows'])
        post.set('{http://www.w3.org/1999/xlink}href', '/csw')

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


def build_record_xml(record, element_set='full'):
    """Build a single record in Dublin Core format."""
    rec = etree.Element('{%s}Record' % NAMESPACES['csw'], nsmap=NAMESPACES)

    etree.SubElement(rec, '{%s}identifier' % NAMESPACES['dc']).text = record['identifier']
    etree.SubElement(rec, '{%s}title' % NAMESPACES['dc']).text = record['title']
    etree.SubElement(rec, '{%s}type' % NAMESPACES['dc']).text = record['type']

    if element_set in ('full', 'summary'):
        etree.SubElement(rec, '{%s}abstract' % NAMESPACES['dct']).text = record['abstract']
        etree.SubElement(rec, '{%s}format' % NAMESPACES['dc']).text = record['format']
        for subject in record.get('subject', []):
            etree.SubElement(rec, '{%s}subject' % NAMESPACES['dc']).text = subject
        etree.SubElement(rec, '{%s}date' % NAMESPACES['dc']).text = record['date']

    if element_set == 'full':
        etree.SubElement(rec, '{%s}creator' % NAMESPACES['dc']).text = record.get('creator', '')
        etree.SubElement(rec, '{%s}publisher' % NAMESPACES['dc']).text = record.get('publisher', '')
        etree.SubElement(rec, '{%s}language' % NAMESPACES['dc']).text = record.get('language', 'eng')

        bbox = record.get('bbox', {})
        if bbox:
            ows_bbox = etree.SubElement(rec, '{%s}BoundingBox' % NAMESPACES['ows'])
            ows_bbox.set('crs', record.get('crs', 'EPSG:4326'))
            etree.SubElement(ows_bbox, '{%s}LowerCorner' % NAMESPACES['ows']).text = \
                '%s %s' % (bbox.get('west', ''), bbox.get('south', ''))
            etree.SubElement(ows_bbox, '{%s}UpperCorner' % NAMESPACES['ows']).text = \
                '%s %s' % (bbox.get('east', ''), bbox.get('north', ''))

    return rec


def build_search_results(records, element_set='full', start_position=1, max_records=10):
    """Build GetRecordsResponse XML."""
    root = etree.Element('{%s}GetRecordsResponse' % NAMESPACES['csw'], nsmap=NAMESPACES)
    root.set('version', '2.0.2')

    # SearchStatus
    status = etree.SubElement(root, '{%s}SearchStatus' % NAMESPACES['csw'])
    status.set('timestamp', datetime.now(timezone.utc).isoformat())

    # SearchResults
    results = etree.SubElement(root, '{%s}SearchResults' % NAMESPACES['csw'])
    results.set('numberOfRecordsMatched', str(len(records)))
    results.set('numberOfRecordsReturned', str(min(len(records), max_records)))
    results.set('nextRecord', str(min(start_position + max_records, len(records) + 1)))
    results.set('elementSet', element_set)

    for rec in list(records.values())[(start_position - 1):(start_position - 1 + max_records)]:
        results.append(build_record_xml(rec, element_set))

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


def build_record_by_id_response(record_id, element_set='full'):
    """Build GetRecordById response."""
    if record_id in METADATA_RECORDS:
        root = etree.Element('{%s}GetRecordByIdResponse' % NAMESPACES['csw'], nsmap=NAMESPACES)
        root.append(build_record_xml(METADATA_RECORDS[record_id], element_set))
        return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    return None


def build_exception(code, text):
    """Build OGC ExceptionReport XML."""
    root = etree.Element('{%s}ExceptionReport' % NAMESPACES['ows'], nsmap={'ows': NAMESPACES['ows']})
    root.set('version', '1.2.0')
    exc = etree.SubElement(root, '{%s}Exception' % NAMESPACES['ows'])
    exc.set('exceptionCode', code)
    et = etree.SubElement(exc, '{%s}ExceptionText' % NAMESPACES['ows'])
    et.text = text
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


def build_transaction_response(action, identifier):
    """Build Transaction response XML."""
    root = etree.Element('{%s}TransactionResponse' % NAMESPACES['csw'], nsmap=NAMESPACES)
    root.set('version', '2.0.2')

    summary = etree.SubElement(root, '{%s}TransactionSummary' % NAMESPACES['csw'])
    if action == 'Insert':
        etree.SubElement(summary, '{%s}totalInserted' % NAMESPACES['csw']).text = '1'
    elif action == 'Update':
        etree.SubElement(summary, '{%s}totalUpdated' % NAMESPACES['csw']).text = '1'

    if action == 'Insert':
        ins_result = etree.SubElement(root, '{%s}InsertResult' % NAMESPACES['csw'])
        brief = etree.SubElement(ins_result, '{%s}BriefRecord' % NAMESPACES['csw'])
        etree.SubElement(brief, '{%s}identifier' % NAMESPACES['dc']).text = identifier

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


# ============================================================================
# CSW request processing
# ============================================================================

def process_get_records(xml_root):
    """Process a GetRecords request from parsed XML."""
    element_set = 'full'
    start_position = 1
    max_records = 10

    # Parse attributes
    sp = xml_root.get('startPosition')
    if sp:
        try:
            start_position = int(sp)
        except ValueError:
            pass
    mr = xml_root.get('maxRecords')
    if mr:
        try:
            max_records = int(mr)
        except ValueError:
            pass

    # Check for ElementSetName in Query
    query = xml_root.find('.//{%s}Query' % NAMESPACES['csw'])
    if query is not None:
        esn = query.find('{%s}ElementSetName' % NAMESPACES['csw'])
        if esn is not None and esn.text in ('brief', 'summary', 'full'):
            element_set = esn.text

    # Check for constraint/filter
    filtered_records = dict(METADATA_RECORDS)

    if query is not None:
        constraint = query.find('{%s}Constraint' % NAMESPACES['csw'])
        if constraint is not None:
            ogc_filter = constraint.find('{%s}Filter' % NAMESPACES['ogc'])
            if ogc_filter is not None:
                prop_eq = ogc_filter.find('{%s}PropertyIsEqualTo' % NAMESPACES['ogc'])
                if prop_eq is not None:
                    prop_name = prop_eq.find('{%s}PropertyName' % NAMESPACES['ogc'])
                    literal = prop_eq.find('{%s}Literal' % NAMESPACES['ogc'])
                    if prop_name is not None and literal is not None:
                        field = prop_name.text
                        value = literal.text if literal.text else ''
                        filtered_records = {}
                        for rid, rec in METADATA_RECORDS.items():
                            if field == 'dc:title' and value.lower() in rec['title'].lower():
                                filtered_records[rid] = rec
                            elif field == 'dc:subject':
                                if value.lower() in [s.lower() for s in rec.get('subject', [])]:
                                    filtered_records[rid] = rec
                            elif field == 'dc:type' and value.lower() == rec['type'].lower():
                                filtered_records[rid] = rec
                            elif field == 'dc:identifier' and value == rec['identifier']:
                                filtered_records[rid] = rec

                prop_like = ogc_filter.find('{%s}PropertyIsLike' % NAMESPACES['ogc'])
                if prop_like is not None:
                    prop_name = prop_like.find('{%s}PropertyName' % NAMESPACES['ogc'])
                    literal = prop_like.find('{%s}Literal' % NAMESPACES['ogc'])
                    if prop_name is not None and literal is not None:
                        field = prop_name.text
                        value = literal.text if literal.text else ''
                        value_lower = value.lower().replace('%', '')
                        filtered_records = {}
                        for rid, rec in METADATA_RECORDS.items():
                            if field in ('dc:title', 'csw:AnyText'):
                                searchable = rec['title'] + ' ' + rec['abstract']
                                if value_lower in searchable.lower():
                                    filtered_records[rid] = rec
                            elif field == 'dc:subject':
                                if any(value_lower in s.lower() for s in rec.get('subject', [])):
                                    filtered_records[rid] = rec

    return build_search_results(filtered_records, element_set, start_position, max_records)


def process_transaction(xml_root):
    """Process a CSW Transaction request (Insert/Update)."""
    insert_el = xml_root.find('{%s}Insert' % NAMESPACES['csw'])
    if insert_el is not None:
        record = insert_el.find('{%s}Record' % NAMESPACES['csw'])
        if record is None:
            record = insert_el.find('{%s}Record' % NAMESPACES['dc'])
        if record is not None:
            identifier = str(uuid.uuid4())[:8]
            dc_id = record.find('{%s}identifier' % NAMESPACES['dc'])
            if dc_id is not None and dc_id.text:
                identifier = dc_id.text

            title_el = record.find('{%s}title' % NAMESPACES['dc'])
            abstract_el = record.find('{%s}abstract' % NAMESPACES['dct'])

            METADATA_RECORDS['rec-' + identifier] = {
                'identifier': identifier,
                'title': title_el.text if title_el is not None else 'Untitled',
                'abstract': abstract_el.text if abstract_el is not None else '',
                'type': 'dataset',
                'format': 'application/xml',
                'subject': [],
                'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'bbox': {},
                'crs': 'EPSG:4326',
                'creator': 'Anonymous',
                'publisher': 'GeoNode Portal',
                'language': 'eng',
            }
            return build_transaction_response('Insert', identifier)

    return build_exception('InvalidParameterValue', 'Transaction operation not supported')


# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html', records=METADATA_RECORDS)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/catalogue/<record_id>')
def record_detail(record_id):
    record = METADATA_RECORDS.get(record_id)
    if record is None:
        abort(404)
    return render_template('record_detail.html', record=record)


@app.route('/csw', methods=['GET', 'POST'])
def csw_endpoint():
    """
    CSW 2.0.2 endpoint implementing GetCapabilities, GetRecords,
    GetRecordById, and Transaction operations.

    Supports both HTTP GET (KVP) and HTTP POST (XML) bindings.
    """
    if request.method == 'GET':
        service = request.args.get('service', 'CSW')
        req = request.args.get('request', '')
        version = request.args.get('version', '2.0.2')

        if req == 'GetCapabilities':
            return Response(build_capabilities_xml(), mimetype='application/xml')

        elif req == 'GetRecords':
            element_set = request.args.get('ElementSetName', 'full')
            type_names = request.args.get('typeNames', 'csw:Record')
            start = int(request.args.get('startPosition', '1'))
            max_rec = int(request.args.get('maxRecords', '10'))
            return Response(
                build_search_results(METADATA_RECORDS, element_set, start, max_rec),
                mimetype='application/xml'
            )

        elif req == 'GetRecordById':
            record_id = request.args.get('Id', request.args.get('id', ''))
            element_set = request.args.get('ElementSetName', 'full')
            result = build_record_by_id_response(record_id, element_set)
            if result:
                return Response(result, mimetype='application/xml')
            return Response(
                build_exception('InvalidParameterValue', 'Record not found: %s' % record_id),
                status=404, mimetype='application/xml'
            )

        return Response(
            build_exception('MissingParameterValue', 'Missing "request" parameter'),
            status=400, mimetype='application/xml'
        )

    elif request.method == 'POST':
        xml_data = request.data
        if not xml_data:
            return Response(
                build_exception('MissingParameterValue', 'Empty request body'),
                status=400, mimetype='application/xml'
            )

        try:
            doc = etree.fromstring(xml_data)
        except Exception as e:
            return Response(
                build_exception('NoApplicableCode', 'XML parsing error'),
                status=400, mimetype='application/xml'
            )

        local_name = etree.QName(doc.tag).localname

        if local_name == 'GetCapabilities':
            return Response(build_capabilities_xml(), mimetype='application/xml')

        elif local_name == 'GetRecords':
            return Response(process_get_records(doc), mimetype='application/xml')

        elif local_name == 'GetRecordById':
            id_el = doc.find('{%s}Id' % NAMESPACES['csw'])
            if id_el is not None and id_el.text:
                element_set = 'full'
                esn = doc.find('{%s}ElementSetName' % NAMESPACES['csw'])
                if esn is not None:
                    element_set = esn.text
                record_id_value = id_el.text.strip()
                result = build_record_by_id_response(record_id_value, element_set)
                if result:
                    return Response(result, mimetype='application/xml')
                return Response(
                    build_exception('InvalidParameterValue',
                                   'No record found for Id: %s' % record_id_value),
                    status=404, mimetype='application/xml'
                )
            return Response(
                build_exception('MissingParameterValue', 'Missing Id element'),
                status=400, mimetype='application/xml'
            )

        elif local_name == 'Transaction':
            return Response(process_transaction(doc), mimetype='application/xml')

        return Response(
            build_exception('InvalidParameterValue', 'Unknown request: %s' % local_name),
            status=400, mimetype='application/xml'
        )


@app.route('/ping')
def health():
    return 'OK', 200


# ============================================================================
# Error handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/csw'):
        return Response(
            build_exception('InvalidParameterValue', 'Not found'),
            status=404, mimetype='application/xml'
        )
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/csw'):
        return Response(
            build_exception('NoApplicableCode', 'Internal server error'),
            status=500, mimetype='application/xml'
        )
    return 'Internal Server Error', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
