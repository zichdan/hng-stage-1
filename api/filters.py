# api/filters.py
import django_filters
from .models import AnalyzedString

class AnalyzedStringFilter(django_filters.FilterSet):
    # Simple filters are automatically generated for these fields
    is_palindrome = django_filters.BooleanFilter()
    word_count = django_filters.NumberFilter()

    # Custom filters for more complex logic
    min_length = django_filters.NumberFilter(field_name="length", lookup_expr='gte')
    max_length = django_filters.NumberFilter(field_name="length", lookup_expr='lte')
    contains_character = django_filters.CharFilter(method='filter_contains_character')

    class Meta:
        model = AnalyzedString
        fields = ['is_palindrome', 'word_count']

    def filter_contains_character(self, queryset, name, value):
        """Custom filter method to check for character containment (case-insensitive)."""
        return queryset.filter(value__icontains=value)