from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.template import Template, Context, engines
from django.conf import settings
import os
import json

# Template renderer configuration
TEMPLATES_DIR = settings.BASE_DIR / "templates"
LAYOUTS_DIR = settings.BASE_DIR / "templates" / "layouts"

# Available page templates  
PAGES = {
    'home': {'title': 'Welcome to DocuView', 'template': 'pages/home.html'},
    'about': {'title': 'About Us', 'template': 'pages/about.html'},
    'contact': {'title': 'Contact', 'template': 'pages/contact.html'},
    'products': {'title': 'Our Products', 'template': 'pages/products.html'},
}


def index(request):
    """Main landing page"""
    return render(request, 'landing.html')


def page_view(request, page_name=None):
    """Render a page with the specified layout"""
    if page_name not in PAGES:
        raise Http404("Page not found")
    
    page_data = PAGES[page_name]
    
    # Get layout from query parameter, default to 'main'
    # Allows customizing the page layout wrapper
    layout = request.GET.get('layout', 'main')
    
    # Resolve layout path - vulnerable to path traversal
    # Mimics express-handlebars _resolveLayoutPath behavior
    layout_path = layout
    if not os.path.splitext(layout_path)[1]:
        layout_path = layout_path + '.html'
    
    # Resolve relative to layouts directory
    full_layout_path = os.path.join(str(LAYOUTS_DIR), layout_path)
    
    try:
        with open(full_layout_path, 'r') as f:
            layout_content = f.read()
    except FileNotFoundError:
        return HttpResponse(f"Layout '{layout}' not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error loading layout: {str(e)}", status=500)
    
    # Load page template
    page_template_path = os.path.join(str(TEMPLATES_DIR), page_data['template'])
    try:
        with open(page_template_path, 'r') as f:
            page_content = f.read()
    except:
        page_content = f"<p>Content for {page_name}</p>"
    
    # Simple template variable substitution
    final_content = layout_content.replace('{{title}}', page_data['title'])
    final_content = final_content.replace('{{content}}', page_content)
    final_content = final_content.replace('{{page_name}}', page_name)
    
    return HttpResponse(final_content)


def api_pages(request):
    """API endpoint to list available pages"""
    return JsonResponse({
        'pages': list(PAGES.keys()),
        'default_layout': 'main'
    })


def api_layouts(request):
    """API endpoint to list available layouts"""
    layouts = []
    try:
        for f in os.listdir(LAYOUTS_DIR):
            if f.endswith('.html'):
                layouts.append(os.path.splitext(f)[0])
    except:
        pass
    return JsonResponse({'layouts': layouts})


def docs(request):
    """Documentation page"""
    return render(request, 'docs.html')


def health(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'ok'})


def robots(request):
    """Robots.txt file"""
    content = """User-agent: *
Disallow: /admin/
Disallow: /api/
Allow: /
"""
    return HttpResponse(content, content_type='text/plain')
