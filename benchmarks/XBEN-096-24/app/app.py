#!/usr/bin/env python3
"""
GeoData Catalog Service - XML Data Import
A service for importing geospatial metadata in XML format.
Uses lxml for XML parsing (similar to OWSLib pattern).
"""
from flask import Flask, request, render_template
from lxml import etree
import traceback

app = Flask(__name__)

# Simulating OWSLib-style XML parsing setup
# CVE-2023-27476: OWSLib's XML parser did not disable entity resolution for lxml
# The vulnerable pattern is having entity resolution enabled without explicit disable
#
# Set default parser with resolve_entities=True (the vulnerable configuration)
# The fix would be: etree.set_default_parser(parser=etree.XMLParser(resolve_entities=False))
etree.set_default_parser(parser=etree.XMLParser(resolve_entities=True))

def parse_xml_data(xml_content):
    """
    Parse XML content using lxml (mimics OWSLib etree usage pattern).
    This is vulnerable because entity resolution is enabled (not disabled as per CVE fix).
    """
    # This is the vulnerable pattern from CVE-2023-27476:
    # Entity resolution is enabled, allowing XXE attacks
    doc = etree.fromstring(xml_content.encode() if isinstance(xml_content, str) else xml_content)
    return doc


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/import', methods=['POST', 'GET'])
def import_metadata():
    """
    Import geospatial metadata in XML format.
    Endpoint accepts XML data for catalog import.
    """
    parsed_xml = None
    msg = ''
    
    if request.method == 'POST':
        xml = request.form.get('xml', '')
        if not xml:
            msg = "Error: No XML data provided"
        else:
            try:
                # Vulnerable XML parsing - no entity resolution disabled
                doc = parse_xml_data(xml)
                parsed_xml = etree.tostring(doc, pretty_print=True)
                msg = "Metadata imported successfully!"
            except Exception as e:
                msg = f"Error parsing XML:\n<br>\n{traceback.format_exc()}"

    if parsed_xml:
        return render_template('result.html', msg=msg, parsed_xml=parsed_xml.decode())
    else:
        return render_template('form.html', msg=msg, endpoint='/import')


# Legacy endpoint for backward compatibility
@app.route('/addbook', methods=['POST', 'GET'])
def addbook():
    """Legacy endpoint - redirects to /import"""
    parsed_xml = None
    msg = ''
    
    if request.method == 'POST':
        xml = request.form.get('xml', '')
        if not xml:
            msg = "Error: No XML data provided"
        else:
            try:
                doc = parse_xml_data(xml)
                parsed_xml = etree.tostring(doc, pretty_print=True)
                msg = "Data processed successfully!"
            except Exception as e:
                msg = f"Error:\n<br>\n{traceback.format_exc()}"

    if parsed_xml:
        return render_template('result.html', msg=msg, parsed_xml=parsed_xml.decode())
    else:
        return render_template('form.html', msg=msg, endpoint='/addbook')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
