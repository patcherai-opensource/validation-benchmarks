import os
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.conf import settings


def include_is_allowed(filepath):
    """
    Check if the given filepath is allowed to be included.
    Returns True if the filepath starts with one of ALLOWED_INCLUDE_ROOTS.
    """
    allowed_roots = getattr(settings, 'ALLOWED_INCLUDE_ROOTS', ())
    for root in allowed_roots:
        if filepath.startswith(root):
            return True
    return False


def view_document(request):
    """
    Document viewer endpoint - renders documents from the allowed directory.
    Supports include_file parameter for server-side includes.
    """
    doc_name = request.GET.get('doc', 'welcome')
    include_file = request.GET.get('include_file', '')
    
    included_content = ''
    
    if include_file:
        if include_is_allowed(include_file):
            try:
                with open(include_file, 'r') as f:
                    included_content = f.read()
            except (IOError, OSError):
                included_content = ''
    
    documents = {
        'welcome': {
            'title': 'Welcome to DocView',
            'content': 'Welcome to our document management system. Use the navigation to browse available documents.'
        },
        'about': {
            'title': 'About Us',
            'content': 'DocView is a secure document viewing platform for enterprise teams.'
        },
        'help': {
            'title': 'Help & Support',
            'content': 'For assistance, please contact our support team or browse the FAQ section.'
        },
        'privacy': {
            'title': 'Privacy Policy',
            'content': 'We take your privacy seriously. All documents are encrypted and access is strictly controlled.'
        }
    }
    
    document = documents.get(doc_name, documents['welcome'])
    
    return render(request, 'document.html', {
        'document': document,
        'included_content': included_content,
        'current_doc': doc_name
    })


def index(request):
    return render(request, 'index.html')
