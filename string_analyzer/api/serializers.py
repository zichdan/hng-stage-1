# api/serializers.py
from rest_framework import serializers
from .models import AnalyzedString

class StringInputSerializer(serializers.Serializer):
    """Serializer for validating the input on POST requests."""
    value = serializers.CharField(max_length=10000)

class AnalyzedStringSerializer(serializers.ModelSerializer):
    """
    Serializer for the main AnalyzedString model, formats the output
    to match the required nested structure.
    """
    properties = serializers.SerializerMethodField()

    class Meta:
        model = AnalyzedString
        # Note: 'id' is the sha256_hash in our model
        fields = ['id', 'value', 'properties', 'created_at']

    def get_properties(self, obj):
        """Nests the computed properties under a 'properties' key."""
        return {
            "length": obj.length,
            "is_palindrome": obj.is_palindrome,
            "unique_characters": obj.unique_characters,
            "word_count": obj.word_count,
            "sha256_hash": obj.id, # The ID is the hash
            "character_frequency_map": obj.character_frequency_map,
        }