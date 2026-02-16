# =============================================================================
# GeoData Catalogue Service
# Namespace definitions for OGC and internal use
# =============================================================================

GDC_NAMESPACES = {
    'gdc': 'http://geodata.example.com/gdc',
    'ogc': 'http://www.opengis.net/ogc',
    'gml': 'http://www.opengis.net/gml',
    'ows': 'http://www.opengis.net/ows',
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xlink': 'http://www.w3.org/1999/xlink',
    'wms': 'http://www.opengis.net/wms',
    'wfs': 'http://www.opengis.net/wfs',
    'wcs': 'http://www.opengis.net/wcs',
}


def nspath(path, ns_key='gdc'):
    """Build a namespace-qualified path."""
    ns = GDC_NAMESPACES.get(ns_key, '')
    if ns:
        return '{%s}%s' % (ns, path)
    return path
