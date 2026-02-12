<?php
require_once dirname(__FILE__) . '/../lib/auth.php';

header('Content-Type: text/xml; charset=utf-8');
header('X-Powered-By: Axis/1.3');

if (isset($_GET['wsdl'])) {
    echo '<?xml version="1.0" encoding="UTF-8"?>';
    ?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:tns="http://axis.apache.org/admin"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    name="AdminService"
    targetNamespace="http://axis.apache.org/admin">
    <wsdl:types>
        <xsd:schema targetNamespace="http://axis.apache.org/admin">
            <xsd:element name="listServicesResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="service" type="xsd:string" maxOccurs="unbounded"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </wsdl:types>
    <wsdl:message name="listServicesResponse">
        <wsdl:part element="tns:listServicesResponse" name="parameters"/>
    </wsdl:message>
    <wsdl:portType name="AdminPortType">
        <wsdl:operation name="listServices">
            <wsdl:output message="tns:listServicesResponse"/>
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="AdminBinding" type="tns:AdminPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="listServices">
            <soap:operation soapAction="listServices"/>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="AdminService">
        <wsdl:port binding="tns:AdminBinding" name="AdminPort">
            <soap:address location="/axis/services/AdminService"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>
    <?php
} else {
    if (!isAdminAuthenticated()) {
        header('HTTP/1.0 401 Unauthorized');
        echo '<?xml version="1.0" encoding="UTF-8"?>';
        echo '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">';
        echo '<soapenv:Body><soapenv:Fault><faultstring>Authentication required for AdminService</faultstring></soapenv:Fault></soapenv:Body>';
        echo '</soapenv:Envelope>';
        exit;
    }
    
    echo '<?xml version="1.0" encoding="UTF-8"?>';
    ?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:adm="http://axis.apache.org/admin">
    <soapenv:Body>
        <adm:listServicesResponse>
            <service>AdminService</service>
            <service>Version</service>
            <service>StockQuoteService</service>
        </adm:listServicesResponse>
    </soapenv:Body>
</soapenv:Envelope>
    <?php
}
