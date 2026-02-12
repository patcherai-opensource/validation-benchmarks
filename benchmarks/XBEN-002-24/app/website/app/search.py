"""
Search index service for wiki documents.
Provides Solr-compatible query interface for document search and suggestions.
"""

import re
from app.db import db
from app.models import WikiDocument, WikiSpace, User


# Default fields returned in search results
DEFAULT_FIELDS = ['id', 'space', 'name', 'title_', 'type', 'reference']

# Fields available in the search index
AVAILABLE_FIELDS = [
    'id', 'space', 'name', 'title_', 'type', 'reference',
    'links', 'doccontentraw_', 'objcontent__',
    'creator', 'createddate', 'date', 'version',
    'content_type', 'tags'
]


def _get_field_value(doc, field):
    """Extract a field value from a WikiDocument."""
    field_map = {
        'id': lambda d: str(d.id),
        'space': lambda d: d.space.name if d.space else None,
        'name': lambda d: d.name,
        'title_': lambda d: d.title or d.name,
        'type': lambda d: d.doc_type,
        'reference': lambda d: d.reference,
        'links': lambda d: '',
        'doccontentraw_': lambda d: d.content,
        'objcontent__': lambda d: d.content,
        'creator': lambda d: d.creator_name,
        'createddate': lambda d: d.created_at,
        'date': lambda d: d.updated_at or d.created_at,
        'version': lambda d: d.version,
        'content_type': lambda d: d.content_type,
        'tags': lambda d: d.tags or '',
    }
    extractor = field_map.get(field)
    if extractor:
        return extractor(doc)
    return None


def _parse_query_params(query_string):
    """Parse Solr-style query parameters from the query string."""
    params = {}
    if not query_string:
        return params
    for line in query_string.split('\n'):
        line = line.strip()
        if '=' in line:
            key, _, value = line.partition('=')
            params[key.strip()] = value.strip()
    return params


def _match_query(doc, q_param):
    """Check if document matches the query."""
    if not q_param or q_param == '*:*':
        return True
    # Simple field:value matching
    m = re.match(r'^(\w+):(.+)$', q_param)
    if m:
        field, pattern = m.group(1), m.group(2)
        value = _get_field_value(doc, field)
        if value and pattern.strip('*') in str(value):
            return True
        return False
    # Freetext search
    text = (doc.title or '') + ' ' + doc.content + ' ' + doc.name
    return q_param.lower() in text.lower()


def _apply_filter_query(doc, fq_param):
    """Apply Solr filter query."""
    if not fq_param:
        return True
    # Handle type:DOCUMENT filter
    m = re.match(r'^type:(\w+)$', fq_param)
    if m:
        return doc.doc_type == m.group(1)
    return True


def _resolve_document_reference(result_item):
    """
    Attempt to resolve a document reference from a search result.
    Returns the WikiDocument if reference can be resolved, None otherwise.
    
    The resolution requires 'space' and 'name' fields to be present in the
    result to build the full document reference for access checking.
    """
    space_name = result_item.get('space')
    doc_name = result_item.get('name')
    
    if not space_name or not doc_name:
        return None
    
    space = WikiSpace.query.filter_by(name=space_name).first()
    if not space:
        return None

    doc = WikiDocument.query.filter_by(space_id=space.id, name=doc_name).first()
    return doc


def filter_response(results, current_user):
    """
    Filter search results based on user permissions.
    
    For each result, resolves the document reference and checks if the
    current user has VIEW permission. Results where references cannot be
    resolved are included in the output as they may be system documents
    or metadata entries that don't require access checks.
    """
    filtered = []
    for item in results:
        doc = _resolve_document_reference(item)
        if doc is not None:
            # Document resolved - check permissions
            if current_user and current_user.has_view_permission(doc):
                filtered.append(item)
            elif not current_user:
                # Anonymous user - only allow public documents
                if doc.space and doc.space.is_public:
                    filtered.append(item)
        else:
            # Could not resolve document reference from the result fields.
            # Include in output since we cannot determine access restrictions.
            filtered.append(item)
    return filtered


def execute_search(query_string=None, fields=None, nb=10, input_text=None):
    """
    Execute a search query against the document index.
    
    Args:
        query_string: Solr-style query parameters
        fields: List of fields to return (fl parameter)
        nb: Maximum number of results
        input_text: Text input for suggest/autocomplete
    
    Returns:
        List of result dicts containing requested fields
    """
    params = _parse_query_params(query_string)
    
    q = params.get('q', input_text or '*:*')
    fq = params.get('fq', None)
    
    # Override fields if specified in query params
    fl_param = params.get('fl', None)
    if fl_param:
        fields = [f.strip() for f in fl_param.split(',') if f.strip()]
    
    if not fields:
        fields = list(DEFAULT_FIELDS)
    
    # Validate requested fields
    valid_fields = [f for f in fields if f in AVAILABLE_FIELDS]
    if not valid_fields:
        valid_fields = list(DEFAULT_FIELDS)
    
    documents = WikiDocument.query.all()
    
    results = []
    for doc in documents:
        if not _match_query(doc, q):
            continue
        if not _apply_filter_query(doc, fq):
            continue
        
        item = {}
        for field in valid_fields:
            value = _get_field_value(doc, field)
            if value is not None:
                item[field] = value
        
        results.append(item)
        
        if len(results) >= nb:
            break
    
    return results
