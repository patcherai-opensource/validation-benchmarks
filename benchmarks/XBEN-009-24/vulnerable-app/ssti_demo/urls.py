from django.contrib import admin
from django.urls import path
from .views import index, view_document, list_documents, about

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('docs/<str:doc_id>/', view_document, name='view_document'),
    path('api/documents/', list_documents, name='list_documents'),
    path('about/', about, name='about'),
]
