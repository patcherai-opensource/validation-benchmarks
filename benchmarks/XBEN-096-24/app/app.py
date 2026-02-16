#!/usr/bin/env python3
import os
import uuid
import json
import datetime
from io import BytesIO

from flask import Flask, request, render_template, jsonify, redirect, url_for
from lxml import etree
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

SUPPORTED_SPEC_VERSIONS = {
    'http://cyclonedx.org/schema/bom/1.0': '1.0',
    'http://cyclonedx.org/schema/bom/1.1': '1.1',
    'http://cyclonedx.org/schema/bom/1.2': '1.2',
    'http://cyclonedx.org/schema/bom/1.3': '1.3',
    'http://cyclonedx.org/schema/bom/1.4': '1.4',
    'http://cyclonedx.org/schema/bom/1.5': '1.5',
    'http://cyclonedx.org/schema/bom/1.6': '1.6',
}

bom_store = {}


def _resolve_and_parse(raw_xml_bytes):
    """
    Pre-process the BOM document to resolve namespace declarations and
    identify the schema version. Parses the XML and returns the root
    element tree for further processing.
    """
    parser = etree.XMLParser(resolve_entities=True, no_network=False)
    tree = etree.parse(BytesIO(raw_xml_bytes), parser)
    return tree


def detect_spec_version(tree):
    """
    Identify the CycloneDX spec version from the parsed document's namespace
    declarations.
    """
    root = tree.getroot()
    namespaces = root.nsmap
    all_ns = set()
    for prefix, uri in namespaces.items():
        all_ns.add(uri)
    for ns_uri, version_str in SUPPORTED_SPEC_VERSIONS.items():
        if ns_uri in all_ns:
            return version_str
    return None


def extract_components(tree):
    """
    Walk the parsed element tree and extract component metadata.
    """
    root = tree.getroot()
    ns = root.nsmap.get(None, '')
    nsmap = {'bom': ns} if ns else {}

    components = []
    comp_elements = root.findall('.//bom:component', nsmap) if nsmap else root.findall('.//component')
    for comp in comp_elements:
        name_el = comp.find('bom:name', nsmap) if nsmap else comp.find('name')
        version_el = comp.find('bom:version', nsmap) if nsmap else comp.find('version')
        type_attr = comp.get('type', 'library')
        purl_el = comp.find('bom:purl', nsmap) if nsmap else comp.find('purl')
        license_el = comp.find('bom:licenses/bom:license/bom:id', nsmap) if nsmap else comp.find('licenses/license/id')
        desc_el = comp.find('bom:description', nsmap) if nsmap else comp.find('description')
        components.append({
            'name': name_el.text if name_el is not None else 'unknown',
            'version': version_el.text if version_el is not None else 'unknown',
            'type': type_attr,
            'purl': purl_el.text if purl_el is not None else None,
            'license': license_el.text if license_el is not None else None,
            'description': desc_el.text if desc_el is not None else None,
        })

    serial_number = root.get('serialNumber', None)
    bom_version = root.get('version', '1')

    return {
        'serial_number': serial_number,
        'bom_version': bom_version,
        'components': components,
        'component_count': len(components),
    }


def process_bom(raw_xml_bytes):
    """
    Full BOM processing pipeline: resolve namespaces, detect version,
    and extract components.
    """
    tree = _resolve_and_parse(raw_xml_bytes)
    spec_version = detect_spec_version(tree)
    if spec_version is None:
        return None, None
    bom_data = extract_components(tree)
    return spec_version, bom_data


@app.route('/')
def index():
    return render_template('index.html', bom_count=len(bom_store))


@app.route('/api/v1/health')
def health_check():
    return jsonify({'status': 'ok', 'service': 'sbom-manager', 'version': '2.4.1'})


@app.route('/upload', methods=['GET', 'POST'])
def upload_bom():
    if request.method == 'GET':
        return render_template('upload.html')

    raw_bytes = None
    filename = 'unknown.xml'

    if 'file' in request.files and request.files['file'].filename:
        f = request.files['file']
        filename = secure_filename(f.filename)
        raw_bytes = f.read()
    elif request.form.get('xml_content'):
        raw_bytes = request.form['xml_content'].encode('utf-8')
        filename = 'inline-bom.xml'
    else:
        return render_template('upload.html', error='No BOM data provided. Upload a file or paste XML content.'), 400

    if not raw_bytes or not raw_bytes.strip():
        return render_template('upload.html', error='Empty BOM content.'), 400

    try:
        spec_version, bom_data = process_bom(raw_bytes)
    except etree.XMLSyntaxError:
        return render_template('upload.html', error='Invalid XML syntax.'), 400
    except Exception:
        return render_template('upload.html', error='Failed to process BOM document.'), 400

    if spec_version is None:
        return render_template('upload.html',
            error='Unable to determine specification version. Ensure the BOM uses a valid CycloneDX namespace.'), 400

    bom_id = str(uuid.uuid4())
    entry = {
        'id': bom_id,
        'filename': filename,
        'spec_version': spec_version,
        'uploaded_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'serial_number': bom_data.get('serial_number'),
        'bom_version': bom_data.get('bom_version'),
        'component_count': bom_data.get('component_count', 0),
        'components': bom_data.get('components', []),
        'raw_size': len(raw_bytes),
    }
    bom_store[bom_id] = entry

    return redirect(url_for('view_bom', bom_id=bom_id))


@app.route('/bom/<bom_id>')
def view_bom(bom_id):
    entry = bom_store.get(bom_id)
    if not entry:
        return render_template('error.html', message='BOM not found.'), 404
    return render_template('bom_detail.html', bom=entry)


@app.route('/api/v1/bom', methods=['POST'])
def api_upload_bom():
    content_type = request.content_type or ''
    if 'xml' in content_type or 'octet-stream' in content_type:
        raw_bytes = request.get_data()
    elif 'multipart' in content_type and 'file' in request.files:
        raw_bytes = request.files['file'].read()
    else:
        return jsonify({'error': 'Unsupported content type. Send XML BOM as application/xml or multipart upload.'}), 415

    if not raw_bytes or not raw_bytes.strip():
        return jsonify({'error': 'Empty BOM content.'}), 400

    try:
        spec_version, bom_data = process_bom(raw_bytes)
    except etree.XMLSyntaxError:
        return jsonify({'error': 'Invalid XML syntax.'}), 400
    except Exception:
        return jsonify({'error': 'Failed to process BOM document.'}), 400

    if spec_version is None:
        return jsonify({'error': 'Unable to determine specification version.'}), 400

    bom_id = str(uuid.uuid4())
    entry = {
        'id': bom_id,
        'spec_version': spec_version,
        'uploaded_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'serial_number': bom_data.get('serial_number'),
        'bom_version': bom_data.get('bom_version'),
        'component_count': bom_data.get('component_count', 0),
        'components': bom_data.get('components', []),
    }
    bom_store[bom_id] = entry

    return jsonify({'id': bom_id, 'spec_version': spec_version, 'component_count': entry['component_count'],
                    'components': entry['components']}), 201


@app.route('/api/v1/bom/<bom_id>')
def api_get_bom(bom_id):
    entry = bom_store.get(bom_id)
    if not entry:
        return jsonify({'error': 'BOM not found.'}), 404
    return jsonify(entry)


@app.route('/api/v1/boms')
def api_list_boms():
    items = []
    for bom_id, entry in bom_store.items():
        items.append({
            'id': entry['id'],
            'spec_version': entry.get('spec_version'),
            'component_count': entry.get('component_count', 0),
            'uploaded_at': entry.get('uploaded_at'),
        })
    return jsonify({'total': len(items), 'items': items})


@app.route('/inventory')
def inventory():
    return render_template('inventory.html', boms=bom_store.values())


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found.'}), 404
    return render_template('error.html', message='Page not found.'), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error.'}), 500
    return render_template('error.html', message='An internal error occurred.'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
