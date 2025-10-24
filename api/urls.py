# api/urls.py
from django.urls import path
from .views import StringViewSet, natural_language_filter_view

urlpatterns = [
    # Standard CRUD endpoints
    path('strings', StringViewSet.as_view({'post': 'create', 'get': 'list'}), name='string-list-create'),
    # Note: We use <path:value> to handle strings that might contain slashes.
    path('strings/<path:value>', StringViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='string-detail'),
    
    # Natural Language endpoint
    path('strings/filter-by-natural-language', natural_language_filter_view, name='string-natural-filter'),
]



