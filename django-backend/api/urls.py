from django.urls import path
from .views import get_trips, add_trip
from .views import get_trip_details, get_budget_items, add_budget_item, update_budget_item, \
        delete_budget_item, add_people_item, get_people_items, update_people_item, delete_people_item, \
        get_person_photo, add_or_update_person_photo, delete_person_photo, cleanup_unused_images, \
        add_memory, edit_memory, delete_memory, get_memories, edit_trip, delete_trip, get_unique_locations, \
        get_unique_categories, get_expense_summary, get_category_pie_data, get_location_pie_data, get_secondary_summary, \
        get_people_photos_filtered, get_memory_photos_filtered

urlpatterns = [
    path('trips/', get_trips),  # GET - Fetch all trips
    path('add_trip/', add_trip),  # POST - Add a new trip
    path('trip/<int:trip_id>/', get_trip_details), # GET - Fetch trip details
    path('trip/<int:trip_id>/edit/', edit_trip),  # PUT - Edit trip name
    path('trip/<int:trip_id>/delete/', delete_trip),  # DELETE - Delete trip
    path('trip/<int:trip_id>/budget/', get_budget_items), # GET - Fetch budget items for a trip
    path('trip/<int:trip_id>/budget/add/', add_budget_item),  # POST - Add a budget item to a trip
    path('trip/<int:trip_id>/budget/<int:budget_id>/edit/', update_budget_item),  # PUT - Update a budget item
    path('trip/<int:trip_id>/budget/<int:budget_id>/delete/', delete_budget_item),  # DELETE - Delete a budget item
    path('trip/<int:trip_id>/people/add/', add_people_item),  # POST - Add a person to a trip
    path('trip/<int:trip_id>/people/', get_people_items),  # GET - Fetch all people for a trip
    path('trip/<int:trip_id>/people/<int:person_id>/edit/', update_people_item),  # PUT - Update a person
    path('trip/<int:trip_id>/people/<int:person_id>/delete/', delete_people_item),  # DELETE - Delete a person
    path('trip/<int:trip_id>/people/<int:person_id>/photo/', get_person_photo),  # GET - Fetch a person's photo in a trip
    path('trip/<int:trip_id>/people/<int:person_id>/photo/add_or_update/', add_or_update_person_photo),  # POST - Add/Update photo
    path('trip/<int:trip_id>/people/<int:person_id>/photo/delete/', delete_person_photo),  # DELETE - Delete photo
    path('cleanup_unused_images/', cleanup_unused_images),  # DELETE - Clean up orphaned images
    path('trip/<int:trip_id>/memories/', get_memories),  # GET - Fetch all memories for a trip
    path('trip/<int:trip_id>/memories/add/', add_memory),  # POST - Add a memory
    path('trip/<int:trip_id>/memories/<int:memory_id>/edit/', edit_memory),  # PUT - Edit a memory
    path('trip/<int:trip_id>/memories/<int:memory_id>/delete/', delete_memory),  # DELETE - Delete a memory
    path('locations/', get_unique_locations), # GET - Fetch unique locations
    path('categories/', get_unique_categories), # GET - Fetch unique categories
    path('report/summary/', get_expense_summary), # GET - Fetch expense summary data
    path('report/category-pie/', get_category_pie_data), # GET - Fetch category pie chart data
    path('report/location-pie/', get_location_pie_data), # GET - Fetch location pie chart data
    path('report/secondary-summary/', get_secondary_summary), # GET - Fetch secondary summary data
    path('report/people-photos/', get_people_photos_filtered), # GET - Fetch people photos filtered by trip_id
    path('report/memory-photos/', get_memory_photos_filtered), # GET - Fetch memory photos filtered by trip_id
]
