from django.db import models
from django.conf import settings


class Queue(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    allow_public_submission = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    OPEN_STATUS = 1
    REOPENED_STATUS = 2
    RESOLVED_STATUS = 3
    CLOSED_STATUS = 4
    DUPLICATE_STATUS = 5

    STATUS_CHOICES = (
        (OPEN_STATUS, 'Open'),
        (REOPENED_STATUS, 'Reopened'),
        (RESOLVED_STATUS, 'Resolved'),
        (CLOSED_STATUS, 'Closed'),
        (DUPLICATE_STATUS, 'Duplicate'),
    )

    PRIORITY_CHOICES = (
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Normal'),
        (4, 'Low'),
        (5, 'Very Low'),
    )

    title = models.CharField(max_length=200)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='tickets')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    submitter_email = models.EmailField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tickets',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=OPEN_STATUS)
    description = models.TextField(blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    resolution = models.TextField(blank=True, null=True)

    def __str__(self):
        return '[%s-%d] %s' % (self.queue.slug, self.id, self.title)

    def get_status_display_short(self):
        for s in self.STATUS_CHOICES:
            if s[0] == self.status:
                return s[1]
        return 'Unknown'

    class Meta:
        ordering = ['-created']


class FollowUp(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='followups')
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    public = models.BooleanField(default=True)

    def __str__(self):
        return '%s' % self.title

    class Meta:
        ordering = ['date']


class SavedSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_searches',
    )
    title = models.CharField(max_length=100)
    query = models.TextField()
    shared = models.BooleanField(default=False)

    def __str__(self):
        return '%s (by %s)' % (self.title, self.user)