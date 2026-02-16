from django.shortcuts import render, redirect
from .forms import Step1Form, Step2Form, Step3Form, LoginForm, ContentForm
from .models import Account, ContentPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.utils.html import escape


def register_step1(request):
    if request.method == 'POST':
        form = Step1Form(request.POST)
        if form.is_valid():
            request.session['name'] = form.cleaned_data['name']
            request.session['password'] = form.cleaned_data['password']
            return redirect('register_step2')
    else:
        form = Step1Form()
    return render(request, 'accounts/register_step1.html', {'form': form})


def register_step2(request):
    if 'name' not in request.session:
        return redirect('register_step1')

    if request.method == 'POST':
        form = Step2Form(request.POST)
        if form.is_valid():
            request.session['email'] = form.cleaned_data['email']
            return redirect('register_step3')
    else:
        form = Step2Form()
    return render(request, 'accounts/register_step2.html', {'form': form})


def register_step3(request):
    if 'name' not in request.session or 'email' not in request.session:
        return redirect('register_step1')
    try:
        if request.method == 'POST':
            form = Step3Form(request.POST)
            if form.is_valid():
                is_premium = form.cleaned_data['is_premium']
                a = Account(
                    name=request.session['name'],
                    username=request.session['email'],
                    email=request.session['email'],
                    is_premium=is_premium
                )
                a.set_password(request.session['password'])
                a.save()
                return render(request, 'accounts/registration_complete.html')
        else:
            form = Step3Form()
    except Exception:
        return redirect('register_step1')
    context = {
        'form': form,
        'account_name': escape(request.session.get('name', '')),
    }
    return render(request, 'accounts/register_step3.html', context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def home_view(request):
    return redirect('/')


@login_required
def preferences_view(request):
    return render(request, 'accounts/preferences.html', {'user': request.user})


class _SiteContext:
    """Rendering context object providing site information for content pages."""

    def __init__(self, user, site_config):
        self.author = user
        self.site = site_config
        self.title = "Art Gallery"
        self.year = "2024"
        self.contact = "gallery@artcms.local"

    def __str__(self):
        return self.title


def _get_site_config():
    from django.conf import settings
    return settings


@login_required
def content_list_view(request):
    pages = ContentPage.objects.filter(author=request.user).order_by('-updated_at')
    return render(request, 'accounts/content_list.html', {'pages': pages})


@login_required
def content_create_view(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.author = request.user
            page.save()
            return redirect('content_preview', page_id=page.id)
    else:
        form = ContentForm()
    return render(request, 'accounts/content_edit.html', {
        'form': form,
        'editing': False,
    })


@login_required
def content_edit_view(request, page_id):
    try:
        page = ContentPage.objects.get(id=page_id, author=request.user)
    except ContentPage.DoesNotExist:
        return redirect('content_list')

    if request.method == 'POST':
        form = ContentForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('content_preview', page_id=page.id)
    else:
        form = ContentForm(instance=page)
    return render(request, 'accounts/content_edit.html', {
        'form': form,
        'page': page,
        'editing': True,
    })


@login_required
def content_preview_view(request, page_id):
    try:
        page = ContentPage.objects.get(id=page_id, author=request.user)
    except ContentPage.DoesNotExist:
        return redirect('content_list')

    site_config = _get_site_config()
    ctx = _SiteContext(request.user, site_config)

    try:
        rendered_body = page.body.format(ctx)
    except (KeyError, IndexError, ValueError, AttributeError):
        rendered_body = page.body

    return render(request, 'accounts/content_preview.html', {
        'page': page,
        'rendered_body': rendered_body,
    })


@login_required
def content_delete_view(request, page_id):
    try:
        page = ContentPage.objects.get(id=page_id, author=request.user)
    except ContentPage.DoesNotExist:
        return redirect('content_list')

    if request.method == 'POST':
        page.delete()
        return redirect('content_list')
    return render(request, 'accounts/content_delete.html', {'page': page})


def gallery_view(request):
    gallery_items = [
        {'name': 'DSC02674_11', 'description': 'Computer Abstract Art Image', 'image': 'r1.jpg', 'price': '8.5'},
        {'name': 'Urban street-art', 'description': 'graffiti on a wooden construction-wall on Plantage Muidergracht', 'image': 'r2.jpg', 'price': '5.6'},
        {'name': 'Abstract-9974', 'description': 'Abstract Art Image', 'image': 'r3.jpg', 'price': '6.5'},
        {'name': 'Art 235', 'description': 'Composite Image', 'image': 'r4.jpg', 'price': '4.8'},
        {'name': 'Radiographic Image', 'description': 'African Songye Power Figure in the collection of the Indianapolis Museum of Art', 'image': 'r5.jpg', 'price': '11.3'},
        {'name': 'Abstract00BO', 'description': 'BTerryCompton Abstract Art Image', 'image': 'r6.jpg', 'price': '8.4'},
        {'name': 'Aliens laughing', 'description': 'Young gray aliens reading books, laughing', 'image': 'r7.jpg', 'price': '6.5'},
        {'name': 'Flower #56', 'description': '134 flowers Sea Lavender Art', 'image': 'r8.jpg', 'price': '9.0'},
        {'name': 'White Wolves', 'description': 'CPM Art Challenge Photo White Wolves, 2013', 'image': 'r9.jpg', 'price': '7.3'},
    ]
    published_pages = ContentPage.objects.filter(is_published=True).order_by('-updated_at')[:5]
    return render(request, 'accounts/gallery.html', {
        'gallery_items': gallery_items,
        'published_pages': published_pages,
    })


def logout_view(request):
    logout(request)
    return redirect('/')
