from django.http import HttpResponse
from django.shortcuts import render


class SystemConfig:
    """Internal system configuration (not exposed to templates)"""
    def __init__(self):
        try:
            self._secret = open('/flag.txt').read().strip()
        except:
            self._secret = "FLAG{placeholder}"
    
    def get_secret_token(self):
        return self._secret


class Product:
    config = SystemConfig()
    
    def __init__(self, name, category, price, stock):
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"Product({self.name})"
    
    def get_config(self):
        """Internal method for system operations"""
        return self.config


def get_products():
    products = [
        Product("Laptop Pro 15", "Electronics", 1299.99, 45),
        Product("Wireless Mouse", "Electronics", 29.99, 200),
        Product("Office Chair", "Furniture", 249.99, 30),
        Product("Standing Desk", "Furniture", 599.99, 15),
        Product("Notebook Set", "Office Supplies", 12.99, 500),
        Product("Premium Headphones", "Electronics", 199.99, 75),
        Product("Monitor 27\"", "Electronics", 399.99, 60),
        Product("Keyboard Mechanical", "Electronics", 149.99, 120),
    ]
    return products


def index(request):
    return render(request, 'index.html')


def inventory(request):
    products = get_products()
    sort_by = request.GET.get('sort_by', 'name')
    
    context = {
        'products': products,
        'sort_by': sort_by,
        'current_sort': sort_by,
    }
    return render(request, 'inventory.html', context)


def report(request):
    products = get_products()
    sort_by = request.GET.get('sort_by', 'name')
    show_sort_key = request.GET.get('show_sort_key', 'false').lower() == 'true'
    
    context = {
        'products': products,
        'sort_by': sort_by,
        'show_sort_key': show_sort_key,
    }
    return render(request, 'report.html', context)


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
