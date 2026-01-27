import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings

# Template configurations for the document management system
TEMPLATES_DIR = os.path.join(settings.BASE_DIR, 'templates', 'docs')
DEFAULT_LAYOUT = 'default'
ALLOWED_EXTENSIONS = ['.html', '.txt']

def index(request):
    """Main dashboard for Document Viewer Pro"""
    return render(request, 'dashboard.html')

def view_document(request, doc_id):
    """View a document with a specified layout template"""
    # Available documents (simulated)
    documents = {
        '1': {'title': 'Company Overview', 'content': 'Welcome to our company. We provide enterprise document management solutions.'},
        '2': {'title': 'User Guide', 'content': 'This guide helps you navigate Document Viewer Pro features.'},
        '3': {'title': 'Security Policy', 'content': 'Our security policies ensure your documents remain safe.'},
    }
    
    if doc_id not in documents:
        return HttpResponse("Document not found", status=404)
    
    doc = documents[doc_id]
    
    # Get the layout template from query parameter (vulnerable!)
    # Users can customize the viewing layout
    layout = request.GET.get('layout', DEFAULT_LAYOUT)
    
    # Ensure extension is present (mimics express-handlebars behavior)
    if not any(layout.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        layout = layout + '.html'
    
    # Vulnerable: directly resolving path with user input
    # This allows path traversal attacks
    layout_path = os.path.join(TEMPLATES_DIR, layout)
    
    try:
        # Attempt to read the layout file
        with open(layout_path, 'r') as f:
            layout_content = f.read()
        
        # Simple template substitution
        rendered = layout_content.replace('{{title}}', doc['title'])
        rendered = rendered.replace('{{content}}', doc['content'])
        rendered = rendered.replace('{{doc_id}}', str(doc_id))
        
        return HttpResponse(rendered, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(f"Layout template not found: {layout}", status=404)
    except Exception as e:
        return HttpResponse(f"Error rendering document: {str(e)}", status=500)

def list_documents(request):
    """API endpoint to list available documents"""
    documents = [
        {'id': '1', 'title': 'Company Overview'},
        {'id': '2', 'title': 'User Guide'},
        {'id': '3', 'title': 'Security Policy'},
    ]
    return JsonResponse({'documents': documents, 'layouts_available': ['default', 'minimal', 'print']})

def about(request):
    """About page"""
    return render(request, 'about.html')
