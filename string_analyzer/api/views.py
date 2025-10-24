# api/views.py
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
import re

from .models import AnalyzedString
from .serializers import AnalyzedStringSerializer, StringInputSerializer
from .services import analyze_string_value
from .filters import AnalyzedStringFilter

class StringViewSet(viewsets.ViewSet):
    """
    A ViewSet for creating, retrieving, listing, and deleting analyzed strings.
    """
    # Use the raw string value as the lookup field for retrieve/delete
    lookup_field = 'value'


    # api/views.py -> inside the StringViewSet class

    def create(self, request):
        """POST /strings: Analyzes and stores a new string."""
        # 1. Check for missing 'value' field for a 400 Bad Request
        if 'value' not in request.data:
            return Response({"error": "Missing 'value' field"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Check for invalid data type for a 422 Unprocessable Entity
        if not isinstance(request.data['value'], str):
            return Response({"error": "Invalid data type for 'value', must be a string"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        serializer = StringInputSerializer(data=request.data)
        # This validation is now a final check
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        value = serializer.validated_data['value']
        
        try:
            properties = analyze_string_value(value)
            
            # Use get_or_create to handle duplicate check more cleanly
            instance, created = AnalyzedString.objects.get_or_create(
                value=value,
                defaults={
                    'id': properties['sha256_hash'],
                    'length': properties['length'],
                    'is_palindrome': properties['is_palindrome'],
                    'unique_characters': properties['unique_characters'],
                    'word_count': properties['word_count'],
                    'character_frequency_map': properties['character_frequency_map']
                }
            )

            # If the object was not created, it means it already existed.
            if not created:
                return Response({"error": "String already exists in the system"}, status=status.HTTP_409_CONFLICT)
            
            output_serializer = AnalyzedStringSerializer(instance)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # General catch-all for any other unexpected server errors
            return Response({"error": f"An internal server error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, value=None):
        """GET /strings/{string_value}: Retrieves a specific analyzed string."""
        instance = get_object_or_404(AnalyzedString, value=value)
        serializer = AnalyzedStringSerializer(instance)
        return Response(serializer.data)

    def destroy(self, request, value=None):
        """DELETE /strings/{string_value}: Deletes a specific analyzed string."""
        instance = get_object_or_404(AnalyzedString, value=value)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """GET /strings: Lists all strings with optional filtering."""
        queryset = AnalyzedString.objects.all()
        filterset = AnalyzedStringFilter(request.query_params, queryset=queryset)
        
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
            
        filtered_queryset = filterset.qs
        
        serializer = AnalyzedStringSerializer(filtered_queryset, many=True)
        
        # Construct the custom response format
        response_data = {
            "data": serializer.data,
            "count": filtered_queryset.count(),
            "filters_applied": {k: v for k, v in request.query_params.items() if k in filterset.get_fields()}
        }
        return Response(response_data)

# --- Natural Language Endpoint ---

@api_view(['GET'])
def natural_language_filter_view(request):
    """GET /strings/filter-by-natural-language: Filters strings based on a natural language query."""
    query = request.query_params.get('query', '').lower()
    if not query:
        return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Simple NLP parsing logic
    filters = {}
    if "palindromic" in query or "palindrome" in query:
        filters['is_palindrome'] = True
    if "single word" in query:
        filters['word_count'] = 1
    
    length_match = re.search(r'longer than (\d+)', query)
    if length_match:
        filters['min_length'] = int(length_match.group(1)) + 1
        
    contain_match = re.search(r'contain(?:ing|s) the letter ([a-z])', query)
    if contain_match:
        filters['contains_character'] = contain_match.group(1)
    
    # Heuristic for "first vowel"
    if "first vowel" in query:
         filters['contains_character'] = 'a'

    if not filters:
        return Response({"error": "Unable to parse natural language query."}, status=status.HTTP_400_BAD_REQUEST)

    # Apply parsed filters
    queryset = AnalyzedString.objects.all()
    filterset = AnalyzedStringFilter(filters, queryset=queryset)
    filtered_queryset = filterset.qs
    
    serializer = AnalyzedStringSerializer(filtered_queryset, many=True)

    response_data = {
        "data": serializer.data,
        "count": filtered_queryset.count(),
        "interpreted_query": {
            "original": query,
            "parsed_filters": filters
        }
    }
    return Response(response_data)




