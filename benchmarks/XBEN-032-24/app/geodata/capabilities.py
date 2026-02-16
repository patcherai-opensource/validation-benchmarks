# =============================================================================
# GeoData Catalogue Service
# Capabilities document generator
# =============================================================================


def get_capabilities_document(catalogue):
    """Generate a GetCapabilities response document."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Capabilities xmlns="http://geodata.example.com/gdc"
              xmlns:ows="http://www.opengis.net/ows"
              xmlns:ogc="http://www.opengis.net/ogc"
              xmlns:xlink="http://www.w3.org/1999/xlink"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              version="{version}">
  <ows:ServiceIdentification>
    <ows:Title>{title}</ows:Title>
    <ows:Abstract>{abstract}</ows:Abstract>
    <ows:ServiceType>GDC</ows:ServiceType>
    <ows:ServiceTypeVersion>{version}</ows:ServiceTypeVersion>
    <ows:Keywords>
      <ows:Keyword>geospatial</ows:Keyword>
      <ows:Keyword>metadata</ows:Keyword>
      <ows:Keyword>catalogue</ows:Keyword>
      <ows:Keyword>OGC</ows:Keyword>
    </ows:Keywords>
  </ows:ServiceIdentification>
  <ows:ServiceProvider>
    <ows:ProviderName>GeoData Services</ows:ProviderName>
    <ows:ProviderSite xlink:href="http://geodata.example.com"/>
    <ows:ServiceContact>
      <ows:IndividualName>GeoData Admin</ows:IndividualName>
      <ows:ContactInfo>
        <ows:OnlineResource xlink:href="http://geodata.example.com/support"/>
      </ows:ContactInfo>
    </ows:ServiceContact>
  </ows:ServiceProvider>
  <ows:OperationsMetadata>
    <ows:Operation name="GetCapabilities">
      <ows:DCP>
        <ows:HTTP>
          <ows:Get xlink:href="/catalogue/capabilities"/>
        </ows:HTTP>
      </ows:DCP>
    </ows:Operation>
    <ows:Operation name="GetRecords">
      <ows:DCP>
        <ows:HTTP>
          <ows:Post xlink:href="/catalogue/query"/>
        </ows:HTTP>
      </ows:DCP>
      <ows:Parameter name="outputFormat">
        <ows:Value>application/xml</ows:Value>
      </ows:Parameter>
      <ows:Parameter name="outputSchema">
        <ows:Value>http://geodata.example.com/gdc</ows:Value>
      </ows:Parameter>
    </ows:Operation>
    <ows:Operation name="GetRecordById">
      <ows:DCP>
        <ows:HTTP>
          <ows:Post xlink:href="/catalogue/query"/>
        </ows:HTTP>
      </ows:DCP>
    </ows:Operation>
    <ows:Operation name="DescribeRecord">
      <ows:DCP>
        <ows:HTTP>
          <ows:Get xlink:href="/catalogue/describe"/>
        </ows:HTTP>
      </ows:DCP>
    </ows:Operation>
  </ows:OperationsMetadata>
  <ogc:Filter_Capabilities>
    <ogc:Scalar_Capabilities>
      <ogc:ComparisonOperators>
        <ogc:ComparisonOperator>PropertyIsEqualTo</ogc:ComparisonOperator>
        <ogc:ComparisonOperator>PropertyIsLike</ogc:ComparisonOperator>
      </ogc:ComparisonOperators>
    </ogc:Scalar_Capabilities>
    <ogc:Spatial_Capabilities>
      <ogc:SpatialOperators>
        <ogc:SpatialOperator name="BBOX"/>
      </ogc:SpatialOperators>
    </ogc:Spatial_Capabilities>
  </ogc:Filter_Capabilities>
</Capabilities>'''.format(
        version=catalogue.version,
        title=catalogue.title,
        abstract=catalogue.abstract
    )
