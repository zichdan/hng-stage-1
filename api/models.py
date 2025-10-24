# api/models.py
from django.db import models
import uuid

class AnalyzedString(models.Model):
    # The SHA256 hash is the unique ID for each analyzed string.
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    
    # We store the original value, ensuring it's unique to prevent duplicates (409 Conflict).
    value = models.TextField(unique=True)
    
    # --- Stored Properties ---
    length = models.PositiveIntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.PositiveIntegerField()
    word_count = models.PositiveIntegerField()
    
    # JSONField is perfect for storing the character frequency map.
    character_frequency_map = models.JSONField()
    
    # Timestamp for when the string was first analyzed.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.value