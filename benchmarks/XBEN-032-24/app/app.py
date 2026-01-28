from flask import Flask, request, render_template, redirect, url_for, jsonify
from lxml import etree
import os
import hashlib
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

# WPS Service configuration
WPS_VERSION = "2.0.0"
SERVICE_TITLE = "GeoProcessor WPS"
SERVICE_ABSTRACT = "Web Processing Service for geospatial data processing and analysis"

# Available processes
WPS_PROCESSES = {
    "geo:buffer": {
        "identifier": "geo:buffer",
        "title": "Buffer Analysis",
        "abstract": "Creates a buffer polygon around input geometry",
        "inputs": [
            {"id": "input_geometry", "title": "Input Geometry", "type": "gml:GeometryPropertyType"},
            {"id": "distance", "title": "Buffer Distance", "type": "xs:double"}
        ],
        "outputs": [
            {"id": "buffered_geometry", "title": "Buffered Geometry", "type": "gml:GeometryPropertyType"}
        ]
    },
    "geo:centroid": {
        "identifier": "geo:centroid",
        "title": "Centroid Calculation",
        "abstract": "Calculates the centroid of input geometry",
        "inputs": [
            {"id": "input_geometry", "title": "Input Geometry", "type": "gml:GeometryPropertyType"}
        ],
        "outputs": [
            {"id": "centroid_point", "title": "Centroid Point", "type": "gml:PointPropertyType"}
        ]
    },
    "geo:intersection": {
        "identifier": "geo:intersection",
        "title": "Geometry Intersection",
        "abstract": "Computes the intersection of two geometries",
        "inputs": [
            {"id": "geometry_a", "title": "Geometry A", "type": "gml:GeometryPropertyType"},
            {"id": "geometry_b", "title": "Geometry B", "type": "gml:GeometryPropertyType"}
        ],
        "outputs": [
            {"id": "intersection_result", "title": "Intersection Result", "type": "gml:GeometryPropertyType"}
        ]
    },
    "data:echo": {
        "identifier": "data:echo",
        "title": "Echo Service",
        "abstract": "Echoes the input data back to the caller for testing purposes",
        "inputs": [
            {"id": "input_data", "title": "Input Data", "type": "xs:string"}
        ],
        "outputs": [
            {"id": "echoed_data", "title": "Echoed Data", "type": "xs:string"}
        ]
    },
    "data:transform": {
        "identifier": "data:transform",
        "title": "Data Transformation",
        "abstract": "Transforms input data according to specified parameters",
        "inputs": [
            {"id": "source_data", "title": "Source Data", "type": "xs:string"},
            {"id": "transform_type", "title": "Transformation Type", "type": "xs:string"}
        ],
        "outputs": [
            {"id": "transformed_data", "title": "Transformed Data", "type": "xs:string"}
        ]
    }
}

# WPS Namespaces
WPS_NS = "http://www.opengis.net/wps/2.0"
OWS_NS = "http://www.opengis.net/ows/2.0"
XLINK_NS = "http://www.w3.org/1999/xlink"

def generate_capabilities_xml():
    """Generate WPS GetCapabilities response"""
    process_offerings = ""
    for proc_id, proc in WPS_PROCESSES.items():
        process_offerings += f"""
        <wps:ProcessSummary processVersion="1.0.0" jobControlOptions="sync-execute async-execute" outputTransmission="value reference">
            <ows:Title>{proc['title']}</ows:Title>
            <ows:Abstract>{proc['abstract']}</ows:Abstract>
            <ows:Identifier>{proc['identifier']}</ows:Identifier>
        </wps:ProcessSummary>"""
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<wps:Capabilities xmlns:wps="{WPS_NS}" xmlns:ows="{OWS_NS}" xmlns:xlink="{XLINK_NS}" version="{WPS_VERSION}" service="WPS">
    <ows:ServiceIdentification>
        <ows:Title>{SERVICE_TITLE}</ows:Title>
        <ows:Abstract>{SERVICE_ABSTRACT}</ows:Abstract>
        <ows:ServiceType>WPS</ows:ServiceType>
        <ows:ServiceTypeVersion>{WPS_VERSION}</ows:ServiceTypeVersion>
    </ows:ServiceIdentification>
    <ows:ServiceProvider>
        <ows:ProviderName>GeoSystems Inc.</ows:ProviderName>
        <ows:ServiceContact>
            <ows:ContactInfo>
                <ows:Address>
                    <ows:ElectronicMailAddress>support@geosystems.local</ows:ElectronicMailAddress>
                </ows:Address>
            </ows:ContactInfo>
        </ows:ServiceContact>
    </ows:ServiceProvider>
    <ows:OperationsMetadata>
        <ows:Operation name="GetCapabilities">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="/wps"/>
                    <ows:Post xlink:href="/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="DescribeProcess">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="/wps"/>
                    <ows:Post xlink:href="/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="Execute">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Post xlink:href="/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
    </ows:OperationsMetadata>
    <wps:Contents>
        <wps:ProcessOfferings>{process_offerings}
        </wps:ProcessOfferings>
    </wps:Contents>
</wps:Capabilities>'''

def generate_describe_process_xml(process_id):
    """Generate WPS DescribeProcess response"""
    if process_id not in WPS_PROCESSES:
        return generate_exception_xml("InvalidParameterValue", f"Unknown process identifier: {process_id}")
    
    proc = WPS_PROCESSES[process_id]
    
    inputs_xml = ""
    for inp in proc['inputs']:
        inputs_xml += f"""
            <wps:Input minOccurs="1" maxOccurs="1">
                <ows:Title>{inp['title']}</ows:Title>
                <ows:Identifier>{inp['id']}</ows:Identifier>
                <wps:LiteralData>
                    <ows:DataType ows:reference="{inp['type']}"/>
                </wps:LiteralData>
            </wps:Input>"""
    
    outputs_xml = ""
    for out in proc['outputs']:
        outputs_xml += f"""
            <wps:Output>
                <ows:Title>{out['title']}</ows:Title>
                <ows:Identifier>{out['id']}</ows:Identifier>
                <wps:LiteralData>
                    <ows:DataType ows:reference="{out['type']}"/>
                </wps:LiteralData>
            </wps:Output>"""
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<wps:ProcessOfferings xmlns:wps="{WPS_NS}" xmlns:ows="{OWS_NS}">
    <wps:ProcessOffering processVersion="1.0.0" jobControlOptions="sync-execute">
        <wps:Process>
            <ows:Title>{proc['title']}</ows:Title>
            <ows:Abstract>{proc['abstract']}</ows:Abstract>
            <ows:Identifier>{proc['identifier']}</ows:Identifier>
            <wps:Inputs>{inputs_xml}
            </wps:Inputs>
            <wps:Outputs>{outputs_xml}
            </wps:Outputs>
        </wps:Process>
    </wps:ProcessOffering>
</wps:ProcessOfferings>'''

def generate_exception_xml(code, text):
    """Generate OWS Exception response"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="{OWS_NS}" version="{WPS_VERSION}">
    <ows:Exception exceptionCode="{code}">
        <ows:ExceptionText>{text}</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>'''

def generate_execute_response_xml(process_id, outputs):
    """Generate WPS Execute response"""
    outputs_xml = ""
    for out_id, out_value in outputs.items():
        outputs_xml += f"""
        <wps:Output id="{out_id}">
            <wps:Data>
                <wps:LiteralValue>{out_value}</wps:LiteralValue>
            </wps:Data>
        </wps:Output>"""
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<wps:Result xmlns:wps="{WPS_NS}" xmlns:ows="{OWS_NS}">
    <wps:JobID>{hashlib.md5(os.urandom(16)).hexdigest()}</wps:JobID>
    <wps:Status>Succeeded</wps:Status>
    <wps:ProcessIdentifier>{process_id}</wps:ProcessIdentifier>
    <wps:Outputs>{outputs_xml}
    </wps:Outputs>
</wps:Result>'''

def process_execute_request(xml_data):
    """Process WPS Execute request - VULNERABLE TO XXE"""
    try:
        # Vulnerable XML parsing - resolves external entities
        parser = etree.XMLParser(resolve_entities=True)
        root = etree.fromstring(xml_data, parser)
        
        # Extract process identifier
        ns = {'wps': WPS_NS, 'ows': OWS_NS}
        
        # Try to find identifier in various formats
        identifier_elem = root.find('.//{%s}Identifier' % OWS_NS)
        if identifier_elem is None:
            identifier_elem = root.find('.//Identifier')
        if identifier_elem is None:
            # Check if it's a simplified format
            identifier_elem = root.find('.//{%s}ProcessIdentifier' % WPS_NS)
        
        if identifier_elem is None:
            return generate_exception_xml("MissingParameterValue", "Missing process Identifier")
        
        process_id = identifier_elem.text
        
        if process_id not in WPS_PROCESSES:
            return generate_exception_xml("InvalidParameterValue", f"Unknown process: {process_id}")
        
        # Extract inputs
        inputs = {}
        for data_input in root.findall('.//{%s}Input' % WPS_NS) + root.findall('.//Input') + root.findall('.//{%s}DataInputs/{%s}Input' % (WPS_NS, WPS_NS)):
            input_id_elem = data_input.find('.//{%s}Identifier' % OWS_NS)
            if input_id_elem is None:
                input_id_elem = data_input.find('.//Identifier')
            input_id = data_input.get('id') or (input_id_elem.text if input_id_elem is not None else None)
            
            # Try various ways to get the literal data value
            literal_data = data_input.find('.//{%s}LiteralData' % WPS_NS)
            if literal_data is None:
                literal_data = data_input.find('.//LiteralData')
            if literal_data is None:
                literal_data = data_input.find('.//{%s}Data/{%s}LiteralValue' % (WPS_NS, WPS_NS))
            if literal_data is None:
                literal_data = data_input.find('.//LiteralValue')
            
            if input_id and literal_data is not None:
                inputs[input_id] = literal_data.text or ""
        
        # Execute the process (simplified simulation)
        outputs = execute_process(process_id, inputs)
        
        return generate_execute_response_xml(process_id, outputs)
        
    except etree.XMLSyntaxError as e:
        return generate_exception_xml("InvalidRequest", f"XML parsing error: {str(e)}")
    except Exception as e:
        return generate_exception_xml("NoApplicableCode", f"Processing error: {str(e)}")

def execute_process(process_id, inputs):
    """Execute a WPS process (simulation)"""
    if process_id == "geo:buffer":
        geom = inputs.get("input_geometry", "POINT(0 0)")
        dist = inputs.get("distance", "10")
        return {"buffered_geometry": f"POLYGON(({geom} BUFFERED BY {dist}))"}
    
    elif process_id == "geo:centroid":
        geom = inputs.get("input_geometry", "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))")
        return {"centroid_point": f"POINT(0.5 0.5) [from {geom[:50]}...]"}
    
    elif process_id == "geo:intersection":
        geom_a = inputs.get("geometry_a", "POLYGON A")
        geom_b = inputs.get("geometry_b", "POLYGON B")
        return {"intersection_result": f"INTERSECTION({geom_a}, {geom_b})"}
    
    elif process_id == "data:echo":
        data = inputs.get("input_data", "")
        return {"echoed_data": data}
    
    elif process_id == "data:transform":
        source = inputs.get("source_data", "")
        transform_type = inputs.get("transform_type", "identity")
        if transform_type == "uppercase":
            return {"transformed_data": source.upper()}
        elif transform_type == "lowercase":
            return {"transformed_data": source.lower()}
        elif transform_type == "reverse":
            return {"transformed_data": source[::-1]}
        else:
            return {"transformed_data": source}
    
    return {"result": "Process executed"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wps', methods=['GET', 'POST'])
def wps_service():
    """Main WPS endpoint - handles GetCapabilities, DescribeProcess, and Execute"""
    
    if request.method == 'GET':
        # Handle GET requests with query parameters
        service = request.args.get('service', '').upper()
        request_type = request.args.get('request', '')
        
        if service != 'WPS':
            return app.response_class(
                response=generate_exception_xml("InvalidParameterValue", "Service must be WPS"),
                status=400,
                mimetype='application/xml'
            )
        
        if request_type == 'GetCapabilities':
            return app.response_class(
                response=generate_capabilities_xml(),
                status=200,
                mimetype='application/xml'
            )
        elif request_type == 'DescribeProcess':
            identifier = request.args.get('identifier', '')
            return app.response_class(
                response=generate_describe_process_xml(identifier),
                status=200,
                mimetype='application/xml'
            )
        else:
            return app.response_class(
                response=generate_exception_xml("OperationNotSupported", f"Unknown request: {request_type}"),
                status=400,
                mimetype='application/xml'
            )
    
    elif request.method == 'POST':
        # Handle POST requests with XML body
        xml_data = request.data
        
        if not xml_data:
            return app.response_class(
                response=generate_exception_xml("MissingParameterValue", "Request body is empty"),
                status=400,
                mimetype='application/xml'
            )
        
        try:
            # Parse to determine request type - also vulnerable
            parser = etree.XMLParser(resolve_entities=True)
            root = etree.fromstring(xml_data, parser)
            
            # Determine request type from root element
            root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
            
            if root_tag == 'GetCapabilities':
                return app.response_class(
                    response=generate_capabilities_xml(),
                    status=200,
                    mimetype='application/xml'
                )
            elif root_tag == 'DescribeProcess':
                identifier_elem = root.find('.//{%s}Identifier' % OWS_NS)
                if identifier_elem is None:
                    identifier_elem = root.find('.//Identifier')
                identifier = identifier_elem.text if identifier_elem is not None else ""
                return app.response_class(
                    response=generate_describe_process_xml(identifier),
                    status=200,
                    mimetype='application/xml'
                )
            elif root_tag == 'Execute':
                return app.response_class(
                    response=process_execute_request(xml_data),
                    status=200,
                    mimetype='application/xml'
                )
            else:
                return app.response_class(
                    response=generate_exception_xml("OperationNotSupported", f"Unknown request type: {root_tag}"),
                    status=400,
                    mimetype='application/xml'
                )
                
        except etree.XMLSyntaxError as e:
            return app.response_class(
                response=generate_exception_xml("InvalidRequest", f"XML syntax error: {str(e)}"),
                status=400,
                mimetype='application/xml'
            )

@app.route('/ows', methods=['GET', 'POST'])
def ows_service():
    """OWS endpoint - redirects to WPS"""
    return wps_service()

@app.route('/api/processes', methods=['GET'])
def list_processes():
    """REST API endpoint to list available processes"""
    processes = []
    for proc_id, proc in WPS_PROCESSES.items():
        processes.append({
            "id": proc_id,
            "title": proc['title'],
            "abstract": proc['abstract']
        })
    return jsonify({"processes": processes})

@app.route('/api/processes/<process_id>', methods=['GET'])
def get_process_details(process_id):
    """REST API endpoint to get process details"""
    if process_id not in WPS_PROCESSES:
        return jsonify({"error": "Process not found"}), 404
    return jsonify(WPS_PROCESSES[process_id])

@app.route('/status')
def status():
    """Health check endpoint"""
    return jsonify({
        "service": SERVICE_TITLE,
        "version": WPS_VERSION,
        "status": "operational",
        "processes_available": len(WPS_PROCESSES)
    })

@app.route('/docs')
def documentation():
    """Documentation page"""
    return render_template('docs.html')

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return app.send_static_file('robots.txt')

@app.route('/version')
def version():
    """Version information"""
    return jsonify({
        "application": "GeoProcessor WPS",
        "version": WPS_VERSION,
        "api_version": "1.0.0",
        "library": "lxml",
        "supported_standards": ["WPS 2.0.0", "OWS 2.0"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
