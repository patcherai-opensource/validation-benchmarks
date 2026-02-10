import os
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Template, engines
from django.conf import settings


def get_template_path(layout_name):
    if not os.path.splitext(layout_name)[1]:
        layout_name = layout_name + '.html'
    
    layouts_dir = os.path.join(settings.BASE_DIR, 'templates', 'layouts')
    return os.path.join(layouts_dir, layout_name)


def render_page(request):
    layout = request.GET.get('layout', 'default')
    title = request.GET.get('title', 'Welcome')
    content = request.GET.get('content', 'Welcome to our content management system.')
    
    layout_path = get_template_path(layout)
    
    try:
        with open(layout_path, 'r') as f:
            layout_content = f.read()
    except FileNotFoundError:
        return HttpResponse('Layout not found', status=404)
    except Exception:
        return HttpResponse('Error loading layout', status=500)
    
    if layout_path.endswith('.html'):
        engine = engines["django"]
        template = engine.from_string(layout_content)
        context = {
            'title': title,
            'content': content,
            'page_name': 'home',
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse(layout_content, content_type='text/plain')


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)
