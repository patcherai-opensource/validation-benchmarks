from django.shortcuts import render, redirect
from .forms import Step1Form, Step2Form, Step3Form, LoginForm
from .models import Account
from django.http import HttpResponse
from django.template import engines, Variable
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from os import getenv

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
                # Save data or create a user here
                a=Account(name=request.session['name'], 
                        username=request.session['email'], 
                        email=request.session['email'], 
                        is_premium=is_premium)
                a.set_password(request.session['password'])
                a.save()
                return render(request, 'accounts/registration_complete.html')
        else:
            form = Step3Form()
    except: 
        return redirect('register_step1')    
    return render(request, 'accounts/register_step3.html', {'form': form})


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


class SecretHolder:
    """A helper class to hold configuration including the secret flag"""
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def __repr__(self):
        return f"SecretHolder(secret_key={self.secret_key})"
    
    def __str__(self):
        return f"Config[secret_key={self.secret_key}]"


class GalleryItem:
    """
    A gallery item that stores art information along with configuration.
    This class is used to simulate a real-world scenario where objects
    might have references to sensitive configuration/settings.
    """
    def __init__(self, name, description, image, price, config):
        self.name = name
        self.description = description
        self.image = image
        self.price = price
        self.config = config  # Reference to configuration containing secrets
    
    def __getitem__(self, key):
        """Allow dictionary-style access for template compatibility"""
        return getattr(self, key, None)
    
    def __repr__(self):
        return f"GalleryItem(name={self.name})"


def gallery_view(request):
    """
    Gallery view with sorting capability.
    Users can specify a sort field via the 'sort' query parameter.
    The dictsort filter is used in the template with the user-provided sort key.
    
    CVE-2021-45116: The dictsort filter's variable resolution allows accessing
    arbitrary attributes through the sort key argument, enabling information disclosure.
    
    When a user specifies sort=config.secret_key, Django's Variable resolution
    will traverse the attribute path and access the secret_key, which then becomes
    the sort key. The resolved values are displayed in the debug output.
    """
    # Get the sort parameter from the query string (defaults to 'name')
    sort_by = request.GET.get('sort', 'name')
    
    # Create a secret holder object with the flag
    secret_holder = SecretHolder(settings.SECRET_KEY)
    
    # Create a list of gallery items with the secret holder embedded
    # Each item has a reference to the configuration/secrets for "metadata" purposes
    gallery_items = [
        GalleryItem('DSC02674_11', 'Computer Abstract Art Image', 'r1.jpg', '8.5', secret_holder),
        GalleryItem('Urban street-art', 'graffiti on a wooden construction-wall', 'r2.jpg', '5.6', secret_holder),
        GalleryItem('Abstract-9974', 'Abstract Art Image', 'r3.jpg', '6.5', secret_holder),
        GalleryItem('Art 235', 'Composite Image', 'r4.jpg', '4.8', secret_holder),
        GalleryItem('Radiographic Image', 'African Songye Power Figure', 'r5.jpg', '11.3', secret_holder),
        GalleryItem('Abstract00BO', 'BTerryCompton Abstract Art Image', 'r6.jpg', '8.4', secret_holder),
        GalleryItem('Aliens laughing', 'Young gray aliens reading books', 'r7.jpg', '6.5', secret_holder),
        GalleryItem('Flower #56', '134 flowers Sea Lavender Art', 'r8.jpg', '9.0', secret_holder),
        GalleryItem('White Wolves', 'CPM Art Challenge Photo', 'r9.jpg', '7.3', secret_holder),
    ]
    
    # Resolve the sort_by value for debug display
    # This uses Django's Variable resolution - the EXACT same mechanism used by dictsort
    # In Django's dictsort filter (django/template/defaultfilters.py):
    #   def _property_resolver(arg):
    #       ...
    #       return Variable(arg).resolve
    # 
    # CVE-2021-45116: The Variable class resolves arbitrary attribute paths,
    # allowing access to sensitive attributes like config.secret_key
    resolved_sort_value = None
    try:
        if gallery_items:
            # Use Django's Variable class to resolve the sort key against the first item
            # This is EXACTLY what dictsort does internally via _property_resolver
            from django.template import Context
            ctx = Context({'item': gallery_items[0]})
            var = Variable('item.' + sort_by)
            resolved_sort_value = var.resolve(ctx)
    except Exception as e:
        resolved_sort_value = f"(unable to resolve: {type(e).__name__})"
    
    # Pass the sort parameter to the template where dictsort filter will be used
    return render(request, 'accounts/gallery.html', {
        'gallery_items': gallery_items,
        'sort_by': sort_by,
        'debug_sort_value': resolved_sort_value
    })

def logout_view(request):
    logout(request)
    return redirect('/')
