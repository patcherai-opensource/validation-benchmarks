from django.core.management.base import BaseCommand
from helpdesk.models import Queue, Ticket, FollowUp
from accounts.models import Account


class Command(BaseCommand):
    help = 'Seed the helpdesk with initial data'

    def handle(self, *args, **options):
        # Create admin user if not exists
        if not Account.objects.filter(username='admin@helpdesk.local').exists():
            admin = Account.objects.create_user(
                username='admin@helpdesk.local',
                email='admin@helpdesk.local',
                password='HdAdmin2024!Secure',
                name='Admin',
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            admin = Account.objects.get(username='admin@helpdesk.local')

        # Create staff user
        if not Account.objects.filter(username='staff@helpdesk.local').exists():
            staff = Account.objects.create_user(
                username='staff@helpdesk.local',
                email='staff@helpdesk.local',
                password='StaffPass2024!',
                name='Support Staff',
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS('Created staff user'))
        else:
            staff = Account.objects.get(username='staff@helpdesk.local')

        # Create queues
        q_general, _ = Queue.objects.get_or_create(
            slug='general',
            defaults={'title': 'General Support', 'allow_public_submission': True}
        )
        q_billing, _ = Queue.objects.get_or_create(
            slug='billing',
            defaults={'title': 'Billing & Payments', 'allow_public_submission': True}
        )
        q_technical, _ = Queue.objects.get_or_create(
            slug='technical',
            defaults={'title': 'Technical Issues', 'allow_public_submission': True}
        )
        q_art, _ = Queue.objects.get_or_create(
            slug='art-submissions',
            defaults={'title': 'Art Submissions', 'allow_public_submission': False}
        )

        self.stdout.write(self.style.SUCCESS('Created queues'))

        # Create sample tickets
        sample_tickets = [
            {
                'title': 'Cannot access premium content',
                'description': 'I signed up for premium but cannot view premium art pieces. Please help.',
                'queue': q_general,
                'priority': 2,
                'submitter_email': 'user1@example.com',
                'status': Ticket.OPEN_STATUS,
            },
            {
                'title': 'Payment processing error',
                'description': 'Getting error 500 when trying to purchase art piece #45. Transaction ID: TXN-2024-001.',
                'queue': q_billing,
                'priority': 1,
                'submitter_email': 'buyer@artcollector.com',
                'status': Ticket.OPEN_STATUS,
                'assigned_to': staff,
            },
            {
                'title': 'Gallery images not loading on mobile',
                'description': 'Using Chrome on Android, gallery images show broken thumbnails. Works fine on desktop.',
                'queue': q_technical,
                'priority': 3,
                'submitter_email': 'mobilefan@gmail.com',
                'status': Ticket.REOPENED_STATUS,
            },
            {
                'title': 'Request to update artist profile',
                'description': 'I need to update my artist bio and profile picture. My artist ID is ART-2024-0087.',
                'queue': q_general,
                'priority': 4,
                'submitter_email': 'artist@portfolio.net',
                'status': Ticket.RESOLVED_STATUS,
                'assigned_to': admin,
            },
            {
                'title': 'Refund request for duplicate charge',
                'description': 'I was charged twice for order #ORD-9921. Please process a refund for the duplicate.',
                'queue': q_billing,
                'priority': 2,
                'submitter_email': 'customer@example.org',
                'status': Ticket.OPEN_STATUS,
            },
            {
                'title': 'Search functionality returns no results',
                'description': 'The search bar on the main gallery page always returns empty results, even for art pieces I can see listed.',
                'queue': q_technical,
                'priority': 3,
                'submitter_email': 'tester@qa.com',
                'status': Ticket.CLOSED_STATUS,
                'assigned_to': staff,
            },
        ]

        for ticket_data in sample_tickets:
            assigned = ticket_data.pop('assigned_to', None)
            if not Ticket.objects.filter(title=ticket_data['title']).exists():
                t = Ticket.objects.create(assigned_to=assigned, **ticket_data)
                FollowUp.objects.create(
                    ticket=t,
                    title='Ticket Created',
                    comment='Ticket was submitted via the support portal.',
                    user=admin if assigned else None,
                    public=True,
                )

        self.stdout.write(self.style.SUCCESS('Seeded helpdesk data successfully'))