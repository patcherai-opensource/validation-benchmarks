#!/usr/bin/env python3
import os
import re
import uuid
import json
import hashlib
from datetime import datetime
from io import BytesIO
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, send_file
from lxml import etree
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(32)

UPLOAD_FOLDER = '/tmp/bom_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

SUPPORTED_SCHEMA_VERSIONS = {
    'http://cyclonedx.org/schema/bom/1.0': '1.0',
    'http://cyclonedx.org/schema/bom/1.1': '1.1',
    'http://cyclonedx.org/schema/bom/1.2': '1.2',
    'http://cyclonedx.org/schema/bom/1.3': '1.3',
    'http://cyclonedx.org/schema/bom/1.4': '1.4',
    'http://cyclonedx.org/schema/bom/1.5': '1.5',
    'http://cyclonedx.org/schema/bom/1.6': '1.6',
}

# In-memory storage for analyzed BOMs
bom_store = {}


def extract_all_namespace_declarations(xml_bytes):
    """
    Extract all namespace declarations from a CycloneDX BOM to identify the
    schema version. Uses XPath namespace axis to find all declared namespaces.
    Also extracts root element attributes for version identification.
    """
    result = {'namespaces': [], 'root_attributes': {}, 'root_tag': None}
    try:
        parser = etree.XMLParser(resolve_entities=True, no_network=False)
        doc = etree.parse(BytesIO(xml_bytes), parser)
        root = doc.getroot()

        # Extract all namespace declarations via iteration
        namespaces = set()
        for elem in doc.iter():
            for ns_prefix, ns_uri in elem.nsmap.items():
                namespaces.add(ns_uri)
        result['namespaces'] = list(namespaces)

        # Extract root element info for schema version identification
        result['root_tag'] = etree.QName(root.tag).localname if '}' in root.tag else root.tag
        result['root_attributes'] = dict(root.attrib)

        # Extract metadata text content for version fingerprinting
        metadata_texts = []
        for child in root:
            local = etree.QName(child.tag).localname if '}' in child.tag else child.tag
            if local == 'metadata':
                for sub in child.iter():
                    if sub.text and sub.text.strip():
                        metadata_texts.append(sub.text.strip())
        result['metadata_texts'] = metadata_texts

    except Exception:
        pass
    return result


def identify_schema_version(xml_bytes):
    """
    Identify the CycloneDX schema version from the BOM XML by inspecting
    namespace declarations.
    """
    extraction = extract_all_namespace_declarations(xml_bytes)
    for ns in extraction.get('namespaces', []):
        if ns in SUPPORTED_SCHEMA_VERSIONS:
            return SUPPORTED_SCHEMA_VERSIONS[ns]
    return None


def parse_bom_components(xml_bytes):
    """
    Parse BOM components using a secure XML parser. This is the main content
    extraction path, separated from schema identification.
    """
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        dtd_validation=False,
        load_dtd=False
    )
    try:
        doc = etree.fromstring(xml_bytes, parser)
    except etree.XMLSyntaxError:
        return None, "Invalid XML syntax"

    # Detect namespace
    nsmap = doc.nsmap
    default_ns = nsmap.get(None, '')
    ns = {'bom': default_ns} if default_ns else {}

    components = []
    prefix = 'bom:' if default_ns else ''

    for comp in doc.findall(f'.//{prefix}component', ns) if default_ns else doc.findall('.//component'):
        component_data = {
            'type': comp.get('type', 'unknown'),
            'bom-ref': comp.get('bom-ref', ''),
        }
        for field in ['name', 'version', 'description', 'purl', 'group', 'publisher']:
            elem = comp.find(f'{prefix}{field}', ns) if default_ns else comp.find(field)
            if elem is not None and elem.text:
                component_data[field] = elem.text

        # Extract licenses
        licenses_elem = comp.find(f'{prefix}licenses', ns) if default_ns else comp.find('licenses')
        if licenses_elem is not None:
            license_list = []
            for lic in (licenses_elem.findall(f'{prefix}license', ns) if default_ns else licenses_elem.findall('license')):
                lid = lic.find(f'{prefix}id', ns) if default_ns else lic.find('id')
                lname = lic.find(f'{prefix}name', ns) if default_ns else lic.find('name')
                if lid is not None and lid.text:
                    license_list.append(lid.text)
                elif lname is not None and lname.text:
                    license_list.append(lname.text)
            if license_list:
                component_data['licenses'] = license_list

        components.append(component_data)
    return components, None


def parse_bom_metadata(xml_bytes):
    """Parse metadata section from BOM XML (secure parser)."""
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        dtd_validation=False,
        load_dtd=False
    )
    try:
        doc = etree.fromstring(xml_bytes, parser)
    except etree.XMLSyntaxError:
        return {}

    nsmap = doc.nsmap
    default_ns = nsmap.get(None, '')
    ns = {'bom': default_ns} if default_ns else {}
    prefix = 'bom:' if default_ns else ''

    metadata = {}
    meta_elem = doc.find(f'{prefix}metadata', ns) if default_ns else doc.find('metadata')
    if meta_elem is not None:
        ts = meta_elem.find(f'{prefix}timestamp', ns) if default_ns else meta_elem.find('timestamp')
        if ts is not None and ts.text:
            metadata['timestamp'] = ts.text

        comp = meta_elem.find(f'{prefix}component', ns) if default_ns else meta_elem.find('component')
        if comp is not None:
            metadata['component'] = {
                'type': comp.get('type', ''),
                'name': (comp.find(f'{prefix}name', ns) if default_ns else comp.find('name')).text if (comp.find(f'{prefix}name', ns) if default_ns else comp.find('name')) is not None else '',
                'version': (comp.find(f'{prefix}version', ns) if default_ns else comp.find('version')).text if (comp.find(f'{prefix}version', ns) if default_ns else comp.find('version')) is not None else '',
            }

    serial = doc.get('serialNumber', '')
    if serial:
        metadata['serialNumber'] = serial
    version = doc.get('version', '')
    if version:
        metadata['bomVersion'] = version

    return metadata


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/bom/upload', methods=['POST'])
def upload_bom():
    """Upload and analyze a CycloneDX BOM file."""
    if 'file' not in request.files and 'bom' not in request.form:
        return jsonify({'error': 'No BOM provided. Use file upload or paste XML in bom field.'}), 400

    xml_bytes = None
    filename = 'inline-bom.xml'

    if 'file' in request.files:
        f = request.files['file']
        if f.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        filename = secure_filename(f.filename)
        xml_bytes = f.read()
    elif 'bom' in request.form:
        xml_bytes = request.form['bom'].encode('utf-8')

    if not xml_bytes or len(xml_bytes) == 0:
        return jsonify({'error': 'Empty BOM data'}), 400

    # Step 1: Identify schema version by extracting namespace declarations
    extraction = extract_all_namespace_declarations(xml_bytes)
    schema_version = None
    for ns in extraction.get('namespaces', []):
        if ns in SUPPORTED_SCHEMA_VERSIONS:
            schema_version = SUPPORTED_SCHEMA_VERSIONS[ns]
            break

    if schema_version is None:
        return jsonify({
            'error': 'Unable to determine CycloneDX schema version. Ensure the BOM uses a supported namespace.',
            'supported_versions': list(SUPPORTED_SCHEMA_VERSIONS.values())
        }), 400

    # Step 2: Parse components with secure parser
    components, parse_error = parse_bom_components(xml_bytes)
    if parse_error:
        return jsonify({'error': f'Failed to parse BOM: {parse_error}'}), 400

    # Step 3: Extract metadata
    metadata = parse_bom_metadata(xml_bytes)

    # Store the analysis result
    bom_id = str(uuid.uuid4())
    sha256_hash = hashlib.sha256(xml_bytes).hexdigest()

    analysis = {
        'id': bom_id,
        'filename': filename,
        'schema_version': schema_version,
        'sha256': sha256_hash,
        'uploaded_at': datetime.utcnow().isoformat() + 'Z',
        'metadata': metadata,
        'component_count': len(components),
        'components': components,
    }

    bom_store[bom_id] = analysis

    # Save the uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{bom_id}.xml')
    with open(filepath, 'wb') as out:
        out.write(xml_bytes)

    return jsonify({
        'status': 'success',
        'bom_id': bom_id,
        'schema_version': schema_version,
        'component_count': len(components),
        'sha256': sha256_hash,
    }), 201


@app.route('/api/v1/bom/<bom_id>', methods=['GET'])
def get_bom(bom_id):
    """Retrieve analysis results for a previously uploaded BOM."""
    if bom_id not in bom_store:
        return jsonify({'error': 'BOM not found'}), 404
    return jsonify(bom_store[bom_id])


@app.route('/api/v1/bom/<bom_id>/components', methods=['GET'])
def get_bom_components(bom_id):
    """List components from an analyzed BOM."""
    if bom_id not in bom_store:
        return jsonify({'error': 'BOM not found'}), 404
    analysis = bom_store[bom_id]
    return jsonify({
        'bom_id': bom_id,
        'schema_version': analysis['schema_version'],
        'components': analysis['components'],
        'total': analysis['component_count'],
    })


@app.route('/api/v1/bom/<bom_id>/export', methods=['GET'])
def export_bom(bom_id):
    """Download the original BOM XML file."""
    if bom_id not in bom_store:
        return jsonify({'error': 'BOM not found'}), 404
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{bom_id}.xml')
    if not os.path.exists(filepath):
        return jsonify({'error': 'BOM file not found on disk'}), 404
    return send_file(filepath, mimetype='application/xml', as_attachment=True,
                     download_name=bom_store[bom_id]['filename'])


@app.route('/api/v1/bom/validate', methods=['POST'])
def validate_bom():
    """
    Validate a CycloneDX BOM against its detected schema version.
    Returns validation results including detected namespaces.
    """
    if 'file' not in request.files and 'bom' not in request.form:
        return jsonify({'error': 'No BOM provided'}), 400

    xml_bytes = None
    if 'file' in request.files:
        f = request.files['file']
        if f.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        xml_bytes = f.read()
    elif 'bom' in request.form:
        xml_bytes = request.form['bom'].encode('utf-8')

    if not xml_bytes:
        return jsonify({'error': 'Empty BOM data'}), 400

    # Extract namespaces and metadata to identify schema version
    extraction = extract_all_namespace_declarations(xml_bytes)
    namespaces = extraction.get('namespaces', [])
    schema_version = None
    for ns in namespaces:
        if ns in SUPPORTED_SCHEMA_VERSIONS:
            schema_version = SUPPORTED_SCHEMA_VERSIONS[ns]
            break

    validation_result = {
        'valid': schema_version is not None,
        'detected_namespaces': namespaces,
        'schema_version': schema_version,
        'root_element': extraction.get('root_tag'),
        'root_attributes': extraction.get('root_attributes', {}),
        'metadata_preview': extraction.get('metadata_texts', []),
    }

    if schema_version is None:
        validation_result['errors'] = ['No supported CycloneDX namespace found']
    else:
        # Additional structural validation with secure parser
        secure_parser = etree.XMLParser(
            resolve_entities=False,
            no_network=True,
            dtd_validation=False,
            load_dtd=False
        )
        try:
            doc = etree.fromstring(xml_bytes, secure_parser)
            root_tag = etree.QName(doc.tag).localname if '}' in doc.tag else doc.tag
            if root_tag != 'bom':
                validation_result['valid'] = False
                validation_result['errors'] = [f'Root element must be "bom", found "{root_tag}"']
            else:
                validation_result['errors'] = []
        except etree.XMLSyntaxError as e:
            validation_result['valid'] = False
            validation_result['errors'] = [f'XML syntax error: {str(e)}']

    return jsonify(validation_result)


@app.route('/api/v1/bom/list', methods=['GET'])
def list_boms():
    """List all analyzed BOMs."""
    results = []
    for bom_id, analysis in bom_store.items():
        results.append({
            'id': analysis['id'],
            'filename': analysis['filename'],
            'schema_version': analysis['schema_version'],
            'component_count': analysis['component_count'],
            'uploaded_at': analysis['uploaded_at'],
            'sha256': analysis['sha256'],
        })
    return jsonify({'boms': results, 'total': len(results)})


@app.route('/api/v1/schema/versions', methods=['GET'])
def schema_versions():
    """List supported CycloneDX schema versions."""
    return jsonify({
        'supported_versions': list(SUPPORTED_SCHEMA_VERSIONS.values()),
        'namespaces': SUPPORTED_SCHEMA_VERSIONS,
    })


@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
