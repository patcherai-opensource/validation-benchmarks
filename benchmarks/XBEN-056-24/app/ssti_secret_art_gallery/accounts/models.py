from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class Account(AbstractUser):
    is_premium = models.BooleanField(default=False)
    name = models.CharField(unique=True, max_length=40)

    def __str__(self):
        return self.username


class ContentPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    body = models.TextField(
        help_text=(
            "Page content. Use {context.title}, {context.author}, "
            "{context.site_name}, or {context.year} to insert dynamic values."
        )
    )
    author = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='pages'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'page'
            slug = base_slug
            counter = 1
            while ContentPage.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
