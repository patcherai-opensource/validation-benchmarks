#!/usr/bin/env python3
"""PyWPS Geospatial Processing Service

A lightweight OGC Web Processing Service (WPS) implementation
for geospatial data processing operations.
"""
import os
import uuid
import logging
from datetime import datetime
from flask import Flask, request, Response, render_template
from lxml import etree

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('pywps')

# XML parser configuration for WPS request handling
XML_PARSER = etree.XMLParser(
    resolve_entities=True,
    no_network=False,
    load_dtd=True,
)

WPS_VERSION = '1.0.0'
OWS_VERSION = '1.1'
SERVICE_TITLE = 'PyWPS Geospatial Processing Service'
SERVICE_ABSTRACT = 'OGC Web Processing Service for geospatial data analysis and transformation'
PROVIDER_NAME = 'GeoProcessing Solutions'
SERVICE_URL = os.environ.get('SERVICE_URL', 'http://localhost:5000/wps')

WPS_NS = 'http://www.opengis.net/wps/1.0.0'
OWS_NS = 'http://www.opengis.net/ows/1.1'
XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
XLINK_NS = 'http://www.w3.org/1999/xlink'

NSMAP = {
    'wps': WPS_NS,
    'ows': OWS_NS,
    'xsi': XSI_NS,
    'xlink': XLINK_NS,
}

PROCESSES = {
    'buffer': {
        'identifier': 'buffer',
        'title': 'Buffer Process',
        'abstract': 'Creates a buffer around a geometry with a specified distance.',
        'inputs': [
            {'identifier': 'geometry', 'title': 'Input Geometry', 'type': 'ComplexData',
             'abstract': 'GML or WKT geometry to buffer', 'mimetypes': ['application/gml+xml', 'text/plain']},
            {'identifier': 'distance', 'title': 'Buffer Distance', 'type': 'LiteralData',
             'abstract': 'Distance for the buffer in map units', 'datatype': 'float'},
        ],
        'outputs': [
            {'identifier': 'result', 'title': 'Buffered Geometry', 'type': 'ComplexData',
             'abstract': 'The resulting buffered geometry', 'mimetypes': ['application/gml+xml']},
        ],
    },
    'intersection': {
        'identifier': 'intersection',
        'title': 'Intersection Process',
        'abstract': 'Computes the geometric intersection of two input geometries.',
        'inputs': [
            {'identifier': 'geometry_a', 'title': 'First Geometry', 'type': 'ComplexData',
             'abstract': 'First input geometry', 'mimetypes': ['application/gml+xml']},
            {'identifier': 'geometry_b', 'title': 'Second Geometry', 'type': 'ComplexData',
             'abstract': 'Second input geometry', 'mimetypes': ['application/gml+xml']},
        ],
        'outputs': [
            {'identifier': 'result', 'title': 'Intersection Result', 'type': 'ComplexData',
             'abstract': 'The intersection of the two geometries', 'mimetypes': ['application/gml+xml']},
        ],
    },
    'centroid': {
        'identifier': 'centroid',
        'title': 'Centroid Process',
        'abstract': 'Calculates the centroid of an input geometry.',
        'inputs': [
            {'identifier': 'geometry', 'title': 'Input Geometry', 'type': 'ComplexData',
             'abstract': 'Input geometry to compute centroid for', 'mimetypes': ['application/gml+xml', 'text/plain']},
        ],
        'outputs': [
            {'identifier': 'result', 'title': 'Centroid Point', 'type': 'ComplexData',
             'abstract': 'The centroid of the input geometry', 'mimetypes': ['application/gml+xml']},
        ],
    },
    'simplify': {
        'identifier': 'simplify',
        'title': 'Simplify Process',
        'abstract': 'Simplifies a geometry using the Douglas-Peucker algorithm.',
        'inputs': [
            {'identifier': 'geometry', 'title': 'Input Geometry', 'type': 'ComplexData',
             'abstract': 'Geometry to simplify', 'mimetypes': ['application/gml+xml', 'text/plain']},
            {'identifier': 'tolerance', 'title': 'Simplification Tolerance', 'type': 'LiteralData',
             'abstract': 'Maximum distance from original geometry', 'datatype': 'float'},
        ],
        'outputs': [
            {'identifier': 'result', 'title': 'Simplified Geometry', 'type': 'ComplexData',
             'abstract': 'The simplified geometry', 'mimetypes': ['application/gml+xml']},
        ],
    },
}


def _get_capabilities_response():
    root = etree.Element('{%s}Capabilities' % WPS_NS, nsmap=NSMAP)
    root.set('version', WPS_VERSION)
    root.set('service', 'WPS')

    si = etree.SubElement(root, '{%s}ServiceIdentification' % OWS_NS)
    etree.SubElement(si, '{%s}Title' % OWS_NS).text = SERVICE_TITLE
    etree.SubElement(si, '{%s}Abstract' % OWS_NS).text = SERVICE_ABSTRACT
    etree.SubElement(si, '{%s}ServiceType' % OWS_NS).text = 'WPS'
    etree.SubElement(si, '{%s}ServiceTypeVersion' % OWS_NS).text = WPS_VERSION

    sp = etree.SubElement(root, '{%s}ServiceProvider' % OWS_NS)
    etree.SubElement(sp, '{%s}ProviderName' % OWS_NS).text = PROVIDER_NAME

    om = etree.SubElement(root, '{%s}OperationsMetadata' % OWS_NS)
    for op_name in ['GetCapabilities', 'DescribeProcess', 'Execute']:
        op = etree.SubElement(om, '{%s}Operation' % OWS_NS)
        op.set('name', op_name)
        dcp = etree.SubElement(op, '{%s}DCP' % OWS_NS)
        http = etree.SubElement(dcp, '{%s}HTTP' % OWS_NS)
        get_el = etree.SubElement(http, '{%s}Get' % OWS_NS)
        get_el.set('{%s}href' % XLINK_NS, SERVICE_URL)
        post_el = etree.SubElement(http, '{%s}Post' % OWS_NS)
        post_el.set('{%s}href' % XLINK_NS, SERVICE_URL)

    po = etree.SubElement(root, '{%s}ProcessOfferings' % WPS_NS)
    for proc_id, proc in PROCESSES.items():
        p = etree.SubElement(po, '{%s}Process' % WPS_NS)
        etree.SubElement(p, '{%s}Identifier' % OWS_NS).text = proc['identifier']
        etree.SubElement(p, '{%s}Title' % OWS_NS).text = proc['title']
        etree.SubElement(p, '{%s}Abstract' % OWS_NS).text = proc['abstract']

    lang = etree.SubElement(root, '{%s}Languages' % WPS_NS)
    default_lang = etree.SubElement(lang, '{%s}Default' % WPS_NS)
    etree.SubElement(default_lang, '{%s}Language' % OWS_NS).text = 'en-US'

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


def _describe_process_response(identifiers):
    root = etree.Element('{%s}ProcessDescriptions' % WPS_NS, nsmap=NSMAP)
    root.set('version', WPS_VERSION)
    root.set('service', 'WPS')

    for ident in identifiers:
        if ident not in PROCESSES:
            return _exception_response('InvalidParameterValue',
                                       'Unknown process identifier: {}'.format(ident),
                                       'identifier')
        proc = PROCESSES[ident]
        pd = etree.SubElement(root, '{%s}ProcessDescription' % WPS_NS)
        pd.set('storeSupported', 'true')
        pd.set('statusSupported', 'true')
        etree.SubElement(pd, '{%s}Identifier' % OWS_NS).text = proc['identifier']
        etree.SubElement(pd, '{%s}Title' % OWS_NS).text = proc['title']
        etree.SubElement(pd, '{%s}Abstract' % OWS_NS).text = proc['abstract']

        di = etree.SubElement(pd, 'DataInputs')
        for inp in proc['inputs']:
            inp_el = etree.SubElement(di, 'Input', minOccurs='1', maxOccurs='1')
            etree.SubElement(inp_el, '{%s}Identifier' % OWS_NS).text = inp['identifier']
            etree.SubElement(inp_el, '{%s}Title' % OWS_NS).text = inp['title']
            etree.SubElement(inp_el, '{%s}Abstract' % OWS_NS).text = inp['abstract']
            if inp['type'] == 'LiteralData':
                ld = etree.SubElement(inp_el, 'LiteralData')
                etree.SubElement(ld, '{%s}DataType' % OWS_NS).text = inp.get('datatype', 'string')
            elif inp['type'] == 'ComplexData':
                cd = etree.SubElement(inp_el, 'ComplexData')
                default = etree.SubElement(cd, 'Default')
                fmt = etree.SubElement(default, 'Format')
                etree.SubElement(fmt, 'MimeType').text = inp['mimetypes'][0]

        po = etree.SubElement(pd, 'ProcessOutputs')
        for outp in proc['outputs']:
            out_el = etree.SubElement(po, 'Output')
            etree.SubElement(out_el, '{%s}Identifier' % OWS_NS).text = outp['identifier']
            etree.SubElement(out_el, '{%s}Title' % OWS_NS).text = outp['title']
            etree.SubElement(out_el, '{%s}Abstract' % OWS_NS).text = outp['abstract']
            cd = etree.SubElement(out_el, 'ComplexOutput')
            default = etree.SubElement(cd, 'Default')
            fmt = etree.SubElement(default, 'Format')
            etree.SubElement(fmt, 'MimeType').text = outp['mimetypes'][0]

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


def _exception_response(code, text, locator=None, http_code=400):
    root = etree.Element('{%s}ExceptionReport' % OWS_NS, nsmap={'ows': OWS_NS})
    root.set('version', OWS_VERSION)
    exc = etree.SubElement(root, '{%s}Exception' % OWS_NS)
    exc.set('exceptionCode', code)
    if locator:
        exc.set('locator', locator)
    etree.SubElement(exc, '{%s}ExceptionText' % OWS_NS).text = text
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True), http_code


def _execute_process(doc):
    ns = {'wps': WPS_NS, 'ows': OWS_NS}

    identifier_el = doc.find('.//{%s}Identifier' % OWS_NS)
    if identifier_el is None:
        return _exception_response('MissingParameterValue', 'Missing process Identifier', 'Identifier')

    identifier = identifier_el.text
    if identifier not in PROCESSES:
        return _exception_response('InvalidParameterValue',
                                   'Unknown process: {}'.format(identifier), 'Identifier')

    proc = PROCESSES[identifier]
    process_uuid = str(uuid.uuid4())

    inputs = {}
    data_inputs = doc.find('.//{%s}DataInputs' % WPS_NS)
    if data_inputs is not None:
        for inp in data_inputs.findall('{%s}Input' % WPS_NS):
            inp_id_el = inp.find('{%s}Identifier' % OWS_NS)
            if inp_id_el is not None:
                inp_id = inp_id_el.text
                data_el = inp.find('{%s}Data' % WPS_NS)
                if data_el is not None:
                    literal = data_el.find('{%s}LiteralData' % WPS_NS)
                    complex_data = data_el.find('{%s}ComplexData' % WPS_NS)
                    if literal is not None:
                        inputs[inp_id] = literal.text or ''
                    elif complex_data is not None:
                        inputs[inp_id] = etree.tostring(complex_data, encoding='unicode')
                    else:
                        inputs[inp_id] = data_el.text or ''

    root = etree.Element('{%s}ExecuteResponse' % WPS_NS, nsmap=NSMAP)
    root.set('version', WPS_VERSION)
    root.set('service', 'WPS')
    root.set('serviceInstance', SERVICE_URL + '?service=WPS&request=GetCapabilities')
    root.set('statusLocation', SERVICE_URL + '?jobid=' + process_uuid)

    proc_el = etree.SubElement(root, '{%s}Process' % WPS_NS)
    etree.SubElement(proc_el, '{%s}Identifier' % OWS_NS).text = identifier
    etree.SubElement(proc_el, '{%s}Title' % OWS_NS).text = proc['title']

    status = etree.SubElement(root, '{%s}Status' % WPS_NS)
    status.set('creationTime', datetime.utcnow().isoformat() + 'Z')
    succeeded = etree.SubElement(status, '{%s}ProcessSucceeded' % WPS_NS)
    succeeded.text = 'Process completed successfully'

    di_echo = etree.SubElement(root, '{%s}DataInputs' % WPS_NS)
    for inp_id, inp_val in inputs.items():
        inp_el = etree.SubElement(di_echo, '{%s}Input' % WPS_NS)
        etree.SubElement(inp_el, '{%s}Identifier' % OWS_NS).text = inp_id
        etree.SubElement(inp_el, '{%s}Title' % OWS_NS).text = inp_id
        data = etree.SubElement(inp_el, '{%s}Data' % WPS_NS)
        lit = etree.SubElement(data, '{%s}LiteralData' % WPS_NS)
        lit.text = inp_val

    po = etree.SubElement(root, '{%s}ProcessOutputs' % WPS_NS)
    for outp in proc['outputs']:
        out_el = etree.SubElement(po, '{%s}Output' % WPS_NS)
        etree.SubElement(out_el, '{%s}Identifier' % OWS_NS).text = outp['identifier']
        etree.SubElement(out_el, '{%s}Title' % OWS_NS).text = outp['title']
        data = etree.SubElement(out_el, '{%s}Data' % WPS_NS)
        lit = etree.SubElement(data, '{%s}LiteralData' % WPS_NS)
        lit.text = 'Process {} completed. Inputs received: {}'.format(
            identifier, ', '.join('{}={}'.format(k, v[:100]) for k, v in inputs.items())
        )

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)


def _handle_get_request():
    service = request.args.get('service', '').upper()
    if service and service != 'WPS':
        body, code = _exception_response('InvalidParameterValue',
                                         'Parameter SERVICE [{}] not supported'.format(service), 'service')
        return Response(body, status=code, content_type='text/xml')

    req_type = request.args.get('request', '').lower()

    if req_type == 'getcapabilities':
        body = _get_capabilities_response()
        return Response(body, content_type='text/xml')
    elif req_type == 'describeprocess':
        identifier = request.args.get('identifier', '')
        if not identifier:
            body, code = _exception_response('MissingParameterValue',
                                             'Missing parameter: identifier', 'identifier')
            return Response(body, status=code, content_type='text/xml')
        identifiers = [i.strip() for i in identifier.split(',')]
        body = _describe_process_response(identifiers)
        if isinstance(body, tuple):
            return Response(body[0], status=body[1], content_type='text/xml')
        return Response(body, content_type='text/xml')
    elif req_type == 'execute':
        body, code = _exception_response('NoApplicableCode',
                                         'Execute requests must be submitted via HTTP POST')
        return Response(body, status=code, content_type='text/xml')
    elif not req_type:
        body = _get_capabilities_response()
        return Response(body, content_type='text/xml')
    else:
        body, code = _exception_response('InvalidParameterValue',
                                         'Unknown request type: {}'.format(req_type), 'request')
        return Response(body, status=code, content_type='text/xml')


def _handle_post_request():
    data = request.get_data()
    if not data:
        body, code = _exception_response('MissingParameterValue', 'Empty POST body')
        return Response(body, status=code, content_type='text/xml')

    try:
        doc = etree.fromstring(data, parser=XML_PARSER)
    except Exception as e:
        body, code = _exception_response('NoApplicableCode',
                                         'Error parsing XML request: {}'.format(str(e)))
        return Response(body, status=code, content_type='text/xml')

    tag = doc.tag
    if tag.endswith('}GetCapabilities') or tag == 'GetCapabilities':
        body = _get_capabilities_response()
        return Response(body, content_type='text/xml')
    elif tag.endswith('}DescribeProcess') or tag == 'DescribeProcess':
        ident_el = doc.find('.//{%s}Identifier' % OWS_NS)
        if ident_el is None:
            ident_el = doc.find('.//Identifier')
        identifiers = [ident_el.text] if ident_el is not None else []
        if not identifiers:
            body, code = _exception_response('MissingParameterValue',
                                             'Missing process Identifier', 'identifier')
            return Response(body, status=code, content_type='text/xml')
        body = _describe_process_response(identifiers)
        if isinstance(body, tuple):
            return Response(body[0], status=body[1], content_type='text/xml')
        return Response(body, content_type='text/xml')
    elif tag.endswith('}Execute') or tag == 'Execute':
        result = _execute_process(doc)
        if isinstance(result, tuple):
            return Response(result[0], status=result[1], content_type='text/xml')
        return Response(result, content_type='text/xml')
    else:
        body, code = _exception_response('InvalidParameterValue',
                                         'Unknown operation: {}'.format(tag))
        return Response(body, status=code, content_type='text/xml')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/wps', methods=['GET', 'POST'])
def wps_endpoint():
    if request.method == 'GET':
        return _handle_get_request()
    else:
        return _handle_post_request()


@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def not_found(e):
    body, code = _exception_response('NoApplicableCode', 'Resource not found', http_code=404)
    return Response(body, status=404, content_type='text/xml')


@app.errorhandler(405)
def method_not_allowed(e):
    body, code = _exception_response('NoApplicableCode', 'Method not allowed', http_code=405)
    return Response(body, status=405, content_type='text/xml')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
