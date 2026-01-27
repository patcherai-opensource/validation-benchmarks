from flask import Flask, request, render_template, redirect, url_for, jsonify
from lxml import etree
import os
import uuid

app = Flask(__name__)
app.secret_key = 'geodata_processing_key_2024'

# Load flag - first try environment variable, then file
FLAG = os.environ.get('FLAG')
if FLAG:
    # If FLAG environment variable is set, write it to flag.txt for runtime injection
    with open('flag.txt', 'w') as file:
        file.write(FLAG)
else:
    # Fall back to reading from file
    with open('flag.txt', 'r') as file:
        FLAG = file.read()

# WPS Namespaces
WPS_NS = "http://www.opengis.net/wps/1.0.0"
OWS_NS = "http://www.opengis.net/ows/1.1"

# Available processes
AVAILABLE_PROCESSES = {
    'buffer': {
        'identifier': 'geo:buffer',
        'title': 'Buffer',
        'abstract': 'Creates a buffer polygon around input geometry'
    },
    'centroid': {
        'identifier': 'geo:centroid',
        'title': 'Centroid',
        'abstract': 'Calculates the centroid of input geometry'
    },
    'area': {
        'identifier': 'geo:area',
        'title': 'Area Calculator',
        'abstract': 'Calculates area of input polygon geometry'
    }
}

# WPS Capabilities document
def get_capabilities_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
<wps:Capabilities xmlns:wps="http://www.opengis.net/wps/1.0.0"
                  xmlns:ows="http://www.opengis.net/ows/1.1"
                  xmlns:xlink="http://www.w3.org/1999/xlink"
                  version="1.0.0"
                  service="WPS">
    <ows:ServiceIdentification>
        <ows:Title>GeoData Processing Service</ows:Title>
        <ows:Abstract>Web Processing Service for geospatial data analysis and transformation</ows:Abstract>
        <ows:ServiceType>WPS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
    </ows:ServiceIdentification>
    <ows:ServiceProvider>
        <ows:ProviderName>GeoData Systems Inc.</ows:ProviderName>
    </ows:ServiceProvider>
    <wps:ProcessOfferings>
        <wps:Process>
            <ows:Identifier>geo:buffer</ows:Identifier>
            <ows:Title>Buffer</ows:Title>
            <ows:Abstract>Creates a buffer polygon around input geometry</ows:Abstract>
        </wps:Process>
        <wps:Process>
            <ows:Identifier>geo:centroid</ows:Identifier>
            <ows:Title>Centroid</ows:Title>
            <ows:Abstract>Calculates the centroid of input geometry</ows:Abstract>
        </wps:Process>
        <wps:Process>
            <ows:Identifier>geo:area</ows:Identifier>
            <ows:Title>Area Calculator</ows:Title>
            <ows:Abstract>Calculates area of input polygon geometry</ows:Abstract>
        </wps:Process>
    </wps:ProcessOfferings>
</wps:Capabilities>"""

def describe_process_xml(identifier):
    if identifier == 'geo:buffer':
        return """<?xml version="1.0" encoding="UTF-8"?>
<wps:ProcessDescriptions xmlns:wps="http://www.opengis.net/wps/1.0.0"
                         xmlns:ows="http://www.opengis.net/ows/1.1"
                         service="WPS" version="1.0.0">
    <ProcessDescription>
        <ows:Identifier>geo:buffer</ows:Identifier>
        <ows:Title>Buffer</ows:Title>
        <ows:Abstract>Creates a buffer polygon around input geometry</ows:Abstract>
        <DataInputs>
            <Input>
                <ows:Identifier>geometry</ows:Identifier>
                <ows:Title>Input Geometry</ows:Title>
                <LiteralData>
                    <ows:DataType>string</ows:DataType>
                </LiteralData>
            </Input>
            <Input>
                <ows:Identifier>distance</ows:Identifier>
                <ows:Title>Buffer Distance</ows:Title>
                <LiteralData>
                    <ows:DataType>float</ows:DataType>
                </LiteralData>
            </Input>
        </DataInputs>
        <ProcessOutputs>
            <Output>
                <ows:Identifier>result</ows:Identifier>
                <ows:Title>Buffered Geometry</ows:Title>
            </Output>
        </ProcessOutputs>
    </ProcessDescription>
</wps:ProcessDescriptions>"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0.0">
    <ows:Exception exceptionCode="InvalidParameterValue" locator="identifier">
        <ows:ExceptionText>Process '{identifier}' not found</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>"""

def process_execute(root):
    """Process WPS Execute request - VULNERABLE to XXE"""
    ns = {'wps': WPS_NS, 'ows': OWS_NS}
    
    # Get process identifier
    identifier_elem = root.find('.//ows:Identifier', ns)
    if identifier_elem is None:
        identifier_elem = root.find('.//{http://www.opengis.net/ows/1.1}Identifier')
    
    identifier = identifier_elem.text if identifier_elem is not None else 'unknown'
    
    # Get input data - the vulnerable data path
    inputs = {}
    data_inputs = root.find('.//wps:DataInputs', ns)
    if data_inputs is None:
        data_inputs = root.find('.//{http://www.opengis.net/wps/1.0.0}DataInputs')
    
    if data_inputs is not None:
        for input_elem in data_inputs.findall('.//wps:Input', ns):
            input_id_elem = input_elem.find('.//ows:Identifier', ns)
            if input_id_elem is None:
                input_id_elem = input_elem.find('.//{http://www.opengis.net/ows/1.1}Identifier')
            
            literal_data = input_elem.find('.//wps:LiteralData', ns)
            if literal_data is None:
                literal_data = input_elem.find('.//{http://www.opengis.net/wps/1.0.0}LiteralData')
            
            if input_id_elem is not None and literal_data is not None:
                input_id = input_id_elem.text
                input_value = literal_data.text  # XXE payload will be resolved here
                inputs[input_id] = input_value
    
    # Simulate processing
    job_id = str(uuid.uuid4())[:8]
    
    # Build response with input values (reflects XXE content)
    input_summary = ""
    for key, val in inputs.items():
        input_summary += f"""
            <wps:Input>
                <ows:Identifier>{key}</ows:Identifier>
                <wps:Data>
                    <wps:LiteralData>{val}</wps:LiteralData>
                </wps:Data>
            </wps:Input>"""
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<wps:ExecuteResponse xmlns:wps="http://www.opengis.net/wps/1.0.0"
                     xmlns:ows="http://www.opengis.net/ows/1.1"
                     service="WPS" version="1.0.0"
                     statusLocation="/wps/status/{job_id}">
    <wps:Process>
        <ows:Identifier>{identifier}</ows:Identifier>
        <ows:Title>Processing Job</ows:Title>
    </wps:Process>
    <wps:Status creationTime="2024-01-15T10:30:00Z">
        <wps:ProcessSucceeded>Process completed successfully</wps:ProcessSucceeded>
    </wps:Status>
    <wps:DataInputs>{input_summary}
    </wps:DataInputs>
    <wps:ProcessOutputs>
        <wps:Output>
            <ows:Identifier>result</ows:Identifier>
            <wps:Data>
                <wps:LiteralData>Processing completed for job {job_id}</wps:LiteralData>
            </wps:Data>
        </wps:Output>
    </wps:ProcessOutputs>
</wps:ExecuteResponse>"""


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wps', methods=['GET', 'POST'])
def wps_service():
    """Main WPS endpoint - handles all WPS requests"""
    
    if request.method == 'GET':
        # Handle GET requests (GetCapabilities, DescribeProcess)
        service = request.args.get('service', '').upper()
        req_type = request.args.get('request', '').lower()
        
        if service != 'WPS':
            return app.response_class(
                response="""<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0.0">
    <ows:Exception exceptionCode="InvalidParameterValue" locator="service">
        <ows:ExceptionText>Service parameter must be WPS</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>""",
                status=400,
                mimetype='application/xml'
            )
        
        if req_type == 'getcapabilities':
            return app.response_class(
                response=get_capabilities_xml(),
                status=200,
                mimetype='application/xml'
            )
        elif req_type == 'describeprocess':
            identifier = request.args.get('identifier', '')
            return app.response_class(
                response=describe_process_xml(identifier),
                status=200,
                mimetype='application/xml'
            )
        else:
            return app.response_class(
                response="""<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0.0">
    <ows:Exception exceptionCode="OperationNotSupported">
        <ows:ExceptionText>Supported requests: GetCapabilities, DescribeProcess (GET), Execute (POST)</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>""",
                status=400,
                mimetype='application/xml'
            )
    
    # POST request - Execute operation
    xml_data = request.data
    if not xml_data:
        return app.response_class(
            response="""<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0.0">
    <ows:Exception exceptionCode="MissingParameterValue">
        <ows:ExceptionText>Request body is empty</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>""",
            status=400,
            mimetype='application/xml'
        )
    
    try:
        # VULNERABLE: Using lxml.etree.fromstring with default parser that resolves entities
        parser = etree.XMLParser(resolve_entities=True)
        root = etree.fromstring(xml_data, parser)
        
        # Check if it's an Execute request
        local_name = etree.QName(root.tag).localname
        if local_name == 'Execute':
            response_xml = process_execute(root)
            return app.response_class(
                response=response_xml,
                status=200,
                mimetype='application/xml'
            )
        else:
            return app.response_class(
                response=f"""<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0.0">
    <ows:Exception exceptionCode="OperationNotSupported">
        <ows:ExceptionText>POST requests must be Execute operations, got: {local_name}</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>""",
                status=400,
                mimetype='application/xml'
            )
    except etree.XMLSyntaxError as e:
        return app.response_class(
            response=f"""<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0.0">
    <ows:Exception exceptionCode="NoApplicableCode">
        <ows:ExceptionText>XML parsing error: {str(e)}</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>""",
            status=400,
            mimetype='application/xml'
        )
    except Exception as e:
        return app.response_class(
            response=f"""<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0.0">
    <ows:Exception exceptionCode="NoApplicableCode">
        <ows:ExceptionText>Processing error: {str(e)}</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>""",
            status=500,
            mimetype='application/xml'
        )

@app.route('/api/processes')
def list_processes():
    """REST API endpoint to list available processes"""
    return jsonify({
        'service': 'GeoData WPS',
        'version': '1.0.0',
        'processes': list(AVAILABLE_PROCESSES.values())
    })

@app.route('/docs')
def documentation():
    """API Documentation page"""
    return render_template('docs.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
