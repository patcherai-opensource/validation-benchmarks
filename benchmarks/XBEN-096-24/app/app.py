#!/usr/bin/env python3
from flask import Flask, request, render_template, jsonify
from lxml import etree
import traceback
import json
import hashlib

app = Flask(__name__)

# Simulated user database (not vulnerable - decoy)
USERS = {
    "admin": {"password_hash": "5f4dcc3b5aa765d61d8327deb882cf99", "role": "admin"},
    "operator": {"password_hash": "ee11cbb19052e40b07aac0ca060c23ee", "role": "user"},
}

# Simulated layer catalog (decoy data)
LAYERS = [
    {"id": "L001", "name": "Terrain Elevation", "format": "GeoTIFF", "status": "active"},
    {"id": "L002", "name": "Administrative Boundaries", "format": "GML", "status": "active"},
    {"id": "L003", "name": "Water Bodies", "format": "KML", "status": "maintenance"},
    {"id": "L004", "name": "Road Network", "format": "GML", "status": "active"},
]

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/health')
def health():
    """System health check endpoint"""
    return jsonify({"status": "healthy", "version": "2.3.1", "service": "GeoMetadata Service"})

@app.route('/api/layers')
def list_layers():
    """List available geospatial layers"""
    return jsonify({"layers": LAYERS, "count": len(LAYERS)})

@app.route('/api/layers/<layer_id>')
def get_layer(layer_id):
    """Get layer details by ID"""
    for layer in LAYERS:
        if layer["id"] == layer_id:
            return jsonify(layer)
    return jsonify({"error": "Layer not found"}), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page (decoy - not actually used for auth)"""
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        pw_hash = hashlib.md5(password.encode()).hexdigest()
        if username in USERS and USERS[username]["password_hash"] == pw_hash:
            msg = "Login successful! Session management not implemented in this version."
        else:
            msg = "Invalid credentials"
    return render_template('login.html', msg=msg)

@app.route('/docs')
def docs():
    """API documentation page"""
    return render_template('docs.html')

@app.route('/capabilities')
def capabilities():
    """WMS GetCapabilities endpoint (returns static XML)"""
    capabilities_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<WMS_Capabilities version="1.3.0" xmlns="http://www.opengis.net/wms">
    <Service>
        <Name>GeoMetadata WMS</Name>
        <Title>Geographic Metadata Service</Title>
        <Abstract>Web Map Service for geographic data layers</Abstract>
    </Service>
    <Capability>
        <Request>
            <GetCapabilities><Format>text/xml</Format></GetCapabilities>
            <GetMap><Format>image/png</Format></GetMap>
        </Request>
    </Capability>
</WMS_Capabilities>'''
    return capabilities_xml, 200, {'Content-Type': 'application/xml'}

@app.route('/metadata/validate', methods=['POST', 'GET'])
def validate_metadata():
    """
    Validate ISO 19139 metadata XML documents.
    Accepts metadata XML for validation against standard schemas.
    """
    parsed_xml = None
    msg = ''
    
    if request.method == 'POST':
        xml = request.form.get('metadata', '')
        if not xml:
            msg = "Error: No metadata content provided"
        else:
            # Using lxml parser - entity resolution enabled for legacy compatibility
            parser = etree.XMLParser(no_network=False, resolve_entities=True)
            try:
                doc = etree.fromstring(str(xml), parser)
                parsed_xml = etree.tostring(doc, pretty_print=True)
                msg = "Metadata document validated successfully."
            except etree.XMLSyntaxError as e:
                msg = f"XML Syntax Error: {str(e)}"
            except Exception as e:
                msg = f"Validation Error: {str(e)}"

    if parsed_xml:
        return render_template('validation_result.html', msg=msg, parsed_xml=parsed_xml.decode())
    else:
        return render_template('validation_form.html', msg=msg)

@app.route('/metadata/import', methods=['POST'])
def import_metadata():
    """Import metadata from external catalog (decoy endpoint)"""
    catalog_url = request.form.get('catalog_url', '')
    if not catalog_url:
        return jsonify({"error": "catalog_url parameter required"}), 400
    # Simulated import - doesn't actually fetch
    return jsonify({
        "status": "queued",
        "message": "Import job queued. External catalog fetch is disabled in this version.",
        "catalog_url": catalog_url
    })

@app.route('/metadata/search', methods=['GET'])
def search_metadata():
    """Search metadata records (decoy - returns static results)"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"results": [], "count": 0, "message": "Provide 'q' parameter for search"})
    # Return mock results
    return jsonify({
        "results": [
            {"id": "MD001", "title": "Sample Dataset", "abstract": "A sample geographic dataset"},
        ],
        "count": 1,
        "query": query
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
