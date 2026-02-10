from flask import Flask, request, render_template, redirect, url_for, session
from lxml import etree
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

users = {'admin': 'geoserver2024'}

OWS_NS = "http://www.opengis.net/ows/1.1"
WPS_NS = "http://www.opengis.net/wps/1.0.0"
XLINK_NS = "http://www.w3.org/1999/xlink"

AVAILABLE_PROCESSES = {
    "geo:buffer": {
        "title": "Buffer",
        "abstract": "Creates a buffer around a geometry feature",
        "inputs": ["geometry", "distance"],
        "outputs": ["buffered_geometry"]
    },
    "geo:centroid": {
        "title": "Centroid",
        "abstract": "Computes the centroid of a geometry",
        "inputs": ["geometry"],
        "outputs": ["centroid_point"]
    },
    "geo:intersection": {
        "title": "Intersection",
        "abstract": "Computes the intersection of two geometries",
        "inputs": ["geometry_a", "geometry_b"],
        "outputs": ["intersection_geometry"]
    },
    "geo:union": {
        "title": "Union",
        "abstract": "Computes the union of multiple geometries",
        "inputs": ["geometries"],
        "outputs": ["union_geometry"]
    },
    "geo:simplify": {
        "title": "Simplify",
        "abstract": "Simplifies a geometry using the Douglas-Peucker algorithm",
        "inputs": ["geometry", "tolerance"],
        "outputs": ["simplified_geometry"]
    }
}


def generate_capabilities():
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<wps:Capabilities xmlns:wps="{WPS_NS}" xmlns:ows="{OWS_NS}" xmlns:xlink="{XLINK_NS}" 
    service="WPS" version="1.0.0" xml:lang="en-US">
    <ows:ServiceIdentification>
        <ows:Title>GeoProcessing WPS Server</ows:Title>
        <ows:Abstract>Web Processing Service for geospatial operations</ows:Abstract>
        <ows:ServiceType>WPS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
    </ows:ServiceIdentification>
    <ows:ServiceProvider>
        <ows:ProviderName>GeoData Solutions Inc.</ows:ProviderName>
    </ows:ServiceProvider>
    <ows:OperationsMetadata>
        <ows:Operation name="GetCapabilities">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://localhost/wps?"/>
                    <ows:Post xlink:href="http://localhost/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="DescribeProcess">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://localhost/wps?"/>
                    <ows:Post xlink:href="http://localhost/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="Execute">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Post xlink:href="http://localhost/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
    </ows:OperationsMetadata>
    <wps:ProcessOfferings>
        {"".join([f'''<wps:Process wps:processVersion="1.0.0">
            <ows:Identifier>{pid}</ows:Identifier>
            <ows:Title>{pinfo["title"]}</ows:Title>
            <ows:Abstract>{pinfo["abstract"]}</ows:Abstract>
        </wps:Process>''' for pid, pinfo in AVAILABLE_PROCESSES.items()])}
    </wps:ProcessOfferings>
    <wps:Languages>
        <wps:Default><ows:Language>en-US</ows:Language></wps:Default>
        <wps:Supported><ows:Language>en-US</ows:Language></wps:Supported>
    </wps:Languages>
</wps:Capabilities>'''


def generate_process_description(identifier):
    if identifier not in AVAILABLE_PROCESSES:
        return None
    proc = AVAILABLE_PROCESSES[identifier]
    inputs_xml = "".join([f'''<Input minOccurs="1" maxOccurs="1">
            <ows:Identifier>{inp}</ows:Identifier>
            <ows:Title>{inp.replace("_", " ").title()}</ows:Title>
            <LiteralData>
                <ows:DataType ows:reference="xs:string">string</ows:DataType>
                <ows:AnyValue/>
            </LiteralData>
        </Input>''' for inp in proc["inputs"]])
    outputs_xml = "".join([f'''<Output>
            <ows:Identifier>{out}</ows:Identifier>
            <ows:Title>{out.replace("_", " ").title()}</ows:Title>
            <LiteralOutput>
                <ows:DataType ows:reference="xs:string">string</ows:DataType>
            </LiteralOutput>
        </Output>''' for out in proc["outputs"]])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<wps:ProcessDescriptions xmlns:wps="{WPS_NS}" xmlns:ows="{OWS_NS}"
    service="WPS" version="1.0.0" xml:lang="en-US">
    <ProcessDescription wps:processVersion="1.0.0" storeSupported="true" statusSupported="true">
        <ows:Identifier>{identifier}</ows:Identifier>
        <ows:Title>{proc["title"]}</ows:Title>
        <ows:Abstract>{proc["abstract"]}</ows:Abstract>
        <DataInputs>
            {inputs_xml}
        </DataInputs>
        <ProcessOutputs>
            {outputs_xml}
        </ProcessOutputs>
    </ProcessDescription>
</wps:ProcessDescriptions>'''


def execute_process(identifier, inputs_data):
    if identifier not in AVAILABLE_PROCESSES:
        return None
    proc = AVAILABLE_PROCESSES[identifier]
    
    output_val = f"Processed result for {identifier}"
    if identifier == "geo:buffer":
        geom = inputs_data.get("geometry", "")
        dist = inputs_data.get("distance", "10")
        output_val = f"POLYGON((buffered {geom} by {dist} units))"
    elif identifier == "geo:centroid":
        geom = inputs_data.get("geometry", "")
        output_val = f"POINT(centroid of {geom})"
    elif identifier == "geo:intersection":
        geom_a = inputs_data.get("geometry_a", "")
        geom_b = inputs_data.get("geometry_b", "")
        output_val = f"POLYGON((intersection of {geom_a} and {geom_b}))"
    elif identifier == "geo:union":
        geoms = inputs_data.get("geometries", "")
        output_val = f"MULTIPOLYGON((union of {geoms}))"
    elif identifier == "geo:simplify":
        geom = inputs_data.get("geometry", "")
        tol = inputs_data.get("tolerance", "0.1")
        output_val = f"POLYGON((simplified {geom} with tolerance {tol}))"
    
    output_id = proc["outputs"][0]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<wps:ExecuteResponse xmlns:wps="{WPS_NS}" xmlns:ows="{OWS_NS}"
    service="WPS" version="1.0.0" xml:lang="en-US"
    serviceInstance="http://localhost/wps?service=WPS&amp;request=GetCapabilities">
    <wps:Process wps:processVersion="1.0.0">
        <ows:Identifier>{identifier}</ows:Identifier>
        <ows:Title>{proc["title"]}</ows:Title>
    </wps:Process>
    <wps:Status creationTime="2024-01-15T10:30:00Z">
        <wps:ProcessSucceeded>Process completed successfully</wps:ProcessSucceeded>
    </wps:Status>
    <wps:ProcessOutputs>
        <wps:Output>
            <ows:Identifier>{output_id}</ows:Identifier>
            <ows:Title>{output_id.replace("_", " ").title()}</ows:Title>
            <wps:Data>
                <wps:LiteralData>{output_val}</wps:LiteralData>
            </wps:Data>
        </wps:Output>
    </wps:ProcessOutputs>
</wps:ExecuteResponse>'''


def generate_exception(code, text):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="{OWS_NS}" version="1.1.0" xml:lang="en-US">
    <ows:Exception exceptionCode="{code}">
        <ows:ExceptionText>{text}</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>'''


@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404


@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin_login():
    if 'username' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('login.html')


@app.route('/admin/login', methods=['POST'])
def admin_do_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('admin_dashboard'))
    return 'Invalid credentials', 401


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    return render_template('dashboard.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('username', None)
    return redirect(url_for('admin_login'))


@app.route('/wps', methods=['GET', 'POST'])
def wps_endpoint():
    if request.method == 'GET':
        service = request.args.get('service', '').upper()
        req_type = request.args.get('request', '')
        
        if service != 'WPS':
            return app.response_class(
                response=generate_exception("InvalidParameterValue", "Missing or invalid service parameter"),
                status=400, mimetype='application/xml')
        
        if req_type == 'GetCapabilities':
            return app.response_class(response=generate_capabilities(), status=200, mimetype='application/xml')
        elif req_type == 'DescribeProcess':
            identifier = request.args.get('identifier', '')
            if not identifier:
                return app.response_class(
                    response=generate_exception("MissingParameterValue", "Missing identifier parameter"),
                    status=400, mimetype='application/xml')
            desc = generate_process_description(identifier)
            if desc is None:
                return app.response_class(
                    response=generate_exception("InvalidParameterValue", f"Unknown process: {identifier}"),
                    status=400, mimetype='application/xml')
            return app.response_class(response=desc, status=200, mimetype='application/xml')
        else:
            return app.response_class(
                response=generate_exception("OperationNotSupported", f"Unsupported request type: {req_type}"),
                status=400, mimetype='application/xml')
    
    xml_data = request.get_data()
    if not xml_data:
        return app.response_class(
            response=generate_exception("MissingParameterValue", "Empty request body"),
            status=400, mimetype='application/xml')
    
    try:
        parser = etree.XMLParser(resolve_entities=True, load_dtd=True, no_network=False)
        root = etree.fromstring(xml_data, parser)
    except etree.XMLSyntaxError as e:
        return app.response_class(
            response=generate_exception("InvalidParameterValue", "Malformed XML request"),
            status=400, mimetype='application/xml')
    
    local_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
    
    if local_tag == 'GetCapabilities':
        return app.response_class(response=generate_capabilities(), status=200, mimetype='application/xml')
    elif local_tag == 'DescribeProcess':
        ns = {'wps': WPS_NS, 'ows': OWS_NS}
        ident_elem = root.find('.//ows:Identifier', ns)
        if ident_elem is None:
            ident_elem = root.find('.//{%s}Identifier' % OWS_NS)
        identifier = ident_elem.text if ident_elem is not None else ''
        if not identifier:
            return app.response_class(
                response=generate_exception("MissingParameterValue", "Missing identifier"),
                status=400, mimetype='application/xml')
        desc = generate_process_description(identifier)
        if desc is None:
            return app.response_class(
                response=generate_exception("InvalidParameterValue", f"Unknown process: {identifier}"),
                status=400, mimetype='application/xml')
        return app.response_class(response=desc, status=200, mimetype='application/xml')
    elif local_tag == 'Execute':
        ns = {'wps': WPS_NS, 'ows': OWS_NS}
        ident_elem = root.find('.//ows:Identifier', ns)
        if ident_elem is None:
            ident_elem = root.find('.//{%s}Identifier' % OWS_NS)
        identifier = ident_elem.text if ident_elem is not None else ''
        
        if not identifier or identifier not in AVAILABLE_PROCESSES:
            return app.response_class(
                response=generate_exception("InvalidParameterValue", f"Unknown or missing process identifier"),
                status=400, mimetype='application/xml')
        
        inputs_data = {}
        for inp in root.iter():
            local_inp = inp.tag.split('}')[-1] if '}' in inp.tag else inp.tag
            if local_inp == 'Input':
                inp_ident = None
                inp_value = None
                for child in inp:
                    child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    if child_tag == 'Identifier':
                        inp_ident = child.text
                    elif child_tag == 'Data':
                        for data_child in child:
                            data_tag = data_child.tag.split('}')[-1] if '}' in data_child.tag else data_child.tag
                            if data_tag == 'LiteralData':
                                inp_value = data_child.text
                if inp_ident and inp_value:
                    inputs_data[inp_ident] = inp_value
        
        result = execute_process(identifier, inputs_data)
        return app.response_class(response=result, status=200, mimetype='application/xml')
    else:
        return app.response_class(
            response=generate_exception("OperationNotSupported", f"Unsupported operation: {local_tag}"),
            status=400, mimetype='application/xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
