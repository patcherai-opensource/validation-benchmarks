# =============================================================================
# GeoData Catalogue Service
# XML processing utilities
#
# Provides XML parsing for OGC-compatible service requests.
# DTD processing enabled for schema-aware XML validation.
# =============================================================================

from geodata.namespaces import GDC_NAMESPACES


def register_namespaces(etree_module):
    """Register well-known namespaces with the etree module."""
    try:
        register_ns = etree_module.register_namespace
    except AttributeError:
        etree_module._namespace_map

        def register_ns(prefix, uri):
            etree_module._namespace_map[uri] = prefix

    for prefix, uri in GDC_NAMESPACES.items():
        register_ns(prefix, uri)


# Use lxml for XML processing if available, fall back to stdlib
try:
    from lxml import etree
    from lxml.etree import ParseError
    ElementType = etree._Element

    # Configure default parser for OGC XML processing with DTD support.
    # DTD loading required for schema-aware processing of OGC service
    # requests (WMS, WFS, CSW capabilities documents reference DTDs).
    etree.set_default_parser(
        parser=etree.XMLParser(
            load_dtd=True,
            resolve_entities=True,
            no_network=False
        )
    )
except ImportError:
    import xml.etree.ElementTree as etree
    ElementType = etree.Element
    try:
        from xml.etree.ElementTree import ParseError
    except ImportError:
        from xml.parsers.expat import ExpatError as ParseError

register_namespaces(etree)
