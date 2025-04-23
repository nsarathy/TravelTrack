from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Triprel, Budget, People, PersonPhoto, Memories
from .serializers import TriprelSerializer, BudgetSerializer, PeopleSerializer, PersonPhotoSerializer, MemoriesSerializer
from rest_framework import status
from django.utils.dateparse import parse_date
import os
from django.conf import settings
from django.db import connection


@api_view(['GET'])
def get_trips(request):
    """Fetch all trips from the database."""
    trips = Triprel.objects.all().order_by('-date_created')
    serializer = TriprelSerializer(trips, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_trip(request):
    """Add a new trip to the database if the name is not empty."""
    trip_name = request.data.get('trip_name', '').strip()
    if not trip_name:
        return Response({'error': 'Trip name cannot be empty'}, status=400)

    trip, created = Triprel.objects.get_or_create(
        trip_name=trip_name, defaults={'date_created': now()})

    if not created:
        return Response({'error': 'Trip already exists'}, status=400)

    return Response({'message': 'Trip added successfully', 'trip_id': trip.trip_id})


@api_view(['GET'])
def get_trip_details(request, trip_id):
    """Fetch trip details if it exists"""
    trip = get_object_or_404(Triprel, trip_id=trip_id)
    serializer = TriprelSerializer(trip)
    return Response(serializer.data)

@api_view(['PUT'])
def edit_trip(request, trip_id):
    """Edit the trip name if it exists and the new name is valid"""
    trip = get_object_or_404(Triprel, trip_id=trip_id)

    # Extract new trip name
    new_trip_name = request.data.get('trip_name', '').strip()
    if not new_trip_name:
        return Response({'error': 'Trip name cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if another trip already has this name
    if Triprel.objects.exclude(trip_id=trip_id).filter(trip_name=new_trip_name).exists():
        return Response({'error': 'A trip with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    # Update trip name
    trip.trip_name = new_trip_name
    trip.save()

    return Response({'message': 'Trip updated successfully', 'trip_id': trip.trip_id})


@api_view(['DELETE'])
def delete_trip(request, trip_id):
    """Delete a trip and all related data"""
    trip = Triprel.objects.filter(trip_id=trip_id).first()
    if not trip:
        return Response({'error': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Delete the trip and all related records
    trip.delete()
    
    return Response({'message': 'Trip deleted successfully.'}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_budget_items(request, trip_id):
    """Check if Budget table exists and return budget items for a trip"""
    budget_items = Budget.objects.filter(trip_id=trip_id).order_by('-date')

    if not budget_items.exists():
        return Response({'message': 'No budget entries found for this trip.'}, status=404)

    serializer = BudgetSerializer(budget_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_budget_item(request, trip_id):
    """Add an expense to the Budget table, ensuring all fields are valid"""

    # Extract data from request
    label = request.data.get("label", "").strip()
    expense = request.data.get("expense", "")
    category = request.data.get("category", "").strip()
    location = request.data.get("location", "").strip()
    date_str = request.data.get("date", "").strip()

    # Validate all fields
    if not (label and expense and category and location and date_str):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        expense = float(expense)
        if expense <= 0:
            return Response({"error": "Expense must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"error": "Expense must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

    # Parse date
    try:
        date = parse_date(date_str)
        if not date:
            raise ValueError
    except ValueError:
        return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the trip exists
    trip = Triprel.objects.filter(trip_id=trip_id).first()
    if not trip:
        return Response({"error": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create and save budget item
    budget_item = Budget.objects.create(
        trip=trip,
        label=label,
        expense=expense,
        category=category,
        location=location,
        date=date
    )

    return Response({"message": "Expense added successfully", "budget_id": budget_item.budget_id}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_budget_item(request, trip_id, budget_id):
    """Update an existing budget item"""
    try:
        print("Received update request:", request.data)

        # Ensure budget item exists
        budget_item = Budget.objects.filter(
            budget_id=budget_id, trip_id=trip_id).first()
        if not budget_item:
            return Response({"error": "Budget item not found."}, status=404)

        # Extract and validate fields
        label = str(request.data.get("label", "")).strip()
        category = str(request.data.get("category", "")).strip()
        location = str(request.data.get("location", "")).strip()
        date_str = str(request.data.get("date", "")).strip()
        expense = request.data.get("expense", "")

        if not (label and expense and category and location and date_str):
            return Response({"error": "All fields are required."}, status=400)

        # Convert expense safely
        try:
            expense = float(expense)
            if expense <= 0:
                return Response({"error": "Expense must be greater than zero."}, status=400)
        except ValueError:
            return Response({"error": "Invalid expense format."}, status=400)

        # Convert date safely
        date = parse_date(date_str)
        if not date:
            return Response({"error": "Invalid date format."}, status=400)

        # Update fields
        budget_item.label = label
        budget_item.expense = expense
        budget_item.category = category
        budget_item.location = location
        budget_item.date = date
        budget_item.save()

        return Response({"message": "Expense updated successfully"}, status=200)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return Response({"error": "Internal server error", "details": str(e)}, status=500)


@api_view(['DELETE'])
def delete_budget_item(request, trip_id, budget_id):
    """Delete a budget item by its ID"""
    try:
        # Find the budget item
        budget_item = Budget.objects.filter(
            budget_id=budget_id, trip_id=trip_id).first()

        if not budget_item:
            return Response({"error": "Budget item not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the item
        budget_item.delete()
        return Response({"message": "Expense deleted successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return Response({"error": "Internal server error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_people_item(request, trip_id):
    """Add a person to the People table, ensuring all fields are valid"""

    # Extract data from request
    name = request.data.get("name", "").strip()
    contact = request.data.get("contact", "").strip()
    met_location = request.data.get("met_location", "").strip()
    met_date_str = request.data.get("met_date", "").strip()

    # Validate all fields
    if not (name and contact and met_location and met_date_str):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Parse date
    try:
        met_date = parse_date(met_date_str)
        if not met_date:
            raise ValueError
    except ValueError:
        return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the trip exists
    trip = Triprel.objects.filter(trip_id=trip_id).first()
    if not trip:
        return Response({"error": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create and save people item
    people_item = People.objects.create(
        trip=trip,
        name=name,
        contact=contact,
        met_location=met_location,
        met_date=met_date
    )

    return Response({"message": "Person added successfully", "person_id": people_item.person_id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_people_items(request, trip_id):
    """Fetch all people for a trip, ensuring the trip exists"""

    # Ensure the trip exists
    trip = Triprel.objects.filter(trip_id=trip_id).first()
    if not trip:
        return Response({"error": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

    # Fetch people
    people_items = People.objects.filter(trip=trip)

    serializer = PeopleSerializer(people_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_person_photo(request, person_id):
    """Add a photo for a person, ensuring the person exists"""

    # Extract data from request
    photo = request.FILES.get("photo", None)

    if not photo:
        return Response({"error": "Photo is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the person exists
    person = People.objects.filter(person_id=person_id).first()
    if not person:
        return Response({"error": "Person not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create and save person photo
    person_photo = PersonPhoto.objects.create(
        person=person,
        photo=photo
    )

    return Response({"message": "Photo added successfully", "photo_id": person_photo.photo_id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_person_photos(request, person_id):
    """Fetch all photos for a person, ensuring the person exists"""

    # Ensure the person exists
    person = People.objects.filter(person_id=person_id).first()
    if not person:
        return Response({"error": "Person not found."}, status=status.HTTP_404_NOT_FOUND)

    # Fetch photos
    photos = PersonPhoto.objects.filter(person=person)

    serializer = PersonPhotoSerializer(photos, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def update_people_item(request, trip_id, person_id):
    """Update an existing person in the People table"""

    try:
        # Ensure person exists
        person = People.objects.filter(
            person_id=person_id, trip_id=trip_id).first()
        if not person:
            return Response({"error": "Person not found."}, status=status.HTTP_404_NOT_FOUND)

        # Extract and validate fields
        name = request.data.get("name", "").strip()
        contact = request.data.get("contact", "").strip()
        met_location = request.data.get("met_location", "").strip()
        met_date_str = request.data.get("met_date", "").strip()

        if not (name and contact and met_location and met_date_str):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert date safely
        met_date = parse_date(met_date_str)
        if not met_date:
            return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)

        # Update fields
        person.name = name
        person.contact = contact
        person.met_location = met_location
        person.met_date = met_date
        person.save()

        return Response({"message": "Person updated successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return Response({"error": "Internal server error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_people_item(request, trip_id, person_id):
    """Delete a person from the People table"""

    try:
        # Ensure person exists
        person = People.objects.filter(
            person_id=person_id, trip_id=trip_id).first()
        if not person:
            return Response({"error": "Person not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the item
        person.delete()
        return Response({"message": "Person deleted successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return Response({"error": "Internal server error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_person_photo(request, trip_id, person_id):
    """Fetch the most recent photo for a person within a specific trip"""

    # Debugging log
    print(f"Fetching photo for trip_id: {trip_id}, person_id: {person_id}")

    person = People.objects.filter(
        person_id=person_id, trip_id=trip_id).first()
    if not person:
        return Response({"error": "Person not found in this trip."}, status=status.HTTP_404_NOT_FOUND)

    person_photo = PersonPhoto.objects.filter(
        person=person, trip=trip_id).order_by('-photo_id').first()

    if not person_photo:
        return Response({"message": "No photo found for this person."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PersonPhotoSerializer(person_photo)
    return Response(serializer.data)


@api_view(['POST'])
def add_or_update_person_photo(request, trip_id, person_id):
    """Add or update a person's photo, ensuring the person exists in the trip"""

    photo = request.FILES.get("photo", None)
    if not photo:
        return Response({"error": "Photo is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the trip exists
    trip = Triprel.objects.filter(trip_id=trip_id).first()
    if not trip:
        return Response({"error": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the person exists within the specified trip
    person = People.objects.filter(person_id=person_id, trip=trip).first()
    if not person:
        return Response({"error": "Person not found in this trip."}, status=status.HTTP_404_NOT_FOUND)

    # Check if a photo already exists for this person in this trip
    person_photo = PersonPhoto.objects.filter(person=person, trip=trip).first()

    if person_photo:
        person_photo.photo = photo
        person_photo.save()
        return Response({"message": "Photo updated successfully", "photo_id": person_photo.photo_id}, status=status.HTTP_200_OK)

    else:
        new_photo = PersonPhoto.objects.create(
            person=person, trip=trip, photo=photo)
        return Response({"message": "Photo added successfully", "photo_id": new_photo.photo_id}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_person_photo(request, trip_id, person_id):
    """Delete a person's photo within a specific trip"""

    person = People.objects.filter(
        person_id=person_id, trip_id=trip_id).first()
    if not person:
        return Response({"error": "Person not found in this trip."}, status=status.HTTP_404_NOT_FOUND)

    person_photo = PersonPhoto.objects.filter(
        person=person, trip=trip_id).first()

    if not person_photo:
        return Response({"error": "No photo found for this person."}, status=status.HTTP_404_NOT_FOUND)

    person_photo.delete()
    return Response({"message": "Photo deleted successfully."}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def cleanup_unused_images(request):
    """Delete images from storage that are not in the PersonPhoto table."""

    # ✅ Step 1: Get all file paths from the database (safe with prepared statement)
    with connection.cursor() as cursor:
        # Adjust table name if needed
        cursor.execute("SELECT photo FROM api_personphoto")
        db_image_paths = {row[0]
                          for row in cursor.fetchall()}  # Set for fast lookup

    # ✅ Step 2: Get all image file paths from the filesystem
    image_dir = os.path.join(settings.MEDIA_ROOT, "images")
    if not os.path.exists(image_dir):
        return Response({"message": "No images directory found."}, status=404)

    folder_images = {f"/media/images/{file}" for file in os.listdir(
        image_dir) if file.endswith(('.jpg', '.png', '.jpeg'))}

    # ✅ Step 3: Find and delete images that are NOT in the database
    unused_images = []
    db_image_names = [str(image_path.split('/')[-1])
                      for image_path in db_image_paths]
    for image_path in folder_images:
        image_name = str(image_path.split('/')[-1])
        if image_name not in db_image_names:
            unused_images.append(image_path)
    deleted_files = []

    for unused_image in unused_images:
        file_path = os.path.join(
            settings.MEDIA_ROOT, unused_image.replace('/media/', ''))
        try:
            os.remove(file_path)
            deleted_files.append(unused_image)
        except Exception as e:
            print(f"Failed to delete {unused_image}: {e}")

    with connection.cursor() as cursor:
        # Adjust table name if needed
        cursor.execute("SELECT memory_photo FROM api_memories")
        db_memory_paths = {row[0]
                           for row in cursor.fetchall()}

    memory_dir = os.path.join(settings.MEDIA_ROOT, "memories")
    if not os.path.exists(memory_dir):
        return Response({"message": "No memories directory found."}, status=404)

    folder_memories = {f"/media/memories/{file}" for file in os.listdir(
        memory_dir) if file.endswith(('.jpg', '.png', '.jpeg'))}

    unused_memories = []
    db_memory_names = [str(memory_path.split('/')[-1])
                       for memory_path in db_memory_paths]
    for memory_path in folder_memories:
        memory_name = str(memory_path.split('/')[-1])
        if memory_name not in db_memory_names:
            unused_memories.append(memory_path)

    deleted_memories = []
    for unused_memory in unused_memories:
        file_path = os.path.join(
            settings.MEDIA_ROOT, unused_memory.replace('/media/', ''))
        try:
            os.remove(file_path)
            deleted_memories.append(unused_memory)
        except Exception as e:
            print(f"Failed to delete {unused_memory}: {e}")

    return Response({"message": "Cleanup complete", "deleted": deleted_files, "unused": unused_images, "db_path": db_image_paths, "unused memories": unused_memories, "deleted memories": deleted_memories}, status=200)


@api_view(['GET'])
def get_memories(request, trip_id):
    """Fetch all memories for a specific trip"""

    trip = Triprel.objects.filter(trip_id=trip_id).first()
    if not trip:
        return Response({"error": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

    memories = Memories.objects.filter(trip=trip)
    serializer = MemoriesSerializer(memories, many=True)

    return Response(serializer.data)


@api_view(['POST'])
def add_memory(request, trip_id):
    """Add a memory to a trip with a photo, caption, location, and date."""

    # Extract data
    photo = request.FILES.get("memory_photo", None)
    caption = request.data.get("caption", "").strip()
    location = request.data.get("location", "").strip()
    date = request.data.get("date", "").strip()  # Date as string

    if not photo or not caption or not location or not date:
        return Response({"error": "All fields (photo, caption, location, date) are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the trip exists
    trip = Triprel.objects.filter(trip_id=trip_id).first()
    if not trip:
        return Response({"error": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create and save memory
    memory = Memories.objects.create(
        trip=trip,
        memory_photo=photo,
        caption=caption,
        location=location,
        date=date
    )

    return Response({"message": "Memory added successfully", "memory_id": memory.memory_id}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def edit_memory(request, trip_id, memory_id):
    """Edit an existing memory's photo, caption, location, or date."""

    # Ensure the memory exists
    memory = Memories.objects.filter(
        memory_id=memory_id, trip_id=trip_id).first()
    if not memory:
        return Response({"error": "Memory not found."}, status=status.HTTP_404_NOT_FOUND)

    # Extract data
    caption = request.data.get("caption", "").strip()
    location = request.data.get("location", "").strip()
    date = request.data.get("date", "").strip()  # Keep as string
    photo = request.FILES.get("memory_photo", None)

    if caption:
        memory.caption = caption

    if location:
        memory.location = location

    if date:
        memory.date = date  # No need to convert

    if photo:
        memory.memory_photo = photo  # Replace the existing photo

    memory.save()

    return Response({"message": "Memory updated successfully"}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_memory(request, trip_id, memory_id):
    """Delete a memory from the database and remove its image."""

    # Ensure the memory exists
    memory = Memories.objects.filter(
        memory_id=memory_id, trip_id=trip_id).first()
    if not memory:
        return Response({"error": "Memory not found."}, status=status.HTTP_404_NOT_FOUND)

    # Delete the photo file
    memory.memory_photo.delete(save=False)

    # Delete the memory record
    memory.delete()

    return Response({"message": "Memory deleted successfully."}, status=status.HTTP_200_OK)

from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response

# @api_view(['GET'])
# def get_report(request):
#     """
#     Get total and average expenses based on user filters (trip, location, date range).
#     Uses **ONLY PREPARED STATEMENTS**, NO ORM.
#     """

#     trip_id = request.GET.get("trip_id")  # Optional
#     location = request.GET.get("location")  # Optional
#     start_date = request.GET.get("start_date")  # Optional
#     end_date = request.GET.get("end_date")  # Optional

#     # Base query - filters dynamically based on input
#     base_query = """
#         SELECT SUM(expense) AS total_expense, AVG(expense) AS average_expense, COUNT(*) AS number_of_expenses, MAX(date) AS last_expense_date, MAX(expense) AS max_expense, MIN(expense) AS min_expense
#         FROM api_budget
#         WHERE 1=1
#     """
#     filters = []
#     params = []

#     if trip_id:
#         base_query += " AND trip_id = %s"
#         params.append(trip_id)

#     if location:
#         base_query += " AND location = %s"
#         params.append(location)

#     if start_date and end_date:
#         base_query += " AND date BETWEEN %s AND %s"
#         params.extend([start_date, end_date])

#     # Execute query
#     with connection.cursor() as cursor:
#         cursor.execute(base_query, params)
#         result = cursor.fetchone()

#     total_expense = result[0] if result[0] else 0
#     average_expense = result[1] if result[1] else 0
#     number_of_expenses = result[2] if result[2] else 0
#     last_expense_date = result[3] if result[3] else None
#     max_expense = result[4] if result[4] else 0
#     min_expense = result[5] if result[5] else 0

#     # Get breakdown by category (Pie Chart Data)
#     category_query = """
#         SELECT category, SUM(expense) AS total_category_expense
#         FROM api_budget
#         WHERE 1=1
#     """
#     if trip_id:
#         category_query += " AND trip_id = %s"
#     if location:
#         category_query += " AND location = %s"
#     if start_date and end_date:
#         category_query += " AND date BETWEEN %s AND %s"

#     category_query += " GROUP BY category"
#     category_params = params.copy()  # Same parameters as base_query

#     with connection.cursor() as cursor:
#         cursor.execute(category_query, category_params)
#         categories = cursor.fetchall()

#     category_data = [{"category": row[0], "total": row[1]} for row in categories]

#     # Get breakdown by location (Pie Chart Data)
#     location_query = """
#         SELECT location, SUM(expense) AS total_location_expense
#         FROM api_budget
#         WHERE 1=1
#     """
#     if trip_id:
#         location_query += " AND trip_id = %s"
#     if start_date and end_date:
#         location_query += " AND date BETWEEN %s AND %s"

#     location_query += " GROUP BY location"
#     location_params = params.copy()  # Same parameters as base_query

#     with connection.cursor() as cursor:
#         cursor.execute(location_query, location_params)
#         locations = cursor.fetchall()

#     location_data = [{"location": row[0], "total": row[1]} for row in locations]

#     # Get breakdown by trip (Pie Chart Data)
#     trip_query = """
#         SELECT trip_id, SUM(expense) AS total_trip_expense
#         FROM api_budget
#         WHERE 1=1
#     """
#     if location:
#         trip_query += " AND location = %s"
#     if start_date and end_date:
#         trip_query += " AND date BETWEEN %s AND %s"

#     trip_query += " GROUP BY trip_id"
#     trip_params = params.copy()  # Same parameters as base_query

#     with connection.cursor() as cursor:
#         cursor.execute(trip_query, trip_params)
#         trips = cursor.fetchall()

#     trip_data = [{"trip_id": row[0], "total": row[1]} for row in trips]

#     # Return JSON Response
#     return Response({
#         "total_expense": total_expense,
#         "average_expense": average_expense,
#         "category_data": category_data,
#         "location_data": location_data,
#         "trip_data": trip_data
#     })

# @api_view(['GET'])
# def get_locations_for_input(request):
#     """Fetch unique locations from the budget table for input purposes"""

#     query = """
#         SELECT DISTINCT location FROM api_budget
#         WHERE location IS NOT NULL AND location != ''
#     """

#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         locations = cursor.fetchall()

#     # Convert to list of strings
#     locations_list = [row[0] for row in locations]

#     return Response(locations_list)

# @api_view(['GET'])
# def get_categories_for_input(request):
#     """Fetch unique categories from the budget table for input purposes"""

#     query = """
#         SELECT DISTINCT category FROM api_budget
#         WHERE category IS NOT NULL AND category != ''
#     """

#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         categories = cursor.fetchall()

#     # Convert to list of strings
#     categories_list = [row[0] for row in categories]

#     return Response(categories_list)

@api_view(['GET'])
def get_unique_locations(request):
    """
    Return unique non-empty, non-null locations from Budget table using prepared SQL.
    """
    query = """
        SELECT DISTINCT location FROM api_budget
        WHERE location IS NOT NULL AND TRIM(location) != ''
        ORDER BY location ASC
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        locations = [{"location": row[0]} for row in results]

    return Response(locations, status=200)

@api_view(['GET'])
def get_unique_categories(request):
    """
    Return unique non-empty, non-null categories from Budget table using prepared SQL.
    """
    query = """
        SELECT DISTINCT category FROM api_budget
        WHERE category IS NOT NULL AND TRIM(category) != ''
        ORDER BY category ASC
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        categories = [{"category": row[0]} for row in results]

    return Response(categories, status=200)

@api_view(['GET'])
def get_expense_summary(request):
    """
    Returns total, average, min, max, count, and last date of expenses based on filters.
    """
    trip_id = request.GET.get("trip_id")
    location = request.GET.get("location")
    category = request.GET.get("category")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    query = """
        SELECT 
            SUM(expense) AS total_expense,
            AVG(expense) AS average_expense,
            COUNT(*) AS number_of_expenses,
            MAX(expense) AS max_expense,
            MIN(expense) AS min_expense,
            MAX(date) AS last_expense_date
        FROM api_budget
        WHERE 1=1
    """
    params = []

    if trip_id:
        query += " AND trip_id = %s"
        params.append(trip_id)
    if location:
        query += " AND location = %s"
        params.append(location)
    if category:
        query += " AND category = %s"
        params.append(category)
    if start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchone()

    return Response({
        "total_expense": result[0] or 0,
        "average_expense": result[1] or 0,
        "number_of_expenses": result[2] or 0,
        "max_expense": result[3] or 0,
        "min_expense": result[4] or 0,
        "last_date": result[5]
    })

@api_view(['GET'])
def get_category_pie_data(request):
    """
    Returns category-wise total expenses (filtered).
    If user selected a specific category, returns just that slice.
    """
    trip_id = request.GET.get("trip_id")
    location = request.GET.get("location")
    category = request.GET.get("category")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    query = """
        SELECT category, SUM(expense) AS total
        FROM api_budget
        WHERE 1=1
    """
    params = []

    if trip_id:
        query += " AND trip_id = %s"
        params.append(trip_id)
    if location:
        query += " AND location = %s"
        params.append(location)
    if category:
        query += " AND category = %s"
        params.append(category)
    if start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    query += " GROUP BY category ORDER BY total DESC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()

    data = [{"category": row[0], "total": row[1]} for row in results]
    return Response(data)

@api_view(['GET'])
def get_location_pie_data(request):
    """
    Returns location-wise total expenses (filtered).
    If user selected a specific location, returns just that slice.
    """
    trip_id = request.GET.get("trip_id")
    location = request.GET.get("location")
    category = request.GET.get("category")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    query = """
        SELECT location, SUM(expense) AS total
        FROM api_budget
        WHERE 1=1
    """
    params = []

    if trip_id:
        query += " AND trip_id = %s"
        params.append(trip_id)
    if location:
        query += " AND location = %s"
        params.append(location)
    if category:
        query += " AND category = %s"
        params.append(category)
    if start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    query += " GROUP BY location ORDER BY total DESC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()

    data = [{"location": row[0], "total": row[1]} for row in results]
    return Response(data)

@api_view(['GET'])
def get_secondary_summary(request):
    trip_id = request.GET.get("trip_id")
    location = request.GET.get("location")
    category = request.GET.get("category")  # used only for Budget filter
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    people_count = 0
    memory_count = 0
    location_count = 0

    # --- Count of people met ---
    people_query = "SELECT COUNT(*) FROM api_people WHERE 1=1"
    people_params = []

    if trip_id:
        people_query += " AND trip_id = %s"
        people_params.append(trip_id)
    if location:
        people_query += " AND met_location = %s"
        people_params.append(location)
    if start_date and end_date:
        people_query += " AND met_date BETWEEN %s AND %s"
        people_params.extend([start_date, end_date])

    with connection.cursor() as cursor:
        cursor.execute(people_query, people_params)
        people_count = cursor.fetchone()[0] or 0

    # --- Count of unique locations visited (Budget table) ---
    location_query = "SELECT COUNT(DISTINCT location) FROM api_budget WHERE 1=1"
    location_params = []

    if trip_id:
        location_query += " AND trip_id = %s"
        location_params.append(trip_id)
    if category:
        location_query += " AND category = %s"
        location_params.append(category)
    if start_date and end_date:
        location_query += " AND date BETWEEN %s AND %s"
        location_params.extend([start_date, end_date])
    
    location_query += " UNION SELECT COUNT(DISTINCT met_location) FROM api_people WHERE 1=1"
    if trip_id:
        location_query += " AND trip_id = %s"
        location_params.append(trip_id)
    if start_date and end_date:
        location_query += " AND met_date BETWEEN %s AND %s"
        location_params.extend([start_date, end_date])
        
    location_query += " UNION SELECT COUNT(DISTINCT location) FROM api_memories WHERE 1=1"
    if trip_id:
        location_query += " AND trip_id = %s"
        location_params.append(trip_id)
    if start_date and end_date:
        location_query += " AND date BETWEEN %s AND %s"
        location_params.extend([start_date, end_date])

    with connection.cursor() as cursor:
        cursor.execute(location_query, location_params)
        location_count = cursor.fetchone()[0] or 0

    # --- Count of memories (Memories table) ---
    memory_query = "SELECT COUNT(*) FROM api_memories WHERE 1=1"
    memory_params = []

    if trip_id:
        memory_query += " AND trip_id = %s"
        memory_params.append(trip_id)
    if location:
        memory_query += " AND location = %s"
        memory_params.append(location)
    if start_date and end_date:
        memory_query += " AND date BETWEEN %s AND %s"
        memory_params.extend([start_date, end_date])

    with connection.cursor() as cursor:
        cursor.execute(memory_query, memory_params)
        memory_count = cursor.fetchone()[0] or 0

    return Response({
        "people_met": people_count,
        "locations_visited": location_count,
        "memories": memory_count
    })

@api_view(['GET'])
def get_people_photos_filtered(request):
    """
    Return list of people photo URLs based on filters.
    """
    trip_id = request.GET.get("trip_id")
    location = request.GET.get("location")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    query = """
        SELECT DISTINCT photo FROM api_personphoto pp
        JOIN api_people p ON pp.person_id = p.person_id
        WHERE 1=1
    """
    params = []

    if trip_id:
        query += " AND p.trip_id = %s"
        params.append(trip_id)
    if location:
        query += " AND p.met_location = %s"
        params.append(location)
    if start_date and end_date:
        query += " AND p.met_date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        photos = [row[0] for row in cursor.fetchall() if row[0]]

    return Response({"photos": photos})


@api_view(['GET'])
def get_memory_photos_filtered(request):
    """
    Return list of memory photo URLs based on filters.
    """
    trip_id = request.GET.get("trip_id")
    location = request.GET.get("location")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    query = """
        SELECT DISTINCT memory_photo FROM api_memories
        WHERE memory_photo IS NOT NULL AND TRIM(memory_photo) != ''
    """
    params = []

    if trip_id:
        query += " AND trip_id = %s"
        params.append(trip_id)
    if location:
        query += " AND location = %s"
        params.append(location)
    if start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        photos = [row[0] for row in cursor.fetchall() if row[0]]

    return Response({"photos": photos})
