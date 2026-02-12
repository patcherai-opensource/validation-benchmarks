<?php
header('Content-Type: text/xml; charset=utf-8');
header('X-Powered-By: Axis/1.3');

if (isset($_GET['wsdl'])) {
    echo '<?xml version="1.0" encoding="UTF-8"?>';
    ?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:tns="http://axis.apache.org/version"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    name="VersionService"
    targetNamespace="http://axis.apache.org/version">
    <wsdl:types>
        <xsd:schema targetNamespace="http://axis.apache.org/version">
            <xsd:element name="getVersionResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="return" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </wsdl:types>
    <wsdl:message name="getVersionResponse">
        <wsdl:part element="tns:getVersionResponse" name="parameters"/>
    </wsdl:message>
    <wsdl:portType name="VersionPortType">
        <wsdl:operation name="getVersion">
            <wsdl:output message="tns:getVersionResponse"/>
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="VersionBinding" type="tns:VersionPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="getVersion">
            <soap:operation soapAction="getVersion"/>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="VersionService">
        <wsdl:port binding="tns:VersionBinding" name="VersionPort">
            <soap:address location="/axis/services/Version"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>
    <?php
} else {
    echo '<?xml version="1.0" encoding="UTF-8"?>';
    ?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:ver="http://axis.apache.org/version">
    <soapenv:Body>
        <ver:getVersionResponse>
            <return>Apache Axis version: 1.3
Built on Oct 05, 2006 (04:45:02 PDT)</return>
        </ver:getVersionResponse>
    </soapenv:Body>
</soapenv:Envelope>
    <?php
}
