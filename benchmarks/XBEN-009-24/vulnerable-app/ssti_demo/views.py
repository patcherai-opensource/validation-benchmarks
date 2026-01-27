from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import os
import copy

# Simulated contact database (would be in a real DB in production)
# This represents the Dolibarr contact database that gets exposed
CONTACTS_DB = [
    {"id": 1, "name": "John Smith", "email": "john.smith@acme.local", "phone": "+1-555-0101", "company": "ACME Corp", "type": "customer"},
    {"id": 2, "name": "Jane Doe", "email": "jane.doe@widgets.local", "phone": "+1-555-0102", "company": "Widgets Inc", "type": "customer"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@suppliers.local", "phone": "+1-555-0103", "company": "Suppliers Ltd", "type": "supplier"},
    {"id": 4, "name": "Alice Brown", "email": "alice.brown@techcorp.local", "phone": "+1-555-0104", "company": "TechCorp", "type": "customer"},
    {"id": 5, "name": "Charlie Wilson", "email": "charlie@internal.local", "phone": "+1-555-0105", "company": "Internal", "type": "employee"},
    {"id": 6, "name": "Diana Miller", "email": "diana@partners.local", "phone": "+1-555-0106", "company": "Partners Inc", "type": "supplier"},
    {"id": 7, "name": "Edward Davis", "email": "edward@clients.local", "phone": "+1-555-0107", "company": "Clients LLC", "type": "customer"},
    {"id": 8, "name": "Fiona Garcia", "email": "fiona@vendors.local", "phone": "+1-555-0108", "company": "Vendors Co", "type": "supplier"},
    {"id": 9, "name": "System Administrator", "email": "admin@system.local", "phone": "+1-555-0000", "company": "Internal", "type": "employee", "notes": ""},  # Flag will be added here
    {"id": 10, "name": "Henry Martinez", "email": "henry@services.local", "phone": "+1-555-0110", "company": "Services Corp", "type": "customer"},
]

# Initialize the flag in the admin contact notes
def get_contacts_with_flag():
    contacts = copy.deepcopy(CONTACTS_DB)
    flag = ""
    try:
        flag = open('/flag.txt').read().strip()
    except:
        flag = os.environ.get('FLAG', 'FLAG{placeholder}')
    
    # Add flag to admin contact notes
    for contact in contacts:
        if contact.get("id") == 9:
            contact["notes"] = f"CONFIDENTIAL: System access token: {flag}"
    return contacts

def index(request):
    return render(request, 'index.html')

def ticket_create(request):
    """Public ticket creation page - legitimate public endpoint"""
    return render(request, 'ticket_create.html')

@csrf_exempt
def public_ticket_ajax(request):
    """
    VULNERABLE ENDPOINT - CVE-2023-33568 style broken authorization
    
    This endpoint mimics Dolibarr's /public/ticket/ajax/ajax.php
    When TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST is enabled (simulated as always on),
    the getContacts action allows unauthenticated database dumping.
    
    No authentication check is performed - this is the vulnerability!
    """
    action = request.GET.get('action', '') or request.POST.get('action', '')
    email = request.GET.get('email', '') or request.POST.get('email', '')
    
    if action == 'getContacts':
        # VULNERABILITY: No authentication check!
        # In a fixed version, this would call accessforbidden() for unauthenticated requests
        
        contacts = get_contacts_with_flag()
        
        # Search contacts by email pattern (% acts as wildcard like in SQL)
        if email:
            if email == '%' or email == '*':
                # Wildcard - return all contacts (the exploitation vector)
                matching = contacts
            else:
                # Partial match search
                search_term = email.lower().replace('%', '')
                matching = [c for c in contacts if search_term in c.get('email', '').lower() or 
                           search_term in c.get('name', '').lower() or
                           search_term in c.get('company', '').lower()]
        else:
            matching = []
        
        return JsonResponse({
            'success': True,
            'data': matching,
            'count': len(matching)
        })
    
    elif action == 'createTicket':
        # Legitimate ticket creation (not vulnerable)
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        email = request.POST.get('email', '')
        
        if not subject or not message or not email:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        return JsonResponse({
            'success': True,
            'message': 'Ticket created successfully',
            'ticket_id': 'TKT-2024-001'
        })
    
    else:
        return JsonResponse({
            'success': False,
            'error': 'Invalid action parameter'
        })

def admin_login(request):
    """Admin login page - requires authentication (not vulnerable)"""
    if request.method == 'POST':
        # Hardcoded admin check - not the vulnerability
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        # This is secure - brute force protection would exist in production
        return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    
    return render(request, 'admin_login.html')

def api_docs(request):
    """API documentation page - hints at available endpoints"""
    return render(request, 'api_docs.html')
