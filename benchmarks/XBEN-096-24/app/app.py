#!/usr/bin/env python3
"""
GeoData Catalog Service - Internal XML Processing API
Handles metadata records in OGC/ISO 19115 compatible formats
"""
from flask import Flask, request, render_template, jsonify
from lxml import etree
import logging
import os

app = Flask(__name__)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_xml_parser():
    """
    Returns configured XML parser for processing OGC metadata records.
    Uses lxml for performance with large geospatial metadata documents.
    """
    return etree.XMLParser(resolve_entities=True)


def parse_metadata_record(xml_content):
    """
    Parse an XML metadata record and extract key fields.
    Supports OGC CSW and ISO 19115 metadata formats.
    """
    parser = get_xml_parser()
    doc = etree.fromstring(xml_content.encode('utf-8') if isinstance(xml_content, str) else xml_content, parser)
    return doc


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/catalog')
def catalog():
    return render_template('catalog.html')


@app.route('/api/records', methods=['GET'])
def list_records():
    """List available metadata records in the catalog"""
    records = [
        {"id": "rec-001", "title": "Urban Land Use Dataset 2023", "type": "vector"},
        {"id": "rec-002", "title": "Satellite Imagery Archive", "type": "raster"},
        {"id": "rec-003", "title": "Climate Monitoring Stations", "type": "observation"},
    ]
    return jsonify({"records": records, "total": len(records)})


@app.route('/api/records/upload', methods=['POST', 'GET'])
def upload_record():
    """
    Upload a new metadata record to the catalog.
    Accepts XML metadata in OGC/ISO 19115 format.
    """
    parsed_xml = None
    message = ''
    error = False
    
    if request.method == 'POST':
        xml_content = request.form.get('xml', '')
        
        if not xml_content.strip():
            return render_template('upload.html', 
                                 message='No XML content provided', 
                                 error=True,
                                 endpoint='/api/records/upload')
        
        try:
            doc = parse_metadata_record(xml_content)
            parsed_xml = etree.tostring(doc, pretty_print=True).decode('utf-8')
            message = "Metadata record validated and indexed successfully."
        except etree.XMLSyntaxError as e:
            logger.warning(f"XML parsing error: {e}")
            message = "Invalid XML format. Please check your metadata document."
            error = True
        except Exception as e:
            logger.error(f"Unexpected error processing record: {e}")
            message = "An error occurred while processing your request."
            error = True

    if parsed_xml:
        return render_template('result.html', 
                             message=message, 
                             parsed_xml=parsed_xml,
                             record_id="rec-" + os.urandom(4).hex())
    else:
        return render_template('upload.html', 
                             message=message, 
                             error=error,
                             endpoint='/api/records/upload')


@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "geodata-catalog"})


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
