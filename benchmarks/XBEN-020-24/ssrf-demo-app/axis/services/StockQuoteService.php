<?php
header('Content-Type: text/xml; charset=utf-8');
header('X-Powered-By: Axis/1.3');

if (isset($_GET['wsdl'])) {
    echo '<?xml version="1.0" encoding="UTF-8"?>';
    ?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:tns="http://axis.apache.org/samples"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    name="StockQuoteService"
    targetNamespace="http://axis.apache.org/samples">
    <wsdl:types>
        <xsd:schema targetNamespace="http://axis.apache.org/samples">
            <xsd:element name="getQuote">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="symbol" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="getQuoteResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="return" type="xsd:float"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </wsdl:types>
    <wsdl:message name="getQuoteRequest">
        <wsdl:part element="tns:getQuote" name="parameters"/>
    </wsdl:message>
    <wsdl:message name="getQuoteResponse">
        <wsdl:part element="tns:getQuoteResponse" name="parameters"/>
    </wsdl:message>
    <wsdl:portType name="StockQuotePortType">
        <wsdl:operation name="getQuote">
            <wsdl:input message="tns:getQuoteRequest"/>
            <wsdl:output message="tns:getQuoteResponse"/>
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="StockQuoteBinding" type="tns:StockQuotePortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="getQuote">
            <soap:operation soapAction="getQuote"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="StockQuoteService">
        <wsdl:port binding="tns:StockQuoteBinding" name="StockQuotePort">
            <soap:address location="/axis/services/StockQuoteService"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>
    <?php
} else {
    echo '<?xml version="1.0" encoding="UTF-8"?>';
    ?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:samp="http://axis.apache.org/samples">
    <soapenv:Body>
        <samp:getQuoteResponse>
            <return>55.25</return>
        </samp:getQuoteResponse>
    </soapenv:Body>
</soapenv:Envelope>
    <?php
}
