from django.shortcuts import render, redirect
from .forms import Step1Form, Step2Form, Step3Form, LoginForm
from .models import Account
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.conf import settings


class ConfigHolder:
    """Configuration object that holds application settings"""
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.debug = settings.DEBUG
        self.app_name = "Art Gallery"
        self.version = "1.0.0"

app_config = ConfigHolder()


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
                a = Account(name=request.session['name'], 
                        username=request.session['email'], 
                        email=request.session['email'], 
                        is_premium=is_premium)
                a.set_password(request.session['password'])
                a.save()
                return render(request, 'accounts/registration_complete.html')
        else:
            form = Step3Form()
        
        return render(request, 'accounts/register_step3.html', {
            'form': form, 
            'account_name': request.session['name']
        })
    except: 
        return redirect('register_step1')


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


class ArtItem:
    """Represents an art gallery item"""
    def __init__(self, name, description, image, price, config=None):
        self.name = name
        self.description = description
        self.image = image
        self.price = price
        self.config = config


def gallery_view(request):
    sort_by = request.GET.get('sort', 'name')
    field = request.GET.get('field', '')
    
    gallery_items = [
        ArtItem('DSC02674_11', 'Computer Abstract Art Image', 'r1.jpg', '8.5', app_config),
        ArtItem('Urban street-art', 'Graffiti on a wooden construction-wall', 'r2.jpg', '5.6', app_config),
        ArtItem('Abstract-9974', 'Abstract Art Image', 'r3.jpg', '6.5', app_config),
        ArtItem('Art 235', 'Composite Image', 'r4.jpg', '4.8', app_config),
        ArtItem('Radiographic Image', 'African Songye Power Figure', 'r5.jpg', '11.3', app_config),
        ArtItem('Abstract00BO', 'BTerryCompton Abstract Art Image', 'r6.jpg', '8.4', app_config),
        ArtItem('Aliens laughing', 'Young gray aliens reading books', 'r7.jpg', '6.5', app_config),
        ArtItem('Flower #56', '134 flowers Sea Lavender Art', 'r8.jpg', '9.0', app_config),
        ArtItem('White Wolves', 'CPM Art Challenge Photo White Wolves', 'r9.jpg', '7.3', app_config),
    ]
    
    return render(request, 'accounts/gallery.html', {
        'gallery_items': gallery_items,
        'sort_by': sort_by,
        'current_sort': sort_by,
        'field': field
    })

def logout_view(request):
    logout(request)
    return redirect('/')
