# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================


class Namespaces(object):
    """
    Provides OGC/ISO namespace definitions.
    """

    _namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'csw': 'http://www.opengis.net/cat/csw/2.0.2',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dct': 'http://purl.org/dc/terms/',
        'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
        'fes': 'http://www.opengis.net/fes/2.0',
        'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
        'gmd': 'http://www.isotc211.org/2005/gmd',
        'gml': 'http://www.opengis.net/gml',
        'gml32': 'http://www.opengis.net/gml/3.2',
        'gmx': 'http://www.isotc211.org/2005/gmx',
        'ogc': 'http://www.opengis.net/ogc',
        'ows': 'http://www.opengis.net/ows',
        'ows110': 'http://www.opengis.net/ows/1.1',
        'ows200': 'http://www.opengis.net/ows/2.0',
        'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
        'se': 'http://www.opengis.net/se',
        'sml': 'http://www.opengis.net/sensorML/1.0.1',
        'sml101': 'http://www.opengis.net/sensorML/1.0.1',
        'sos': 'http://www.opengis.net/sos/1.0',
        'sos20': 'http://www.opengis.net/sos/2.0',
        'swe': 'http://www.opengis.net/swe/1.0.1',
        'swe101': 'http://www.opengis.net/swe/1.0.1',
        'swe20': 'http://www.opengis.net/swe/2.0',
        'swes': 'http://www.opengis.net/swes/2.0',
        'wcs': 'http://www.opengis.net/wcs',
        'wfs': 'http://www.opengis.net/wfs',
        'wfs20': 'http://www.opengis.net/wfs/2.0',
        'wms': 'http://www.opengis.net/wms',
        'wmts': 'http://www.opengis.net/wmts/1.0',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'wps100': 'http://www.opengis.net/wps/1.0.0',
        'wps200': 'http://www.opengis.net/wps/2.0',
        'xs': 'http://www.w3.org/2001/XMLSchema',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xlink': 'http://www.w3.org/1999/xlink',
    }

    def get_namespaces(self, keys=None):
        """Return namespace dict, optionally filtered by keys."""
        if keys is not None:
            return {k: v for k, v in self._namespaces.items() if k in keys}
        return self._namespaces

    def get_namespace(self, key):
        """Return a single namespace URI by prefix."""
        return self._namespaces.get(key)

    def get_versioned_namespace(self, key, version=None):
        """Return namespace URI, trying versioned variants first."""
        if version:
            versioned_key = '%s%s' % (key, version.replace('.', ''))
            if versioned_key in self._namespaces:
                return self._namespaces[versioned_key]
        return self._namespaces.get(key)
