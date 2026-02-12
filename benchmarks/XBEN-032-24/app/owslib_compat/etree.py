# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
# =============================================================================


from lxml import etree
from lxml.etree import ParseError
ElementType = etree._Element

from owslib_compat.namespaces import Namespaces


def patch_well_known_namespaces(etree_mod=None):
    """Monkey patches lxml.etree to add some well-known namespaces."""

    if etree_mod is None:
        etree_mod = etree

    ns = Namespaces()

    try:
        register_namespace = etree_mod.register_namespace
    except AttributeError:
        etree_mod._namespace_map

        def register_namespace(prefix, uri):
            etree_mod._namespace_map[uri] = prefix

    for k, v in list(ns.get_namespaces().items()):
        register_namespace(k, v)


patch_well_known_namespaces(etree)
