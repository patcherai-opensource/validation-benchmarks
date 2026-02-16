from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    is_premium = models.BooleanField(default=False)
    name = models.CharField(unique=True, max_length=40)

    def __str__(self):
        return self.username


class ContentPage(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=200)
    body = models.TextField(
        help_text='Use {0.title} for site title, {0.author} for your name, '
                  '{0.year} for current year, {0.contact} for contact email.'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title
