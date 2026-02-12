from django.contrib import admin
from .models import Ticket, Queue, FollowUp, SavedSearch

admin.site.register(Queue)
admin.site.register(Ticket)
admin.site.register(FollowUp)
admin.site.register(SavedSearch)