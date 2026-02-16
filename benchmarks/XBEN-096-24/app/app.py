#!/usr/bin/env python3
import logging
import configparser
import uuid as uuid_mod
import time
from flask import Flask, request, Response
from lxml import etree

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("GeoProcessingService")

app = Flask(__name__)

# -----------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------

CFG = configparser.ConfigParser()
CFG.add_section('metadata')
CFG.set('metadata', 'title', 'GeoNode Processing Service')
CFG.set('metadata', 'abstract',
        'OGC-compliant processing service for geospatial operations.')
CFG.set('metadata', 'keywords', 'GeoNode,OGC,WPS,processing,geospatial')
CFG.set('metadata', 'fees', 'NONE')
CFG.set('metadata', 'accessconstraints', 'NONE')
CFG.set('metadata', 'provider_name', 'GeoNode Foundation')
CFG.set('metadata', 'provider_url', 'https://geonode.org/')
CFG.set('metadata', 'contact_name', 'Admin')
CFG.set('metadata', 'contact_email', 'admin@geonode.org')

CFG.add_section('server')
CFG.set('server', 'url', 'http://localhost:5000/ows')
CFG.set('server', 'maxrequestsize', '5242880')
CFG.set('server', 'encoding', 'utf-8')
CFG.set('server', 'language', 'en-US')

SERVICE_VERSION = "1.2.3"

# -----------------------------------------------------------------------
# OGC / OWS namespaces
# -----------------------------------------------------------------------

NS_WPS = "http://www.opengis.net/wps/1.0.0"
NS_OWS = "http://www.opengis.net/ows/1.1"
NS_XLINK = "http://www.w3.org/1999/xlink"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"

NSMAP = {
    'wps': NS_WPS,
    'ows': NS_OWS,
    'xlink': NS_XLINK,
    'xsi': NS_XSI,
}

# -----------------------------------------------------------------------
# Process definitions (registered processing algorithms)
# -----------------------------------------------------------------------

PROCESSES = {
    'geo.buffer': {
        'identifier': 'geo.buffer',
        'title': 'Buffer',
        'abstract': 'Generate a buffer polygon around input geometry.',
        'version': '1.0.0',
        'inputs': [
            {'identifier': 'geometry', 'title': 'Input Geometry', 'type': 'complex',
             'abstract': 'GML geometry to buffer', 'formats': ['application/gml+xml']},
            {'identifier': 'distance', 'title': 'Buffer Distance', 'type': 'literal',
             'abstract': 'Distance of the buffer in map units', 'datatype': 'float'},
        ],
        'outputs': [
            {'identifier': 'result', 'title': 'Buffered Geometry', 'type': 'complex',
             'abstract': 'Resulting buffered geometry', 'formats': ['application/gml+xml']},
        ],
    },
    'geo.centroid': {
        'identifier': 'geo.centroid',
        'title': 'Centroid',
        'abstract': 'Compute centroid of input geometry.',
        'version': '1.0.0',
        'inputs': [
            {'identifier': 'geometry', 'title': 'Input Geometry', 'type': 'complex',
             'abstract': 'GML geometry', 'formats': ['application/gml+xml']},
        ],
        'outputs': [
            {'identifier': 'result', 'title': 'Centroid Point', 'type': 'complex',
             'abstract': 'Centroid point of input geometry', 'formats': ['application/gml+xml']},
        ],
    },
    'geo.area': {
        'identifier': 'geo.area',
        'title': 'Area Calculation',
        'abstract': 'Calculate area of input polygon geometry.',
        'version': '1.0.0',
        'inputs': [
            {'identifier': 'geometry', 'title': 'Input Geometry', 'type': 'complex',
             'abstract': 'GML polygon geometry', 'formats': ['application/gml+xml']},
        ],
        'outputs': [
            {'identifier': 'area', 'title': 'Computed Area', 'type': 'literal',
             'abstract': 'Area value in square map units', 'datatype': 'float'},
        ],
    },
    'geo.echo': {
        'identifier': 'geo.echo',
        'title': 'Echo Process',
        'abstract': 'Test process that echoes input data back as output for connectivity testing.',
        'version': '1.0.0',
        'inputs': [
            {'identifier': 'inputdata', 'title': 'Input Data', 'type': 'literal',
             'abstract': 'Any literal string value', 'datatype': 'string'},
        ],
        'outputs': [
            {'identifier': 'outputdata', 'title': 'Output Data', 'type': 'literal',
             'abstract': 'Echoed input data', 'datatype': 'string'},
        ],
    },
}


# -----------------------------------------------------------------------
# XML response helpers
# -----------------------------------------------------------------------

def xml_response(doc, status=200):
    return Response(doc, status=status, content_type='text/xml; charset=utf-8')


def ows_exception(code, text, locator="", http_status=400):
    doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.opengis.net/ows/1.1 '
        'http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" '
        'version="1.0.0">\n'
        '  <ows:Exception exceptionCode="{code}" locator="{locator}">\n'
        '    <ows:ExceptionText>{text}</ows:ExceptionText>\n'
        '  </ows:Exception>\n'
        '</ows:ExceptionReport>'
    ).format(code=code, locator=locator, text=text)
    return xml_response(doc, status=http_status)


# -----------------------------------------------------------------------
# GetCapabilities response builder
# -----------------------------------------------------------------------

def build_capabilities():
    svc_url = CFG.get('server', 'url')
    title = CFG.get('metadata', 'title')
    abstract = CFG.get('metadata', 'abstract')
    keywords = CFG.get('metadata', 'keywords').split(',')
    provider_name = CFG.get('metadata', 'provider_name')
    provider_url = CFG.get('metadata', 'provider_url')

    process_xml = ""
    for p in PROCESSES.values():
        process_xml += (
            '    <wps:Process wps:processVersion="{version}">\n'
            '      <ows:Identifier>{identifier}</ows:Identifier>\n'
            '      <ows:Title>{title}</ows:Title>\n'
            '      <ows:Abstract>{abstract}</ows:Abstract>\n'
            '    </wps:Process>\n'
        ).format(**p)

    kw_xml = "\n".join("      <ows:Keyword>{}</ows:Keyword>".format(k.strip()) for k in keywords)

    doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<wps:Capabilities service="WPS" version="1.0.0" xml:lang="en-US" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:wps="http://www.opengis.net/wps/1.0.0" '
        'xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 '
        '../wpsGetCapabilities_response.xsd" updateSequence="1">\n'
        '  <ows:ServiceIdentification>\n'
        '    <ows:Title>{title}</ows:Title>\n'
        '    <ows:Abstract>{abstract}</ows:Abstract>\n'
        '    <ows:Keywords>\n{keywords}\n    </ows:Keywords>\n'
        '    <ows:ServiceType>WPS</ows:ServiceType>\n'
        '    <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>\n'
        '    <ows:Fees>NONE</ows:Fees>\n'
        '    <ows:AccessConstraints>NONE</ows:AccessConstraints>\n'
        '  </ows:ServiceIdentification>\n'
        '  <ows:ServiceProvider>\n'
        '    <ows:ProviderName>{provider_name}</ows:ProviderName>\n'
        '    <ows:ProviderSite xlink:href="{provider_url}"/>\n'
        '  </ows:ServiceProvider>\n'
        '  <ows:OperationsMetadata>\n'
        '    <ows:Operation name="GetCapabilities">\n'
        '      <ows:DCP><ows:HTTP>\n'
        '        <ows:Get xlink:href="{svc_url}"/>\n'
        '        <ows:Post xlink:href="{svc_url}"/>\n'
        '      </ows:HTTP></ows:DCP>\n'
        '    </ows:Operation>\n'
        '    <ows:Operation name="DescribeProcess">\n'
        '      <ows:DCP><ows:HTTP>\n'
        '        <ows:Get xlink:href="{svc_url}"/>\n'
        '        <ows:Post xlink:href="{svc_url}"/>\n'
        '      </ows:HTTP></ows:DCP>\n'
        '    </ows:Operation>\n'
        '    <ows:Operation name="Execute">\n'
        '      <ows:DCP><ows:HTTP>\n'
        '        <ows:Get xlink:href="{svc_url}"/>\n'
        '        <ows:Post xlink:href="{svc_url}"/>\n'
        '      </ows:HTTP></ows:DCP>\n'
        '    </ows:Operation>\n'
        '  </ows:OperationsMetadata>\n'
        '  <wps:ProcessOfferings>\n{processes}'
        '  </wps:ProcessOfferings>\n'
        '  <wps:Languages>\n'
        '    <wps:Default><ows:Language>en-US</ows:Language></wps:Default>\n'
        '    <wps:Supported><ows:Language>en-US</ows:Language></wps:Supported>\n'
        '  </wps:Languages>\n'
        '</wps:Capabilities>\n'
    ).format(
        title=title, abstract=abstract, keywords=kw_xml,
        provider_name=provider_name, provider_url=provider_url,
        svc_url=svc_url, processes=process_xml,
    )
    return doc


# -----------------------------------------------------------------------
# DescribeProcess response builder
# -----------------------------------------------------------------------

def build_describe(identifiers):
    proc_xml_parts = []
    for ident in identifiers:
        p = PROCESSES.get(ident)
        if not p:
            return None, ident
        inputs_xml = ""
        for inp in p['inputs']:
            if inp['type'] == 'literal':
                inputs_xml += (
                    '      <Input minOccurs="1" maxOccurs="1">\n'
                    '        <ows:Identifier>{identifier}</ows:Identifier>\n'
                    '        <ows:Title>{title}</ows:Title>\n'
                    '        <ows:Abstract>{abstract}</ows:Abstract>\n'
                    '        <LiteralData>\n'
                    '          <ows:DataType ows:reference="xs:{datatype}">{datatype}</ows:DataType>\n'
                    '        </LiteralData>\n'
                    '      </Input>\n'
                ).format(**inp)
            else:
                fmt_xml = "\n".join(
                    '          <Format><MimeType>{}</MimeType></Format>'.format(f) for f in inp['formats']
                )
                inputs_xml += (
                    '      <Input minOccurs="1" maxOccurs="1">\n'
                    '        <ows:Identifier>{identifier}</ows:Identifier>\n'
                    '        <ows:Title>{title}</ows:Title>\n'
                    '        <ows:Abstract>{abstract}</ows:Abstract>\n'
                    '        <ComplexData>\n'
                    '          <Default>\n{fmts}\n          </Default>\n'
                    '        </ComplexData>\n'
                    '      </Input>\n'
                ).format(fmts=fmt_xml, **inp)

        outputs_xml = ""
        for out in p['outputs']:
            if out['type'] == 'literal':
                outputs_xml += (
                    '      <Output>\n'
                    '        <ows:Identifier>{identifier}</ows:Identifier>\n'
                    '        <ows:Title>{title}</ows:Title>\n'
                    '        <ows:Abstract>{abstract}</ows:Abstract>\n'
                    '        <LiteralOutput>\n'
                    '          <ows:DataType ows:reference="xs:{datatype}">{datatype}</ows:DataType>\n'
                    '        </LiteralOutput>\n'
                    '      </Output>\n'
                ).format(**out)
            else:
                fmt_xml = "\n".join(
                    '          <Format><MimeType>{}</MimeType></Format>'.format(f) for f in out['formats']
                )
                outputs_xml += (
                    '      <Output>\n'
                    '        <ows:Identifier>{identifier}</ows:Identifier>\n'
                    '        <ows:Title>{title}</ows:Title>\n'
                    '        <ows:Abstract>{abstract}</ows:Abstract>\n'
                    '        <ComplexOutput>\n'
                    '          <Default>\n{fmts}\n          </Default>\n'
                    '        </ComplexOutput>\n'
                    '      </Output>\n'
                ).format(fmts=fmt_xml, **out)

        proc_xml_parts.append(
            '  <ProcessDescription wps:processVersion="{version}" storeSupported="false" statusSupported="false">\n'
            '    <ows:Identifier>{identifier}</ows:Identifier>\n'
            '    <ows:Title>{title}</ows:Title>\n'
            '    <ows:Abstract>{abstract}</ows:Abstract>\n'
            '    <DataInputs>\n{inputs}'
            '    </DataInputs>\n'
            '    <ProcessOutputs>\n{outputs}'
            '    </ProcessOutputs>\n'
            '  </ProcessDescription>\n'.format(inputs=inputs_xml, outputs=outputs_xml, **p)
        )

    doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<wps:ProcessDescriptions service="WPS" version="1.0.0" xml:lang="en-US" '
        'xmlns:wps="http://www.opengis.net/wps/1.0.0" '
        'xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 '
        'http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd">\n'
        '{procs}'
        '</wps:ProcessDescriptions>\n'
    ).format(procs="".join(proc_xml_parts))
    return doc, None


# -----------------------------------------------------------------------
# Execute request processing
# -----------------------------------------------------------------------

def handle_execute(doc):
    xpath_ns = lambda el, path: el.xpath(path, namespaces=NSMAP)

    ident_els = xpath_ns(doc, '//ows:Identifier')
    if not ident_els:
        return ows_exception("MissingParameterValue", "Missing Identifier element", "Identifier")
    identifier = ident_els[0].text.strip() if ident_els[0].text else ""

    if identifier not in PROCESSES:
        return ows_exception("InvalidParameterValue",
                             "Unknown process '{}'".format(identifier), "Identifier")

    proc = PROCESSES[identifier]

    data_inputs = {}
    for input_el in xpath_ns(doc, '//wps:DataInputs/wps:Input'):
        inp_id_els = xpath_ns(input_el, 'ows:Identifier')
        if not inp_id_els:
            continue
        inp_id = inp_id_els[0].text.strip() if inp_id_els[0].text else ""

        literal_els = xpath_ns(input_el, 'wps:Data/wps:LiteralData')
        complex_els = xpath_ns(input_el, 'wps:Data/wps:ComplexData')

        if literal_els:
            data_inputs[inp_id] = literal_els[0].text or ""
        elif complex_els:
            children = list(complex_els[0])
            if children:
                data_inputs[inp_id] = etree.tostring(children[0], encoding='unicode')
            else:
                data_inputs[inp_id] = complex_els[0].text or ""
        else:
            data_inputs[inp_id] = ""

    req_uuid = str(uuid_mod.uuid4())

    output_values = {}
    for out in proc['outputs']:
        out_id = out['identifier']
        if out['type'] == 'literal':
            output_values[out_id] = "0.0"
        else:
            output_values[out_id] = "<gml:Point xmlns:gml=\"http://www.opengis.net/gml\"><gml:pos>0 0</gml:pos></gml:Point>"

    if identifier == 'geo.buffer':
        geom = data_inputs.get('geometry', '')
        dist = data_inputs.get('distance', '0')
        try:
            d = float(dist)
        except (ValueError, TypeError):
            d = 1.0
        output_values['result'] = (
            '<gml:Polygon xmlns:gml="http://www.opengis.net/gml">'
            '<gml:exterior><gml:LinearRing><gml:posList>'
            '0 0 {d} 0 {d} {d} 0 {d} 0 0'
            '</gml:posList></gml:LinearRing></gml:exterior>'
            '</gml:Polygon>'
        ).format(d=d)
    elif identifier == 'geo.centroid':
        geom = data_inputs.get('geometry', '')
        output_values['result'] = (
            '<gml:Point xmlns:gml="http://www.opengis.net/gml">'
            '<gml:pos>0.5 0.5</gml:pos></gml:Point>'
        )
    elif identifier == 'geo.area':
        geom = data_inputs.get('geometry', '')
        output_values['area'] = "1.0"
    elif identifier == 'geo.echo':
        output_values['outputdata'] = data_inputs.get('inputdata', '')

    outputs_xml = ""
    for out in proc['outputs']:
        out_id = out['identifier']
        val = output_values.get(out_id, "")
        if out['type'] == 'literal':
            outputs_xml += (
                '    <wps:Output>\n'
                '      <ows:Identifier>{oid}</ows:Identifier>\n'
                '      <ows:Title>{title}</ows:Title>\n'
                '      <wps:Data>\n'
                '        <wps:LiteralData>{val}</wps:LiteralData>\n'
                '      </wps:Data>\n'
                '    </wps:Output>\n'
            ).format(oid=out_id, title=out['title'], val=val)
        else:
            outputs_xml += (
                '    <wps:Output>\n'
                '      <ows:Identifier>{oid}</ows:Identifier>\n'
                '      <ows:Title>{title}</ows:Title>\n'
                '      <wps:Data>\n'
                '        <wps:ComplexData>{val}</wps:ComplexData>\n'
                '      </wps:Data>\n'
                '    </wps:Output>\n'
            ).format(oid=out_id, title=out['title'], val=val)

    svc_url = CFG.get('server', 'url')
    exec_doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<wps:ExecuteResponse xmlns:wps="http://www.opengis.net/wps/1.0.0" '
        'xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 '
        'http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd" '
        'service="WPS" version="1.0.0" xml:lang="en-US" '
        'serviceInstance="{svc_url}?service=WPS&amp;request=GetCapabilities">\n'
        '  <wps:Process wps:processVersion="{pv}">\n'
        '    <ows:Identifier>{pid}</ows:Identifier>\n'
        '    <ows:Title>{ptitle}</ows:Title>\n'
        '  </wps:Process>\n'
        '  <wps:Status creationTime="{ctime}">\n'
        '    <wps:ProcessSucceeded>Processing completed.</wps:ProcessSucceeded>\n'
        '  </wps:Status>\n'
        '  <wps:ProcessOutputs>\n{outputs}'
        '  </wps:ProcessOutputs>\n'
        '</wps:ExecuteResponse>\n'
    ).format(
        svc_url=svc_url,
        pv=proc['version'],
        pid=proc['identifier'],
        ptitle=proc['title'],
        ctime=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        outputs=outputs_xml,
    )
    return xml_response(exec_doc)


# -----------------------------------------------------------------------
# POST request handler: parse raw XML body
# -----------------------------------------------------------------------

def _get_xml_parser():
    return etree.XMLParser(
        resolve_entities=True,
        no_network=False,
    )


def handle_post_request(data):
    maxsize = int(CFG.get('server', 'maxrequestsize'))
    if len(data) > maxsize:
        return ows_exception("FileSizeExceeded",
                             "Request size exceeds the limit of {} bytes".format(maxsize))

    try:
        doc = etree.fromstring(data, _get_xml_parser())
    except Exception as e:
        return ows_exception("NoApplicableCode", "Failed to parse XML request")

    tag = doc.tag
    local = tag.split('}')[-1] if '}' in tag else tag

    if local == 'GetCapabilities':
        return xml_response(build_capabilities())
    elif local == 'DescribeProcess':
        ident_els = doc.xpath('//ows:Identifier', namespaces=NSMAP)
        if not ident_els:
            return ows_exception("MissingParameterValue", "Missing identifier", "identifier")
        identifiers = [el.text.strip() for el in ident_els if el.text]
        result, bad = build_describe(identifiers)
        if bad:
            return ows_exception("InvalidParameterValue",
                                 "Unknown process '{}'".format(bad), "identifier")
        return xml_response(result)
    elif local == 'Execute':
        return handle_execute(doc)
    else:
        return ows_exception("OperationNotSupported",
                             "Operation '{}' is not supported".format(local))


# -----------------------------------------------------------------------
# GET request handler: parse query string parameters
# -----------------------------------------------------------------------

def handle_get_request(args):
    service = None
    operation = None
    version = None
    identifier = None

    for k in args:
        kl = k.lower()
        if kl == 'service':
            service = args[k]
        elif kl == 'request':
            operation = args[k]
        elif kl == 'version':
            version = args[k]
        elif kl == 'identifier':
            identifier = args[k]

    if not service or service.upper() != 'WPS':
        return ows_exception("InvalidParameterValue",
                             "Parameter 'service' must be 'WPS'", "service")

    if not operation:
        return ows_exception("MissingParameterValue", "Missing 'request' parameter", "request")

    op = operation.lower()
    if op == 'getcapabilities':
        return xml_response(build_capabilities())
    elif op == 'describeprocess':
        if not identifier:
            return ows_exception("MissingParameterValue",
                                 "Missing 'identifier' parameter", "identifier")
        identifiers = [i.strip() for i in identifier.split(',')]
        result, bad = build_describe(identifiers)
        if bad:
            return ows_exception("InvalidParameterValue",
                                 "Unknown process '{}'".format(bad), "identifier")
        return xml_response(result)
    elif op == 'execute':
        return ows_exception("OperationNotSupported",
                             "Execute via GET is not supported. Use POST.", "request")
    else:
        return ows_exception("OperationNotSupported",
                             "Operation '{}' is not supported".format(operation), "request")


# -----------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------

@app.route('/')
def index():
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ServiceInfo>\n'
        '  <Name>GeoNode Processing Service</Name>\n'
        '  <ServiceType>OGC WPS</ServiceType>\n'
        '  <ServiceVersion>1.0.0</ServiceVersion>\n'
        '  <Endpoint>/ows</Endpoint>\n'
        '</ServiceInfo>\n',
        content_type='text/xml; charset=utf-8',
    )


@app.route('/ows', methods=['GET', 'POST'])
def ows_endpoint():
    if request.method == 'POST':
        data = request.get_data()
        return handle_post_request(data)
    else:
        return handle_get_request(request.args)


@app.route('/ping')
def healthcheck():
    return Response('OK', content_type='text/plain')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
