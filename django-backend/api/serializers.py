from rest_framework import serializers
from .models import Triprel, Budget, People, PersonPhoto, Memories

class TriprelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Triprel
        fields = ['trip_id', 'trip_name', 'date_created']
        
class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['budget_id', 'trip_id', 'label', 'expense', 'category', 'location', 'date']
        
class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = ['person_id', 'trip_id', 'name', 'contact', 'met_location', 'met_date']
        
class PersonPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonPhoto
        fields = ['photo_id', 'trip_id', 'person_id', 'photo']
        
class MemoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memories
        fields = ['memory_id', 'trip_id', 'memory_photo', 'caption', 'location', 'date']

