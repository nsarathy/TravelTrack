from django.db import models

# Create your models here.

class Triprel(models.Model):
    trip_id = models.AutoField(primary_key=True)
    trip_name = models.CharField(max_length=255, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.trip_name

class Budget(models.Model):
    budget_id = models.AutoField(primary_key=True)  # Unique ID for each expense
    trip = models.ForeignKey(Triprel, on_delete=models.CASCADE)  # Links to a trip
    label = models.CharField(max_length=255)  # Expense description (e.g., "Lunch")
    expense = models.DecimalField(max_digits=10, decimal_places=2)  # Expense amount
    category = models.CharField(max_length=100)  # Category (e.g., "Food and Drink")
    location = models.CharField(max_length=255)  # Where the expense occurred
    date = models.DateField()  # Date of the expense
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date'], name='expense_date_idx'),
            models.Index(fields=['trip', 'location', 'category'], name='expense_clt_idx'),
        ]

    def __str__(self):
        return f"{self.label} - {self.expense}"
    
class People(models.Model):
    person_id = models.AutoField(primary_key=True) # Unique ID for each person
    trip = models.ForeignKey(Triprel, on_delete=models.CASCADE) # Links to a trip
    name = models.CharField(max_length=255) # Name of the person
    contact = models.CharField(max_length=255) # Contact of the person
    met_location = models.CharField(max_length=255) # Where the person was met
    met_date = models.DateField() # Date the person was met
    
    class Meta:
        ordering = ['-met_date']
        indexes = [
            models.Index(fields=['-met_date'], name='people_met_date_idx'),
            models.Index(fields=['trip', 'met_location'], name='people_tl_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.contact}"
    
class PersonPhoto(models.Model):
    photo_id = models.AutoField(primary_key=True)  # Unique ID for each photo
    trip = models.ForeignKey(Triprel, on_delete=models.CASCADE)  # Link to a trip
    person = models.ForeignKey(People, on_delete=models.CASCADE)  # Link to a person
    photo = models.ImageField(upload_to='images/')  # Photo of the person

    def __str__(self):
        return f"{self.person.name} - photo from {self.trip.trip_name}"

class Memories(models.Model):
    memory_id = models.AutoField(primary_key=True)  # Unique memory ID
    trip = models.ForeignKey(Triprel, on_delete=models.CASCADE)  # Links to a trip
    memory_photo = models.ImageField(upload_to='memories/')  # Photo of the memory
    caption = models.TextField()  # Caption for the memory
    location = models.CharField(max_length=255)  # Location of the memory
    date = models.CharField(max_length=255)  # Store date as a text field (YYYY-MM-DD or any format)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date'], name='memory_date_idx'),
            models.Index(fields=['trip', 'location'], name='memory_tl_idx'),
        ]

    def __str__(self):
        return f"Memory {self.memory_id} - {self.trip.trip_name} ({self.location})"


