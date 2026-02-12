import threading
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import Ticket, Queue, FollowUp

logger = logging.getLogger(__name__)


@login_required
def ticket_list(request):
    queues = Queue.objects.all()
    saved_searches = request.user.saved_searches.all() if request.user.is_authenticated else []
    return render(request, 'helpdesk/ticket_list.html', {
        'queues': queues,
        'saved_searches': saved_searches,
        'user': request.user,
    })


@login_required
def datatables_ticket_list(request):
    """Return ticket data in JSON format for DataTables AJAX requests."""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 25))
    search_value = request.GET.get('search[value]', '')

    tickets = Ticket.objects.all()

    # Filter by search
    if search_value:
        tickets = tickets.filter(
            Q(title__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(submitter_email__icontains=search_value)
        )

    # Filter by queue if specified
    queue_id = request.GET.get('queue', '')
    if queue_id:
        tickets = tickets.filter(queue_id=queue_id)

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        tickets = tickets.filter(status=status)

    total = Ticket.objects.count()
    filtered = tickets.count()

    # Ordering
    order_col = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    order_fields = ['id', 'title', 'status', 'priority', 'queue__title', 'created', 'assigned_to__name']

    if order_col < len(order_fields):
        order_field = order_fields[order_col]
        if order_dir == 'desc':
            order_field = '-' + order_field
        tickets = tickets.order_by(order_field)

    tickets = tickets[start:start + length]

    data = []
    for ticket in tickets:
        data.append({
            'id': ticket.id,
            'title': ticket.title,
            'status': ticket.get_status_display_short(),
            'priority': ticket.get_priority_display(),
            'queue': ticket.queue.title if ticket.queue else '',
            'created': ticket.created.strftime('%Y-%m-%d %H:%M') if ticket.created else '',
            'assigned_to': ticket.assigned_to.name if ticket.assigned_to else 'Unassigned',
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered,
        'data': data,
    })


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    followups = ticket.followups.all()
    return render(request, 'helpdesk/ticket_detail.html', {
        'ticket': ticket,
        'followups': followups,
    })


@login_required
def create_ticket(request):
    queues = Queue.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        queue_id = request.POST.get('queue', '')
        priority = request.POST.get('priority', 3)
        submitter_email = request.POST.get('submitter_email', '')

        if title and queue_id:
            try:
                queue = Queue.objects.get(pk=queue_id)
                ticket = Ticket.objects.create(
                    title=title,
                    description=description,
                    queue=queue,
                    priority=int(priority),
                    submitter_email=submitter_email or request.user.email,
                    assigned_to=None,
                    status=Ticket.OPEN_STATUS,
                )
                FollowUp.objects.create(
                    ticket=ticket,
                    title='Ticket Created',
                    comment='Ticket was created.',
                    user=request.user,
                    public=True,
                )
                return redirect('helpdesk_ticket_detail', ticket_id=ticket.id)
            except Queue.DoesNotExist:
                pass

    return render(request, 'helpdesk/create_ticket.html', {
        'queues': queues,
        'priorities': Ticket.PRIORITY_CHOICES,
    })


@csrf_exempt
def public_create_ticket(request):
    """Allow anonymous users to create tickets on public queues."""
    queues = Queue.objects.filter(allow_public_submission=True)
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        queue_id = request.POST.get('queue', '')
        priority = request.POST.get('priority', 3)
        submitter_email = request.POST.get('submitter_email', '')

        if title and queue_id:
            try:
                queue = Queue.objects.get(pk=queue_id, allow_public_submission=True)
                ticket = Ticket.objects.create(
                    title=title,
                    description=description,
                    queue=queue,
                    priority=int(priority),
                    submitter_email=submitter_email,
                    status=Ticket.OPEN_STATUS,
                )
                return render(request, 'helpdesk/public_ticket_created.html', {
                    'ticket': ticket,
                })
            except Queue.DoesNotExist:
                pass

    return render(request, 'helpdesk/public_create_ticket.html', {
        'queues': queues,
        'priorities': Ticket.PRIORITY_CHOICES,
    })


@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        new_status = request.POST.get('status', '')
        if comment:
            FollowUp.objects.create(
                ticket=ticket,
                title='Updated',
                comment=comment,
                user=request.user,
                public=True,
            )
        if new_status:
            ticket.status = int(new_status)
            ticket.save()
        return redirect('helpdesk_ticket_detail', ticket_id=ticket.id)
    return redirect('helpdesk_ticket_detail', ticket_id=ticket.id)


@login_required
def dashboard(request):
    open_tickets = Ticket.objects.filter(status__in=[Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS]).count()
    my_tickets = Ticket.objects.filter(assigned_to=request.user).count()
    unassigned = Ticket.objects.filter(assigned_to__isnull=True, status=Ticket.OPEN_STATUS).count()
    queues = Queue.objects.all()

    queue_stats = []
    for q in queues:
        queue_stats.append({
            'queue': q,
            'open': q.tickets.filter(status__in=[Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS]).count(),
            'resolved': q.tickets.filter(status=Ticket.RESOLVED_STATUS).count(),
        })

    return render(request, 'helpdesk/dashboard.html', {
        'open_tickets': open_tickets,
        'my_tickets': my_tickets,
        'unassigned': unassigned,
        'queue_stats': queue_stats,
    })


@csrf_exempt
def report_ticket(request):
    """Trigger admin review of a specific ticket via the ticket list page.
    This is used when users want to escalate a ticket for admin attention."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    ticket_id = request.POST.get('ticket_id', '')
    if not ticket_id:
        return JsonResponse({'error': 'ticket_id is required'}, status=400)

    try:
        ticket = Ticket.objects.get(pk=int(ticket_id))
    except (Ticket.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Ticket not found'}, status=404)

    # Trigger admin bot to review the ticket list
    t = threading.Thread(target=_admin_review_tickets, daemon=True)
    t.start()

    return JsonResponse({'status': 'ok', 'message': 'Ticket has been flagged for admin review.'})


_webhook_store = []


@csrf_exempt
def webhook_log(request):
    """Internal webhook endpoint for automated notifications and integrations."""
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8', errors='replace')
            _webhook_store.append(body[:2000])
            if len(_webhook_store) > 50:
                _webhook_store.pop(0)
            logger.info("Webhook received: %s", body[:500])
        except Exception:
            pass
        return JsonResponse({'status': 'received'})
    elif request.method == 'GET':
        data = request.GET.get('data', '')
        if data:
            _webhook_store.append(data[:2000])
            if len(_webhook_store) > 50:
                _webhook_store.pop(0)
            logger.info("Webhook GET: %s", data[:500])
            return JsonResponse({'status': 'received'})
        else:
            return JsonResponse({'entries': list(_webhook_store)})
    return HttpResponseNotAllowed(['GET', 'POST'])


def _admin_review_tickets():
    """Simulate an admin staff member reviewing the ticket list page."""
    import time
    time.sleep(2)
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        admin_secret = ''
        try:
            with open('/flag.txt', 'r') as f:
                admin_secret = f.read().strip()
        except Exception:
            admin_secret = 'no-token-found'

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--window-size=1280,1024')
        chrome_options.binary_location = '/usr/bin/chromium'

        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(15)

        try:
            # Navigate to login page and authenticate as admin
            driver.get('http://127.0.0.1:80/accounts/login/')
            time.sleep(1)

            # Set admin authentication token cookie
            driver.add_cookie({
                'name': 'admin_token',
                'value': admin_secret,
                'path': '/',
                'domain': '127.0.0.1',
            })

            # Log in as the admin user
            username_field = driver.find_element('name', 'username')
            password_field = driver.find_element('name', 'password')
            username_field.send_keys('admin@helpdesk.local')
            password_field.send_keys('HdAdmin2024!Secure')
            password_field.submit()
            time.sleep(2)

            # Visit the ticket list page (where XSS would fire)
            driver.get('http://127.0.0.1:80/helpdesk/tickets/')
            time.sleep(5)
        finally:
            driver.quit()
    except Exception as e:
        logger.error("Admin review failed: %s", str(e))
