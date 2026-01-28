from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
import os

# Configuration for the content inclusion feature
# Only files under these roots can be included
ALLOWED_INCLUDE_ROOTS = ('/app/content/',)

def include_is_allowed(filepath):
    """
    Check if a file path is allowed for inclusion.
    Vulnerable: does not normalize the path before checking!
    """
    for root in ALLOWED_INCLUDE_ROOTS:
        if filepath.startswith(root):
            return True
    return False

def index(request):
    return render(request, 'index.html')

def docs(request):
    """Documentation page"""
    return render(request, 'docs.html')

def preview(request):
    """
    Preview content from an allowed directory.
    Accepts a 'file' parameter to specify which content file to include.
    """
    filepath = request.GET.get('file', '')
    
    if not filepath:
        return render(request, 'preview.html', {'content': None, 'error': None})
    
    # Check if the file is in an allowed root (VULNERABLE CHECK!)
    if not include_is_allowed(filepath):
        return render(request, 'preview.html', {
            'content': None,
            'error': f'Access denied: File must be under an allowed content root.'
        })
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return render(request, 'preview.html', {'content': content, 'error': None, 'filepath': filepath})
    except FileNotFoundError:
        return render(request, 'preview.html', {
            'content': None,
            'error': f'File not found: {filepath}'
        })
    except Exception as e:
        return render(request, 'preview.html', {
            'content': None,
            'error': f'Error reading file: {str(e)}'
        })

def content_list(request):
    """List available content files"""
    content_dir = '/app/content/'
    try:
        files = []
        for f in os.listdir(content_dir):
            if os.path.isfile(os.path.join(content_dir, f)):
                files.append({
                    'name': f,
                    'path': os.path.join(content_dir, f)
                })
        return JsonResponse({'files': files})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def about(request):
    """About page"""
    return render(request, 'about.html')

def search(request):
    """Search feature - non-vulnerable endpoint"""
    query = request.GET.get('q', '')
    results = []
    if query:
        # Simulate a search - not vulnerable
        content_dir = '/app/content/'
        try:
            for f in os.listdir(content_dir):
                filepath = os.path.join(content_dir, f)
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as file:
                        if query.lower() in file.read().lower():
                            results.append(f)
        except:
            pass
    return render(request, 'search.html', {'query': query, 'results': results})
