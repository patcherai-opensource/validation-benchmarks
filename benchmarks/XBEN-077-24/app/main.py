import logging
import datetime

from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from lxml import etree

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("ogcservice")

NAMESPACES = {
    'xlink': 'http://www.w3.org/1999/xlink',
    'gps': 'http://www.opengis.net/gps/1.0.0',
    'ows': 'http://www.opengis.net/ows/1.1',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

# Process registry
PROCESS_REGISTRY = {
    'buffer_analysis': {
        'identifier': 'buffer_analysis',
        'title': 'Buffer Analysis',
        'abstract': 'Computes a buffer zone around input geometries.',
        'version': '1.0.0',
        'inputs': [
            {'identifier': 'input_features', 'title': 'Input Features', 'abstract': 'Input vector features', 'type': 'complex'},
            {'identifier': 'distance', 'title': 'Buffer Distance', 'abstract': 'Distance for buffer computation', 'type': 'literal'},
        ],
        'outputs': [
            {'identifier': 'buffered_features', 'title': 'Buffered Features', 'abstract': 'Output buffer polygons', 'type': 'complex'},
        ]
    },
    'raster_stats': {
        'identifier': 'raster_stats',
        'title': 'Raster Statistics',
        'abstract': 'Calculates zonal statistics for a given raster dataset.',
        'version': '1.0.0',
        'inputs': [
            {'identifier': 'raster_input', 'title': 'Raster Input', 'abstract': 'Input raster data', 'type': 'complex'},
            {'identifier': 'zone_field', 'title': 'Zone Field', 'abstract': 'Field used to define zones', 'type': 'literal'},
        ],
        'outputs': [
            {'identifier': 'statistics_output', 'title': 'Statistics Output', 'abstract': 'Computed zonal statistics', 'type': 'literal'},
        ]
    },
    'coordinate_transform': {
        'identifier': 'coordinate_transform',
        'title': 'Coordinate Transformation',
        'abstract': 'Transforms coordinates from one reference system to another.',
        'version': '1.0.0',
        'inputs': [
            {'identifier': 'source_data', 'title': 'Source Data', 'abstract': 'Input coordinate data as literal value', 'type': 'literal'},
            {'identifier': 'target_crs', 'title': 'Target CRS', 'abstract': 'Target coordinate reference system', 'type': 'literal'},
        ],
        'outputs': [
            {'identifier': 'transformed_data', 'title': 'Transformed Data', 'abstract': 'Transformed coordinate data', 'type': 'literal'},
        ]
    }
}

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def xml_response(content: str, status_code: int = 200) -> Response:
    return Response(content=content, media_type="text/xml", status_code=status_code)


def build_exception_report(code: str, text: str, locator: str = "None") -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.opengis.net/ows/1.1 '
        'http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">\n'
        f'  <ows:Exception exceptionCode="{code}" locator="{locator}">\n'
        f'    <ows:ExceptionText>{text}</ows:ExceptionText>\n'
        '  </ows:Exception>\n'
        '</ows:ExceptionReport>'
    )


def build_capabilities_response() -> str:
    processes_xml = ""
    for proc in PROCESS_REGISTRY.values():
        processes_xml += (
            f'    <gps:Process gps:processVersion="{proc["version"]}">\n'
            f'      <ows:Identifier>{proc["identifier"]}</ows:Identifier>\n'
            f'      <ows:Title>{proc["title"]}</ows:Title>\n'
            f'      <ows:Abstract>{proc["abstract"]}</ows:Abstract>\n'
            f'    </gps:Process>\n'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gps:Capabilities service="GPS" version="1.0.0" xml:lang="en-US" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:gps="http://www.opengis.net/gps/1.0.0" '
        'xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        '  <ows:ServiceIdentification>\n'
        '    <ows:Title>GeoProcessing Service</ows:Title>\n'
        '    <ows:Abstract>OGC compliant geospatial processing service for vector and raster operations.</ows:Abstract>\n'
        '    <ows:Keywords>\n'
        '      <ows:Keyword>geospatial</ows:Keyword>\n'
        '      <ows:Keyword>processing</ows:Keyword>\n'
        '      <ows:Keyword>OGC</ows:Keyword>\n'
        '    </ows:Keywords>\n'
        '    <ows:ServiceType>GPS</ows:ServiceType>\n'
        '    <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>\n'
        '    <ows:Fees>NONE</ows:Fees>\n'
        '    <ows:AccessConstraints>NONE</ows:AccessConstraints>\n'
        '  </ows:ServiceIdentification>\n'
        '  <ows:ServiceProvider>\n'
        '    <ows:ProviderName>GeoServices Inc.</ows:ProviderName>\n'
        '    <ows:ProviderSite xlink:href="https://geoservices.example.org"/>\n'
        '    <ows:ServiceContact>\n'
        '      <ows:IndividualName>Service Administrator</ows:IndividualName>\n'
        '      <ows:PositionName>System Admin</ows:PositionName>\n'
        '    </ows:ServiceContact>\n'
        '  </ows:ServiceProvider>\n'
        '  <ows:OperationsMetadata>\n'
        '    <ows:Operation name="GetCapabilities">\n'
        '      <ows:DCP>\n'
        '        <ows:HTTP>\n'
        '          <ows:Get xlink:href="/ows"/>\n'
        '        </ows:HTTP>\n'
        '      </ows:DCP>\n'
        '    </ows:Operation>\n'
        '    <ows:Operation name="DescribeProcess">\n'
        '      <ows:DCP>\n'
        '        <ows:HTTP>\n'
        '          <ows:Get xlink:href="/ows"/>\n'
        '          <ows:Post xlink:href="/ows"/>\n'
        '        </ows:HTTP>\n'
        '      </ows:DCP>\n'
        '    </ows:Operation>\n'
        '    <ows:Operation name="Execute">\n'
        '      <ows:DCP>\n'
        '        <ows:HTTP>\n'
        '          <ows:Get xlink:href="/ows"/>\n'
        '          <ows:Post xlink:href="/ows"/>\n'
        '        </ows:HTTP>\n'
        '      </ows:DCP>\n'
        '    </ows:Operation>\n'
        '  </ows:OperationsMetadata>\n'
        '  <gps:ProcessOfferings>\n'
        + processes_xml +
        '  </gps:ProcessOfferings>\n'
        '  <gps:Languages>\n'
        '    <gps:Default>\n'
        '      <ows:Language>en-US</ows:Language>\n'
        '    </gps:Default>\n'
        '  </gps:Languages>\n'
        '</gps:Capabilities>\n'
    )


def build_describe_response(identifiers: list) -> str:
    descs = ""
    for ident in identifiers:
        proc = PROCESS_REGISTRY.get(ident)
        if not proc:
            continue

        inputs_xml = ""
        for inp in proc.get('inputs', []):
            if inp['type'] == 'literal':
                inputs_xml += (
                    f'      <Input minOccurs="1" maxOccurs="1">\n'
                    f'        <ows:Identifier>{inp["identifier"]}</ows:Identifier>\n'
                    f'        <ows:Title>{inp["title"]}</ows:Title>\n'
                    f'        <ows:Abstract>{inp["abstract"]}</ows:Abstract>\n'
                    f'        <LiteralData>\n'
                    f'          <ows:DataType ows:reference="urn:ogc:def:dataType:OGC:1.1:string">string</ows:DataType>\n'
                    f'          <ows:AnyValue/>\n'
                    f'        </LiteralData>\n'
                    f'      </Input>\n'
                )
            else:
                inputs_xml += (
                    f'      <Input minOccurs="1" maxOccurs="1">\n'
                    f'        <ows:Identifier>{inp["identifier"]}</ows:Identifier>\n'
                    f'        <ows:Title>{inp["title"]}</ows:Title>\n'
                    f'        <ows:Abstract>{inp["abstract"]}</ows:Abstract>\n'
                    f'        <ComplexData>\n'
                    f'          <Default><Format><MimeType>application/gml+xml</MimeType></Format></Default>\n'
                    f'        </ComplexData>\n'
                    f'      </Input>\n'
                )

        outputs_xml = ""
        for outp in proc.get('outputs', []):
            if outp['type'] == 'literal':
                outputs_xml += (
                    f'      <Output>\n'
                    f'        <ows:Identifier>{outp["identifier"]}</ows:Identifier>\n'
                    f'        <ows:Title>{outp["title"]}</ows:Title>\n'
                    f'        <ows:Abstract>{outp["abstract"]}</ows:Abstract>\n'
                    f'        <LiteralOutput>\n'
                    f'          <ows:DataType ows:reference="urn:ogc:def:dataType:OGC:1.1:string">string</ows:DataType>\n'
                    f'        </LiteralOutput>\n'
                    f'      </Output>\n'
                )
            else:
                outputs_xml += (
                    f'      <Output>\n'
                    f'        <ows:Identifier>{outp["identifier"]}</ows:Identifier>\n'
                    f'        <ows:Title>{outp["title"]}</ows:Title>\n'
                    f'        <ows:Abstract>{outp["abstract"]}</ows:Abstract>\n'
                    f'        <ComplexOutput>\n'
                    f'          <Default><Format><MimeType>application/gml+xml</MimeType></Format></Default>\n'
                    f'        </ComplexOutput>\n'
                    f'      </Output>\n'
                )

        descs += (
            f'  <ProcessDescription gps:processVersion="{proc["version"]}" statusSupported="true" storeSupported="true">\n'
            f'    <ows:Identifier>{proc["identifier"]}</ows:Identifier>\n'
            f'    <ows:Title>{proc["title"]}</ows:Title>\n'
            f'    <ows:Abstract>{proc["abstract"]}</ows:Abstract>\n'
            f'    <DataInputs>\n'
            + inputs_xml +
            f'    </DataInputs>\n'
            f'    <ProcessOutputs>\n'
            + outputs_xml +
            f'    </ProcessOutputs>\n'
            f'  </ProcessDescription>\n'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gps:ProcessDescriptions xmlns:gps="http://www.opengis.net/gps/1.0.0" '
        'xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'service="GPS" version="1.0.0" xml:lang="en-US">\n'
        + descs +
        '</gps:ProcessDescriptions>\n'
    )


def build_execute_response(process_id: str, inputs_data: dict, status: str = "succeeded") -> str:
    proc = PROCESS_REGISTRY.get(process_id)
    if not proc:
        return build_exception_report("InvalidParameterValue",
                                      f"Unknown process '{process_id}'", "Identifier")

    now = datetime.datetime.utcnow().isoformat() + "Z"

    inputs_xml = ""
    for key, val in inputs_data.items():
        inputs_xml += (
            f'      <gps:Input>\n'
            f'        <ows:Identifier>{key}</ows:Identifier>\n'
            f'        <gps:Data>\n'
            f'          <gps:LiteralData>{val}</gps:LiteralData>\n'
            f'        </gps:Data>\n'
            f'      </gps:Input>\n'
        )

    outputs_xml = ""
    for outp in proc.get('outputs', []):
        result_val = "Processing completed. Result: " + ", ".join(
            f"{k}={v}" for k, v in inputs_data.items()
        )
        outputs_xml += (
            f'      <gps:Output>\n'
            f'        <ows:Identifier>{outp["identifier"]}</ows:Identifier>\n'
            f'        <ows:Title>{outp["title"]}</ows:Title>\n'
            f'        <gps:Data>\n'
            f'          <gps:LiteralData>{result_val}</gps:LiteralData>\n'
            f'        </gps:Data>\n'
            f'      </gps:Output>\n'
        )

    status_xml = ""
    if status == "succeeded":
        status_xml = f'    <gps:ProcessSucceeded>Process completed successfully.</gps:ProcessSucceeded>\n'
    elif status == "failed":
        status_xml = f'    <gps:ProcessFailed><gps:ExceptionReport><ows:Exception exceptionCode="NoApplicableCode"><ows:ExceptionText>Processing error.</ows:ExceptionText></ows:Exception></gps:ExceptionReport></gps:ProcessFailed>\n'

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gps:ExecuteResponse xmlns:gps="http://www.opengis.net/gps/1.0.0" '
        'xmlns:ows="http://www.opengis.net/ows/1.1" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'service="GPS" version="1.0.0" xml:lang="en-US">\n'
        f'  <gps:Process gps:processVersion="{proc["version"]}">\n'
        f'    <ows:Identifier>{proc["identifier"]}</ows:Identifier>\n'
        f'    <ows:Title>{proc["title"]}</ows:Title>\n'
        f'    <ows:Abstract>{proc["abstract"]}</ows:Abstract>\n'
        f'  </gps:Process>\n'
        f'  <gps:Status creationTime="{now}">\n'
        + status_xml +
        f'  </gps:Status>\n'
        f'  <gps:DataInputs>\n'
        + inputs_xml +
        f'  </gps:DataInputs>\n'
        f'  <gps:ProcessOutputs>\n'
        + outputs_xml +
        f'  </gps:ProcessOutputs>\n'
        f'</gps:ExecuteResponse>\n'
    )


def parse_post_body(raw_body: bytes):
    """Parse incoming XML request body and dispatch to appropriate handler."""
    parser = etree.XMLParser(resolve_entities=True)
    doc = etree.fromstring(raw_body, parser)

    tag = doc.tag
    nsmap = doc.nsmap

    prefix = doc.prefix
    if prefix and prefix in nsmap:
        ns = nsmap[prefix]
    else:
        ns = nsmap.get(None, '')

    if 'GetCapabilities' in tag:
        return build_capabilities_response()
    elif 'DescribeProcess' in tag:
        identifiers = []
        for el in doc.iter():
            local = etree.QName(el.tag).localname if '}' in el.tag else el.tag
            if local == 'Identifier':
                if el.text:
                    identifiers.append(el.text.strip())
        if not identifiers:
            identifiers = list(PROCESS_REGISTRY.keys())
        return build_describe_response(identifiers)
    elif 'Execute' in tag:
        identifier = None
        inputs_data = {}

        for el in doc.iter():
            local = etree.QName(el.tag).localname if '}' in el.tag else el.tag
            if local == 'Identifier' and identifier is None:
                parent_local = etree.QName(el.getparent().tag).localname if '}' in el.getparent().tag else el.getparent().tag
                if parent_local in ('Execute',):
                    if el.text:
                        identifier = el.text.strip()

        if not identifier:
            for el in doc.iter():
                local = etree.QName(el.tag).localname if '}' in el.tag else el.tag
                if local == 'Identifier':
                    if el.text and el.text.strip() in PROCESS_REGISTRY:
                        identifier = el.text.strip()
                        break

        if not identifier:
            for el in doc:
                local = etree.QName(el.tag).localname if '}' in el.tag else el.tag
                if local == 'Identifier' and el.text:
                    identifier = el.text.strip()
                    break

        for input_el in doc.iter():
            local = etree.QName(input_el.tag).localname if '}' in input_el.tag else input_el.tag
            if local == 'Input':
                inp_id = None
                inp_val = None
                for child in input_el.iter():
                    child_local = etree.QName(child.tag).localname if '}' in child.tag else child.tag
                    if child_local == 'Identifier' and child.text:
                        inp_id = child.text.strip()
                    elif child_local in ('LiteralData', 'ComplexData'):
                        if child.text:
                            inp_val = child.text.strip()
                        else:
                            inp_val = etree.tostring(child, encoding='unicode')
                if inp_id:
                    inputs_data[inp_id] = inp_val or ''

        if not identifier:
            return build_exception_report("MissingParameterValue",
                                          "Missing process identifier", "Identifier")

        if identifier not in PROCESS_REGISTRY:
            return build_exception_report("InvalidParameterValue",
                                          f"Unknown process '{identifier}'", "Identifier")

        return build_execute_response(identifier, inputs_data)
    else:
        return build_exception_report("OperationNotSupported",
                                      f"Operation not supported: {tag}")


def handle_get_request(params: dict):
    """Handle OGC GET requests via KVP encoding."""
    service = None
    request_op = None

    for k, v in params.items():
        kl = k.lower()
        if kl == 'service':
            service = v
        elif kl == 'request':
            request_op = v

    if not service:
        return build_exception_report("MissingParameterValue",
                                      "Missing parameter: service", "service"), 400

    if service.upper() != 'GPS':
        return build_exception_report("InvalidParameterValue",
                                      f"Parameter SERVICE [{service}] not supported", "service"), 400

    if not request_op:
        return build_exception_report("MissingParameterValue",
                                      "Missing parameter: request", "request"), 400

    op = request_op.lower()
    if op == 'getcapabilities':
        return build_capabilities_response(), 200
    elif op == 'describeprocess':
        identifier = None
        for k, v in params.items():
            if k.lower() == 'identifier':
                identifier = v
        if identifier:
            ids = [i.strip() for i in identifier.split(',')]
        else:
            ids = list(PROCESS_REGISTRY.keys())
        return build_describe_response(ids), 200
    elif op == 'execute':
        identifier = None
        for k, v in params.items():
            if k.lower() == 'identifier':
                identifier = v
        if not identifier:
            return build_exception_report("MissingParameterValue",
                                          "Missing parameter: identifier", "identifier"), 400
        if identifier not in PROCESS_REGISTRY:
            return build_exception_report("InvalidParameterValue",
                                          f"Unknown process '{identifier}'", "Identifier"), 400

        inputs_data = {}
        for k, v in params.items():
            if k.lower() == 'datainputs':
                for part in v.split(';'):
                    if '=' in part:
                        field = part.split('@')[0]
                        ikey, ival = field.split('=', 1)
                        inputs_data[ikey.strip()] = ival.strip()
        return build_execute_response(identifier, inputs_data), 200
    else:
        return build_exception_report("OperationNotSupported",
                                      f"Operation not supported: {request_op}"), 400


@app.get("/ows", response_class=Response)
async def ows_get(request: Request):
    params = dict(request.query_params)
    content, status = handle_get_request(params)
    return xml_response(content, status)


@app.post("/ows", response_class=Response)
async def ows_post(request: Request):
    body = await request.body()
    if not body:
        return xml_response(
            build_exception_report("NoApplicableCode", "Empty request body"),
            400
        )

    content_length = len(body)
    max_size = 5 * 1024 * 1024
    if content_length > max_size:
        return xml_response(
            build_exception_report("FileSizeExceeded",
                                   f"Request size exceeded. Maximum allowed: {max_size // (1024*1024)}MB"),
            400
        )

    try:
        result = parse_post_body(body)
        return xml_response(result, 200)
    except etree.XMLSyntaxError as e:
        return xml_response(
            build_exception_report("NoApplicableCode", "Invalid XML in request body"),
            400
        )
    except Exception as e:
        logger.warning(f"Request processing error: {type(e).__name__}")
        return xml_response(
            build_exception_report("NoApplicableCode", "Server processing error"),
            500
        )


@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>GeoProcessing Service</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px 40px; }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 14px; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 6px; padding: 25px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #2c3e50; font-size: 18px; }
        .card h3 { color: #34495e; font-size: 15px; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; color: #555; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
        pre { background: #f8f8f8; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 13px; }
        a { color: #2980b9; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .endpoint { font-family: monospace; background: #e8f4fd; padding: 2px 8px; border-radius: 3px; }
        .footer { text-align: center; padding: 20px; color: #888; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GeoProcessing Service (GPS)</h1>
        <p>OGC-compliant Geospatial Processing Service v1.0.0</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Service Endpoint</h2>
            <p>The GPS service is available at: <span class="endpoint">/ows</span></p>
            <p>Supported operations via HTTP GET (KVP encoding) and HTTP POST (XML encoding):</p>
            <table>
                <tr><th>Operation</th><th>GET Example</th></tr>
                <tr>
                    <td>GetCapabilities</td>
                    <td><a href="/ows?service=GPS&request=GetCapabilities"><code>/ows?service=GPS&amp;request=GetCapabilities</code></a></td>
                </tr>
                <tr>
                    <td>DescribeProcess</td>
                    <td><a href="/ows?service=GPS&request=DescribeProcess&identifier=buffer_analysis"><code>/ows?service=GPS&amp;request=DescribeProcess&amp;identifier=buffer_analysis</code></a></td>
                </tr>
                <tr>
                    <td>Execute</td>
                    <td><code>/ows?service=GPS&amp;request=Execute&amp;identifier=buffer_analysis&amp;datainputs=distance=100</code></td>
                </tr>
            </table>
        </div>
        <div class="card">
            <h2>Available Processes</h2>
            <table>
                <tr><th>Identifier</th><th>Title</th><th>Description</th></tr>
                <tr><td><code>buffer_analysis</code></td><td>Buffer Analysis</td><td>Computes a buffer zone around input geometries.</td></tr>
                <tr><td><code>raster_stats</code></td><td>Raster Statistics</td><td>Calculates zonal statistics for a given raster dataset.</td></tr>
                <tr><td><code>coordinate_transform</code></td><td>Coordinate Transformation</td><td>Transforms coordinates from one reference system to another.</td></tr>
            </table>
        </div>
        <div class="card">
            <h2>POST Execute Example</h2>
            <p>Send XML requests to <code>/ows</code> via HTTP POST:</p>
            <pre>&lt;gps:Execute service="GPS" version="1.0.0"
    xmlns:ows="http://www.opengis.net/ows/1.1"
    xmlns:gps="http://www.opengis.net/gps/1.0.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"&gt;
  &lt;ows:Identifier&gt;coordinate_transform&lt;/ows:Identifier&gt;
  &lt;gps:DataInputs&gt;
    &lt;gps:Input&gt;
      &lt;ows:Identifier&gt;source_data&lt;/ows:Identifier&gt;
      &lt;gps:Data&gt;
        &lt;gps:LiteralData&gt;48.8566,2.3522&lt;/gps:LiteralData&gt;
      &lt;/gps:Data&gt;
    &lt;/gps:Input&gt;
    &lt;gps:Input&gt;
      &lt;ows:Identifier&gt;target_crs&lt;/ows:Identifier&gt;
      &lt;gps:Data&gt;
        &lt;gps:LiteralData&gt;EPSG:3857&lt;/gps:LiteralData&gt;
      &lt;/gps:Data&gt;
    &lt;/gps:Input&gt;
  &lt;/gps:DataInputs&gt;
&lt;/gps:Execute&gt;</pre>
        </div>
    </div>
    <div class="footer">
        GeoProcessing Service &copy; 2024 GeoServices Inc. | Powered by OGC Standards
    </div>
</body>
</html>"""


@app.get("/ping")
async def ping():
    return {"status": "ok"}
