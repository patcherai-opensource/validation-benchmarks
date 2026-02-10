from flask import Flask, request, render_template
from lxml import etree
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
WPS_NS = 'http://www.opengis.net/wps/1.0.0'
OWS_NS = 'http://www.opengis.net/ows/1.1'

NAMESPACES = {
    'wps': WPS_NS,
    'ows': OWS_NS
}

# Available WPS processes
AVAILABLE_PROCESSES = {
    'echo': {
        'title': 'Echo Process',
        'abstract': 'A simple process that echoes back the input data',
        'inputs': ['inputdata'],
        'outputs': ['outputdata']
    },
    'buffer': {
        'title': 'Buffer Process',
        'abstract': 'Creates a buffer around a geometry',
        'inputs': ['geometry', 'distance'],
        'outputs': ['buffered']
    }
}


class WPSRequest:
    """Simplified WPS Request handler - mimics PyWPS vulnerable parsing"""
    
    def __init__(self):
        self.operation = None
        self.identifier = None
        self.inputs = {}
    
    def _post_request(self, http_request):
        """
        Process POST request - vulnerable to XXE
        This mimics the vulnerable code in pywps/app/WPSRequest.py
        where lxml.etree.fromstring() is used without disabling entity resolution
        """
        # VULNERABLE: Uses lxml.etree.fromstring without disabling entities
        # This is the same vulnerability as in PyWPS < 4.5.0
        doc = etree.fromstring(http_request.get_data())
        
        # Determine the operation from root tag
        root_tag = doc.tag.split('}')[-1] if '}' in doc.tag else doc.tag
        
        if root_tag == 'GetCapabilities':
            self.operation = 'getcapabilities'
        elif root_tag == 'DescribeProcess':
            self.operation = 'describeprocess'
            # Get process identifier
            identifier_elem = doc.find('.//{%s}Identifier' % OWS_NS)
            if identifier_elem is not None:
                self.identifier = identifier_elem.text
        elif root_tag == 'Execute':
            self.operation = 'execute'
            # Get process identifier
            identifier_elem = doc.find('.//{%s}Identifier' % OWS_NS)
            if identifier_elem is not None:
                self.identifier = identifier_elem.text
            
            # Parse inputs - this is where XXE payload will be reflected
            data_inputs = doc.find('.//{%s}DataInputs' % WPS_NS)
            if data_inputs is not None:
                for input_elem in data_inputs.findall('.//{%s}Input' % WPS_NS):
                    input_id_elem = input_elem.find('.//{%s}Identifier' % OWS_NS)
                    literal_data_elem = input_elem.find('.//{%s}LiteralData' % WPS_NS)
                    
                    if input_id_elem is not None and literal_data_elem is not None:
                        input_id = input_id_elem.text
                        input_value = literal_data_elem.text
                        self.inputs[input_id] = input_value
        
        return self


def generate_capabilities_response():
    """Generate WPS GetCapabilities response"""
    response = '''<?xml version="1.0" encoding="UTF-8"?>
<wps:Capabilities xmlns:wps="{wps}" xmlns:ows="{ows}" version="1.0.0">
    <ows:ServiceIdentification>
        <ows:Title>PyWPS Test Server</ows:Title>
        <ows:Abstract>Web Processing Service for geospatial data processing</ows:Abstract>
        <ows:ServiceType>WPS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
    </ows:ServiceIdentification>
    <wps:ProcessOfferings>'''.format(wps=WPS_NS, ows=OWS_NS)
    
    for proc_id, proc_info in AVAILABLE_PROCESSES.items():
        response += '''
        <wps:Process>
            <ows:Identifier>{id}</ows:Identifier>
            <ows:Title>{title}</ows:Title>
            <ows:Abstract>{abstract}</ows:Abstract>
        </wps:Process>'''.format(id=proc_id, title=proc_info['title'], abstract=proc_info['abstract'])
    
    response += '''
    </wps:ProcessOfferings>
</wps:Capabilities>'''
    return response


def generate_describe_response(identifier):
    """Generate WPS DescribeProcess response"""
    if identifier not in AVAILABLE_PROCESSES:
        return generate_exception_response('InvalidParameterValue', 'Unknown process: ' + str(identifier))
    
    proc = AVAILABLE_PROCESSES[identifier]
    response = '''<?xml version="1.0" encoding="UTF-8"?>
<wps:ProcessDescriptions xmlns:wps="{wps}" xmlns:ows="{ows}" version="1.0.0">
    <ProcessDescription>
        <ows:Identifier>{id}</ows:Identifier>
        <ows:Title>{title}</ows:Title>
        <ows:Abstract>{abstract}</ows:Abstract>
        <DataInputs>'''.format(wps=WPS_NS, ows=OWS_NS, id=identifier, title=proc['title'], abstract=proc['abstract'])
    
    for inp in proc['inputs']:
        response += '''
            <Input>
                <ows:Identifier>{}</ows:Identifier>
                <LiteralData>
                    <ows:DataType>string</ows:DataType>
                </LiteralData>
            </Input>'''.format(inp)
    
    response += '''
        </DataInputs>
        <ProcessOutputs>'''
    
    for out in proc['outputs']:
        response += '''
            <Output>
                <ows:Identifier>{}</ows:Identifier>
                <LiteralOutput>
                    <ows:DataType>string</ows:DataType>
                </LiteralOutput>
            </Output>'''.format(out)
    
    response += '''
        </ProcessOutputs>
    </ProcessDescription>
</wps:ProcessDescriptions>'''
    return response


def generate_execute_response(identifier, inputs):
    """Generate WPS Execute response - reflects input values (including XXE payloads)"""
    if identifier not in AVAILABLE_PROCESSES:
        return generate_exception_response('InvalidParameterValue', 'Unknown process: ' + str(identifier))
    
    proc = AVAILABLE_PROCESSES[identifier]
    
    # Process the inputs and generate outputs
    # The 'echo' process simply echoes back input - perfect for XXE exfiltration
    output_value = ''
    if identifier == 'echo':
        output_value = inputs.get('inputdata', '')
    elif identifier == 'buffer':
        geometry = inputs.get('geometry', '')
        distance = inputs.get('distance', '1')
        output_value = 'Buffered geometry: {} with distance {}'.format(geometry, distance)
    
    response = '''<?xml version="1.0" encoding="UTF-8"?>
<wps:ExecuteResponse xmlns:wps="{wps}" xmlns:ows="{ows}" version="1.0.0">
    <wps:Process>
        <ows:Identifier>{id}</ows:Identifier>
        <ows:Title>{title}</ows:Title>
    </wps:Process>
    <wps:Status>
        <wps:ProcessSucceeded>Process completed successfully</wps:ProcessSucceeded>
    </wps:Status>
    <wps:ProcessOutputs>
        <wps:Output>
            <ows:Identifier>outputdata</ows:Identifier>
            <wps:Data>
                <wps:LiteralData>{output}</wps:LiteralData>
            </wps:Data>
        </wps:Output>
    </wps:ProcessOutputs>
</wps:ExecuteResponse>'''.format(wps=WPS_NS, ows=OWS_NS, id=identifier, title=proc['title'], output=output_value)
    return response


def generate_exception_response(code, text):
    """Generate WPS Exception response"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="{ows}" version="1.0.0">
    <ows:Exception exceptionCode="{code}">
        <ows:ExceptionText>{text}</ows:ExceptionText>
    </ows:Exception>
</ows:ExceptionReport>'''.format(ows=OWS_NS, code=code, text=text)


@app.route('/')
def index():
    """Landing page with service information"""
    return render_template('index.html')


@app.route('/wps', methods=['GET', 'POST'])
def wps_service():
    """
    WPS Service endpoint - mimics PyWPS behavior
    Vulnerable to XXE when processing POST requests
    """
    try:
        if request.method == 'GET':
            # Handle GET requests via query parameters
            service = request.args.get('service', '').upper()
            req_type = request.args.get('request', '').lower()
            
            if service != 'WPS':
                return app.response_class(
                    response=generate_exception_response('InvalidParameterValue', 'Service must be WPS'),
                    status=400,
                    mimetype='application/xml'
                )
            
            if req_type == 'getcapabilities':
                return app.response_class(
                    response=generate_capabilities_response(),
                    status=200,
                    mimetype='application/xml'
                )
            elif req_type == 'describeprocess':
                identifier = request.args.get('identifier', '')
                return app.response_class(
                    response=generate_describe_response(identifier),
                    status=200,
                    mimetype='application/xml'
                )
            else:
                return app.response_class(
                    response=generate_exception_response('InvalidParameterValue', 'Unknown request type'),
                    status=400,
                    mimetype='application/xml'
                )
        
        elif request.method == 'POST':
            # Handle POST requests - XML body
            # VULNERABLE: WPSRequest._post_request uses lxml.etree.fromstring 
            # without disabling external entities
            wps_request = WPSRequest()
            wps_request._post_request(request)
            
            if wps_request.operation == 'getcapabilities':
                return app.response_class(
                    response=generate_capabilities_response(),
                    status=200,
                    mimetype='application/xml'
                )
            elif wps_request.operation == 'describeprocess':
                return app.response_class(
                    response=generate_describe_response(wps_request.identifier),
                    status=200,
                    mimetype='application/xml'
                )
            elif wps_request.operation == 'execute':
                return app.response_class(
                    response=generate_execute_response(wps_request.identifier, wps_request.inputs),
                    status=200,
                    mimetype='application/xml'
                )
            else:
                return app.response_class(
                    response=generate_exception_response('InvalidParameterValue', 'Unknown operation'),
                    status=400,
                    mimetype='application/xml'
                )
    
    except etree.XMLSyntaxError as e:
        return app.response_class(
            response=generate_exception_response('InvalidParameterValue', 'XML parsing error: ' + str(e)),
            status=400,
            mimetype='application/xml'
        )
    except Exception as e:
        return app.response_class(
            response=generate_exception_response('NoApplicableCode', 'Server error: ' + str(e)),
            status=500,
            mimetype='application/xml'
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
