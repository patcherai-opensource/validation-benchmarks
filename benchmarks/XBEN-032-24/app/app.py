import logging
import json
import os
from flask import Flask, request, Response, render_template, jsonify
from geodata.xmltools import etree
from geodata.catalogue import CatalogueEngine
from geodata.capabilities import get_capabilities_document
from geodata.namespaces import GDC_NAMESPACES

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize catalogue engine with sample geospatial metadata records
catalogue = CatalogueEngine()


@app.route('/')
def landing_page():
    """OGC Catalogue Service landing page"""
    return render_template('landing.html',
                           title='GeoData Catalogue Service',
                           version=catalogue.version)


@app.route('/health')
def health():
    return Response('OK', status=200, mimetype='text/plain')


@app.route('/catalogue/capabilities', methods=['GET'])
def capabilities():
    """GetCapabilities - returns service metadata"""
    fmt = request.args.get('f', 'xml')
    caps_doc = get_capabilities_document(catalogue)
    if fmt == 'json':
        return jsonify({
            'service': 'GDC',
            'version': catalogue.version,
            'title': catalogue.title,
            'abstract': catalogue.abstract,
            'operations': ['GetCapabilities', 'GetRecords', 'GetRecordById', 'DescribeRecord'],
            'filters': ['PropertyIsEqualTo', 'PropertyIsLike', 'BBOX', 'And', 'Or']
        })
    return Response(caps_doc, status=200, mimetype='application/xml')


@app.route('/catalogue/collections', methods=['GET'])
def collections():
    """List available metadata collections"""
    result = catalogue.list_collections()
    fmt = request.args.get('f', 'json')
    if fmt == 'xml':
        xml_out = '<Collections xmlns="http://geodata.example.com/gdc">\n'
        for c in result:
            xml_out += f'  <Collection id="{c["id"]}">\n'
            xml_out += f'    <Title>{c["title"]}</Title>\n'
            xml_out += f'    <Description>{c["description"]}</Description>\n'
            xml_out += f'    <RecordCount>{c["count"]}</RecordCount>\n'
            xml_out += f'  </Collection>\n'
        xml_out += '</Collections>'
        return Response(xml_out, status=200, mimetype='application/xml')
    return jsonify({'collections': result})


@app.route('/catalogue/collections/<collection_id>/items', methods=['GET'])
def collection_items(collection_id):
    """Get items from a collection"""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    items = catalogue.get_items(collection_id, limit=limit, offset=offset)
    if items is None:
        return jsonify({'error': 'Collection not found'}), 404
    return jsonify({
        'type': 'FeatureCollection',
        'numberMatched': len(items),
        'numberReturned': len(items),
        'features': items
    })


@app.route('/catalogue/collections/<collection_id>/items/<item_id>', methods=['GET'])
def collection_item(collection_id, item_id):
    """Get a single item from a collection"""
    item = catalogue.get_item(collection_id, item_id)
    if item is None:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(item)


@app.route('/catalogue/query', methods=['POST'])
def query_records():
    """
    Execute an XML filter query against the catalogue.

    Accepts OGC-style filter XML to search metadata records.
    Supports PropertyIsEqualTo, PropertyIsLike, and BBOX filters.
    """
    content_type = request.content_type or ''
    if 'xml' not in content_type.lower() and 'text' not in content_type.lower():
        return Response(
            '<ExceptionReport><Exception>'
            'Unsupported content type. Expected application/xml'
            '</Exception></ExceptionReport>',
            status=400, mimetype='application/xml'
        )

    xml_data = request.data
    if not xml_data:
        return Response(
            '<ExceptionReport><Exception>'
            'Empty request body'
            '</Exception></ExceptionReport>',
            status=400, mimetype='application/xml'
        )

    try:
        root = etree.fromstring(xml_data)
    except Exception as e:
        return Response(
            f'<ExceptionReport><Exception>'
            f'Invalid XML: {str(e)}'
            f'</Exception></ExceptionReport>',
            status=400, mimetype='application/xml'
        )

    try:
        results, search_context = catalogue.execute_query(root)
        response_xml = build_query_response(results, search_context)
        return Response(response_xml, status=200, mimetype='application/xml')
    except Exception as e:
        logger.warning(f'Query execution error: {type(e).__name__}')
        return Response(
            '<ExceptionReport><Exception>'
            'Error processing query'
            '</Exception></ExceptionReport>',
            status=500, mimetype='application/xml'
        )


@app.route('/catalogue/describe', methods=['GET'])
def describe_record():
    """DescribeRecord - returns schema information"""
    typename = request.args.get('typeName', 'gdc:Record')
    schema_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<DescribeRecordResponse xmlns="http://geodata.example.com/gdc">
  <SchemaComponent targetNamespace="http://geodata.example.com/gdc"
                   schemaLanguage="http://www.w3.org/2001/XMLSchema">
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
               targetNamespace="http://geodata.example.com/gdc">
      <xs:element name="Record">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="identifier" type="xs:string"/>
            <xs:element name="title" type="xs:string"/>
            <xs:element name="subject" type="xs:string" maxOccurs="unbounded"/>
            <xs:element name="description" type="xs:string"/>
            <xs:element name="type" type="xs:string"/>
            <xs:element name="format" type="xs:string"/>
            <xs:element name="bbox" minOccurs="0">
              <xs:complexType>
                <xs:sequence>
                  <xs:element name="westBoundLongitude" type="xs:decimal"/>
                  <xs:element name="eastBoundLongitude" type="xs:decimal"/>
                  <xs:element name="southBoundLatitude" type="xs:decimal"/>
                  <xs:element name="northBoundLatitude" type="xs:decimal"/>
                </xs:sequence>
              </xs:complexType>
            </xs:element>
          </xs:sequence>
        </xs:complexType>
      </xs:element>
    </xs:schema>
  </SchemaComponent>
</DescribeRecordResponse>'''
    return Response(schema_xml, status=200, mimetype='application/xml')


def build_query_response(results, search_context=None):
    """Build XML response from query results"""
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<QueryResponse xmlns="http://geodata.example.com/gdc"\n'
    xml += '               xmlns:gdc="http://geodata.example.com/gdc"\n'
    xml += '               numberOfRecordsMatched="{}" numberOfRecordsReturned="{}">\n'.format(
        len(results), len(results)
    )
    if search_context:
        xml += '  <SearchStatus>\n'
        if 'requestedId' in search_context:
            xml += f'    <RequestedId>{_xml_escape(search_context["requestedId"])}</RequestedId>\n'
        if 'properties' in search_context:
            for prop in search_context['properties']:
                xml += f'    <SearchProperty>{_xml_escape(prop)}</SearchProperty>\n'
        if 'literals' in search_context:
            for lit in search_context['literals']:
                xml += f'    <SearchLiteral>{_xml_escape(lit)}</SearchLiteral>\n'
        xml += '  </SearchStatus>\n'
    for record in results:
        xml += '  <Record>\n'
        xml += f'    <identifier>{_xml_escape(record.get("identifier", ""))}</identifier>\n'
        xml += f'    <title>{_xml_escape(record.get("title", ""))}</title>\n'
        for subject in record.get('subjects', []):
            xml += f'    <subject>{_xml_escape(subject)}</subject>\n'
        xml += f'    <description>{_xml_escape(record.get("description", ""))}</description>\n'
        xml += f'    <type>{_xml_escape(record.get("type", ""))}</type>\n'
        xml += f'    <format>{_xml_escape(record.get("format", ""))}</format>\n'
        if 'bbox' in record:
            bbox = record['bbox']
            xml += '    <bbox>\n'
            xml += f'      <westBoundLongitude>{bbox[0]}</westBoundLongitude>\n'
            xml += f'      <eastBoundLongitude>{bbox[1]}</eastBoundLongitude>\n'
            xml += f'      <southBoundLatitude>{bbox[2]}</southBoundLatitude>\n'
            xml += f'      <northBoundLatitude>{bbox[3]}</northBoundLatitude>\n'
            xml += '    </bbox>\n'
        xml += '  </Record>\n'
    xml += '</QueryResponse>'
    return xml


def _xml_escape(text):
    """Escape special XML characters"""
    if text is None:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
