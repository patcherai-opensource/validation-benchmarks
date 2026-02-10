from django.http import HttpResponse
from django.shortcuts import render
from django.template import engines, Variable, Context


def sort_items(request):
    """
    An endpoint that allows sorting items by a user-specified field.
    
    CVE-2021-45116: The dictsort filter uses Variable.resolve() which allows
    accessing arbitrary dictionary keys including those starting with underscore.
    
    Before the fix in Django 3.2.10, the dictsort filter would resolve
    Variable(arg) where arg is the user-provided sort key. This allowed
    accessing any dictionary key or object attribute, including "private"
    ones prefixed with underscore.
    
    The vulnerability exists because:
    1. User controls the sort key argument to dictsort via GET parameter
    2. dictsort calls _property_resolver(arg) which wraps arg in Variable(arg)
    3. Variable.resolve() traverses dictionary keys and attributes without restriction
    4. This allows accessing internal/private data not intended for user access
    """
    # Load the flag
    try:
        flag = open('/flag.txt').read().strip()
    except:
        flag = "FLAG{test_flag}"
    
    # Get user-controlled sort field - this is the attack vector
    sort_by = request.GET.get('sort', 'priority')
    
    # The "show_value" parameter controls whether we show the sort key value
    show_value = request.GET.get('show_value', 'false').lower() == 'true'
    
    # Create items as dictionaries
    # In a real application, these might come from a database query that includes
    # internal metadata fields not meant to be exposed to users
    items = [
        {
            'id': 1,
            'name': 'Widget A',
            'priority': 3,
            'category': 'hardware',
            'price': 29.99,
            # Internal metadata - underscore prefix indicates "private" data
            '_internal_id': 'hw-001',
            '_admin_note': 'Regular stock item',
        },
        {
            'id': 2,
            'name': 'Widget B', 
            'priority': 1,
            'category': 'software',
            'price': 49.99,
            '_internal_id': 'sw-002',
            '_admin_note': 'On sale this week',
        },
        {
            'id': 3,
            'name': 'Widget C',
            'priority': 2,
            'category': 'hardware',
            'price': 19.99,
            '_internal_id': 'hw-003',
            # The flag is stored in a "private" admin note
            '_admin_note': flag,
        },
    ]
    
    # Build dynamic template that uses dictsort with user-provided key
    # This demonstrates CVE-2021-45116 where the sort key allows accessing private attributes
    engine = engines['django']
    
    if show_value:
        # When show_value is True, we resolve the sort key values for each item
        # and include them in a list that corresponds to the sorted order.
        # This demonstrates CVE-2021-45116 - using Variable.resolve() to access
        # private attributes via a user-controlled sort key.
        
        # Sort items using Variable resolution (same as dictsort does internally)
        def resolve_key(item):
            try:
                ctx = Context({'item': item})
                return Variable('item.' + sort_by).resolve(ctx)
            except:
                return ''
        
        try:
            sorted_items = sorted(items, key=resolve_key)
        except:
            sorted_items = items
        
        # Build the sorted items with their resolved sort values
        items_with_values = []
        for item in sorted_items:
            try:
                ctx = Context({'item': item})
                sort_value = str(Variable('item.' + sort_by).resolve(ctx))
            except:
                sort_value = '-'
            items_with_values.append({
                **item,
                '_resolved_sort_value': sort_value
            })
        
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Item Sorter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #2196F3; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        form { margin: 20px 0; }
        input[type="text"] { padding: 10px; width: 250px; }
        button { padding: 10px 20px; background-color: #2196F3; color: white; border: none; }
        .info { background-color: #e7f3fe; padding: 15px; margin: 20px 0; border-radius: 4px; }
        code { background: #f5f5f5; padding: 2px 6px; }
    </style>
</head>
<body>
<div class="container">
    <h1>📦 Inventory Item Sorter</h1>
    <div class="info">
        <p>Sort fields: <code>name</code>, <code>priority</code>, <code>category</code>, <code>id</code>, <code>price</code></p>
    </div>
    <form action="/sort/" method="get">
        <input type="text" name="sort" value="{{ sort_by }}" placeholder="Field name...">
        <label><input type="checkbox" name="show_value" value="true" checked> Show values</label>
        <button type="submit">Sort</button>
    </form>
    <h2>Items (sorted by: {{ sort_by }})</h2>
    <table>
        <tr><th>#</th><th>ID</th><th>Name</th><th>Category</th><th>Priority</th><th>Price</th><th>Sort Key Value</th></tr>
        {% for item in items %}
        <tr>
            <td>{{ forloop.counter }}</td>
            <td>{{ item.id }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.category }}</td>
            <td>{{ item.priority }}</td>
            <td>${{ item.price }}</td>
            <td>{{ item._resolved_sort_value }}</td>
        </tr>
        {% endfor %}
    </table>
</div>
</body>
</html>
'''
        template = engine.from_string(template_str)
        return HttpResponse(template.render({
            'items': items_with_values, 
            'sort_by': sort_by,
        }, request))
    else:
        context = {
            'items': items,
            'sort_by': sort_by,
            'show_value': show_value,
        }
        return render(request, 'sort_items.html', context)


def index(request):
    return render(request, 'index.html')
