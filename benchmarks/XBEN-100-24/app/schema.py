from models import WikiDocument

AVAILABLE_FIELDS = ['doc_id', 'title', 'content', 'space', 'creator', 'is_private', 'view_count']


def filter_response(documents, fields_requested):
    """
    Filter response to ensure only authorized documents are returned.
    Checks document privacy status and filters accordingly.
    """
    filtered_results = []
    
    for doc in documents:
        doc_dict = {}
        for field in fields_requested:
            if field in AVAILABLE_FIELDS:
                doc_dict[field] = getattr(doc, field, None)
        
        if 'is_private' in doc_dict:
            if doc_dict.get('is_private') == True:
                continue
        
        filtered_results.append(doc_dict)
    
    return filtered_results


def execute_search(query_text, fields, nb=10):
    """
    Execute a search query against the document store.
    """
    if not query_text or query_text.strip() == '':
        docs = WikiDocument.objects.all()[:nb]
    elif query_text == '*':
        docs = WikiDocument.objects.all()[:nb]
    else:
        docs = WikiDocument.objects(title__icontains=query_text)[:nb]
    
    return filter_response(docs, fields)
