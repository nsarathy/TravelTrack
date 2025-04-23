<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import axios from "axios";

const route = useRoute();
const router = useRouter();
const tripId = route.params.tripId;
const tripName = ref("");
const activeTab = ref("Budget");
const budgetItems = ref([]);
const showPopup = ref(false);
const errorMessage = ref("");
const isEditing = ref(false);
const editingBudgetId = ref(null);
const peopleItems = ref([]);
const showPeoplePopup = ref(false);
const errorMessagePeople = ref("");
const isEditingPerson = ref(false);
const editingPersonId = ref(null);
const showPhotoPopup = ref(false);
const selectedPerson = ref(null);
const personPhoto = ref(null);
const errorMessagePhoto = ref("");
const newPhoto = ref(null);
const memories = ref([]);
const showMemoryPopup = ref(false);
const isEditingMemory = ref(false);
const editingMemoryId = ref(null);
const errorMessageMemory = ref("");
const showSettingsPopup = ref(false);
const newTripName = ref("");
const errorMessageTrip = ref("");

const openSettingsPopup = () => {
  showSettingsPopup.value = true;
  newTripName.value = tripName.value; // Pre-fill with existing trip name
};

const updateTripName = async () => {
  errorMessageTrip.value = "";

  if (!newTripName.value.trim()) {
    errorMessageTrip.value = "Trip name cannot be empty.";
    return;
  }

  try {
    const response = await axios.put(
      `http://127.0.0.1:8000/api/trip/${tripId}/edit/`,
      { trip_name: newTripName.value }
    );

    tripName.value = newTripName.value;
    showSettingsPopup.value = false;
  } catch (error) {
    errorMessageTrip.value =
      error.response?.data?.error || "Failed to update trip name.";
  }
};

const deleteTrip = async () => {
  if (
    !confirm(
      "Are you sure you want to delete this trip? This action cannot be undone."
    )
  )
    return;

  try {
    await axios.delete(`http://127.0.0.1:8000/api/trip/${tripId}/delete/`);
    router.push("/"); // Redirect to home after deletion
  } catch (error) {
    errorMessageTrip.value = "Failed to delete trip.";
  }
};

const formatDateCorrectly = (dateString) => {
  const date = new Date(dateString + "T00:00:00"); // Force it to be interpreted as local
  return date.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
};

const newPerson = ref({
  name: "",
  contact: "",
  met_location: "",
  met_date: new Date().toISOString().split("T")[0],
});

const newExpense = ref({
  label: "",
  expense: "",
  category: "Food and Drink",
  location: "",
  date: new Date().toISOString().split("T")[0],
});

const newMemory = ref({
  caption: "",
  location: "",
  date: new Date().toISOString().split("T")[0],
  memory_photo: null,
});

const fetchTripDetails = async () => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/trip/${tripId}/`
    );
    tripName.value = response.data.trip_name;
  } catch (error) {
    console.error("Error fetching trip details:", error);
  }
};

const fetchBudgetItems = async () => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/trip/${tripId}/budget/`
    );
    budgetItems.value = response.data;
  } catch (error) {
    console.error("Error fetching budget items:", error);
  }
};

const fetchPeopleItems = async () => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/trip/${tripId}/people/`
    );
    peopleItems.value = response.data;
  } catch (error) {
    console.error("Error fetching people:", error);
  }
};

const fetchPersonPhoto = async (tripId, personId) => {
  if (!personId) {
    console.error("fetchPersonPhoto: personId is undefined!");
    return;
  }

  try {
    console.log(`Fetching photo for trip: ${tripId}, person: ${personId}`);
    const response = await axios.get(
      `http://127.0.0.1:8000/api/trip/${tripId}/people/${personId}/photo/`
    );
    personPhoto.value = response.data.photo;
  } catch (error) {
    personPhoto.value = null;
    console.error("Error fetching person photo:", error);
  }
};

const fetchMemories = async () => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/trip/${tripId}/memories/`
    );
    memories.value = response.data;
  } catch (error) {
    console.error("Error fetching memories:", error);
  }
};

onMounted(() => {
  fetchTripDetails();
  fetchBudgetItems();
  fetchPeopleItems();
  fetchMemories();
});

const addExpenseClicked = () => {
  showPopup.value = true;
  isEditing.value = false;
  editingBudgetId.value = null;
};

const addMemoryClicked = () => {
  showMemoryPopup.value = true;
  isEditingMemory.value = false;
  editingMemoryId.value = null;
};

const openEditPopup = (item) => {
  isEditing.value = true;
  editingBudgetId.value = item.budget_id;
  newExpense.value = { ...item };
  showPopup.value = true;
};

const openEditPersonPopup = (person) => {
  isEditingPerson.value = true;
  editingPersonId.value = person.person_id;
  newPerson.value = { ...person };
  showPeoplePopup.value = true;
};

const openPhotoPopup = (person) => {
  if (!person || !person.person_id) {
    console.error("openPhotoPopup: Invalid person data", person);
    return;
  }

  selectedPerson.value = person;
  fetchPersonPhoto(tripId, person.person_id);
  showPhotoPopup.value = true;
};

const openEditMemoryPopup = (memory) => {
  isEditingMemory.value = true;
  editingMemoryId.value = memory.memory_id;
  newMemory.value = { ...memory, memory_photo: null };
  showMemoryPopup.value = true;
};

const handlePhotoChange = (event) => {
  newPhoto.value = event.target.files[0];
};

const handleMemoryPhotoChange = (event) => {
  newMemory.value.memory_photo = event.target.files[0];
};

const saveExpense = async () => {
  errorMessage.value = "";

  if (
    !newExpense.value.label.trim() ||
    !String(newExpense.value.expense).trim() ||
    !newExpense.value.category.trim() ||
    !newExpense.value.location.trim() ||
    !newExpense.value.date.trim()
  ) {
    errorMessage.value = "All fields are required.";
    return;
  }

  try {
    newExpense.value.expense = parseFloat(newExpense.value.expense);
    if (isNaN(newExpense.value.expense) || newExpense.value.expense <= 0) {
      throw new Error("Expense must be a valid number greater than zero.");
    }
  } catch (error) {
    errorMessage.value = "Expense must be a valid number greater than zero.";
    return;
  }

  try {
    if (isEditing.value) {
      await axios.put(
        `http://127.0.0.1:8000/api/trip/${tripId}/budget/${editingBudgetId.value}/edit/`,
        newExpense.value
      );
    } else {
      await axios.post(
        `http://127.0.0.1:8000/api/trip/${tripId}/budget/add/`,
        newExpense.value
      );
    }

    fetchBudgetItems();
    showPopup.value = false;
    isEditing.value = false;
    editingBudgetId.value = null;
    newExpense.value = {
      label: "",
      expense: "",
      category: "Food and Drink",
      location: "",
      date: new Date().toISOString().split("T")[0],
    };
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error || "Failed to save expense.";
  }
};

const deleteExpense = async (budgetId) => {
  if (!confirm("Are you sure you want to delete this expense?")) return;

  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/trip/${tripId}/budget/${budgetId}/delete/`
    );
    fetchBudgetItems();
  } catch (error) {
    console.error("Error deleting expense:", error.response?.data || error);
  }
};

const addPersonClicked = () => {
  showPeoplePopup.value = true;
};

const savePerson = async () => {
  errorMessagePeople.value = "";

  if (
    !newPerson.value.name.trim() ||
    !newPerson.value.contact.trim() ||
    !newPerson.value.met_location.trim() ||
    !newPerson.value.met_date.trim()
  ) {
    errorMessagePeople.value = "All fields are required.";
    return;
  }

  try {
    if (isEditingPerson.value) {
      await axios.put(
        `http://127.0.0.1:8000/api/trip/${tripId}/people/${editingPersonId.value}/edit/`,
        newPerson.value
      );
    } else {
      await axios.post(
        `http://127.0.0.1:8000/api/trip/${tripId}/people/add/`,
        newPerson.value
      );
    }

    fetchPeopleItems();
    showPeoplePopup.value = false;
    isEditingPerson.value = false;
    editingPersonId.value = null;

    // Reset fields
    newPerson.value = {
      name: "",
      contact: "",
      met_location: "",
      met_date: new Date().toISOString().split("T")[0],
    };
  } catch (error) {
    errorMessagePeople.value =
      error.response?.data?.error || "Failed to save person.";
  }
};

const deletePerson = async (personId) => {
  if (!confirm("Are you sure you want to delete this person?")) return;

  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/trip/${tripId}/people/${personId}/delete/`
    );
    fetchPeopleItems();
  } catch (error) {
    console.error("Error deleting person:", error.response?.data || error);
  }
};

const uploadPhoto = async () => {
  if (!newPhoto.value) {
    errorMessagePhoto.value = "Please select a photo.";
    return;
  }

  const formData = new FormData();
  formData.append("photo", newPhoto.value);

  try {
    await axios.post(
      `http://127.0.0.1:8000/api/trip/${tripId}/people/${selectedPerson.value.person_id}/photo/add_or_update/`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    newPhoto.value = null;
    errorMessagePhoto.value = "";
    fetchPersonPhoto(tripId, selectedPerson.value.person_id); // Refresh photo
  } catch (error) {
    errorMessagePhoto.value = "Failed to upload photo.";
  }
};

const deletePhoto = async () => {
  if (!confirm("Are you sure you want to delete this photo?")) return;

  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/trip/${tripId}/people/${selectedPerson.value.person_id}/photo/delete/`
    );

    personPhoto.value = null; // Remove photo from UI
  } catch (error) {
    console.error("Error deleting photo:", error);
  }
};

const saveMemory = async () => {
  errorMessageMemory.value = "";

  if (
    !newMemory.value.caption.trim() ||
    !newMemory.value.location.trim() ||
    !newMemory.value.date.trim()
  ) {
    errorMessageMemory.value = "All fields are required.";
    return;
  }

  const formData = new FormData();
  formData.append("caption", newMemory.value.caption);
  formData.append("location", newMemory.value.location);
  formData.append("date", newMemory.value.date);

  if (newMemory.value.memory_photo) {
    formData.append("memory_photo", newMemory.value.memory_photo);
  }

  try {
    if (isEditingMemory.value) {
      await axios.put(
        `http://127.0.0.1:8000/api/trip/${tripId}/memories/${editingMemoryId.value}/edit/`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
    } else {
      await axios.post(
        `http://127.0.0.1:8000/api/trip/${tripId}/memories/add/`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
    }

    fetchMemories();
    showMemoryPopup.value = false;
    isEditingMemory.value = false;
    editingMemoryId.value = null;

    newMemory.value = {
      caption: "",
      location: "",
      date: new Date().toISOString().split("T")[0],
      memory_photo: null,
    };
  } catch (error) {
    errorMessageMemory.value =
      error.response?.data?.error || "Failed to save memory.";
  }
};

const deleteMemory = async (memoryId) => {
  if (!confirm("Are you sure you want to delete this memory?")) return;

  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/trip/${tripId}/memories/${memoryId}/delete/`
    );
    fetchMemories();
  } catch (error) {
    console.error("Error deleting memory:", error);
  }
};

const goBack = () => {
  router.push("/");
};
</script>

<template>
  <div class="container">
    <button class="settings-button" @click="openSettingsPopup">
      ⚙️ Settings
    </button>
    <button class="goback-button" @click="goBack">⬅️ Go Back</button>
    <h1>{{ tripName }}</h1>
    <div class="tabs">
      <button
        @click="activeTab = 'Budget'"
        :class="{ active: activeTab === 'Budget' }"
      >
        Expenses
      </button>
      <button
        @click="activeTab = 'People'"
        :class="{ active: activeTab === 'People' }"
      >
        People
      </button>
      <button
        @click="activeTab = 'Memories'"
        :class="{ active: activeTab === 'Memories' }"
      >
        Memories
      </button>
    </div>

    <div v-if="activeTab === 'Budget'">
      <button class="add-button" @click="addExpenseClicked()">
        + Add Expense
      </button>
      <table>
        <thead>
          <tr>
            <th></th>
            <th>LABEL</th>
            <th>EXPENSE</th>
            <th>CATEGORY</th>
            <th>LOCATION</th>
            <th>DATE</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in budgetItems" :key="item.budget_id">
            <td>
              <button class="edit-btn" @click="openEditPopup(item)">
                Edit
              </button>
              <button class="delete-btn" @click="deleteExpense(item.budget_id)">
                Delete
              </button>
            </td>
            <td>{{ item.label }}</td>
            <td>{{ item.expense }}</td>
            <td>{{ item.category }}</td>
            <td>{{ item.location }}</td>
            <td>
              {{ formatDateCorrectly(item.date) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'People'">
      <button class="add-button" @click="addPersonClicked">+ Add Person</button>

      <table v-if="peopleItems.length">
        <thead>
          <tr>
            <th></th>
            <th>NAME</th>
            <th>CONTACT</th>
            <th>MET LOCATION</th>
            <th>MET DATE</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="person in peopleItems" :key="person.person_id">
            <td>
              <button class="edit-btn" @click="openEditPersonPopup(person)">
                Edit
              </button>
              <button
                class="delete-btn"
                @click="deletePerson(person.person_id)"
              >
                Delete
              </button>
            </td>
            <td>{{ person.name }}</td>
            <td>{{ person.contact }}</td>
            <td>{{ person.met_location }}</td>
            <td>
              {{ formatDateCorrectly(person.met_date) }}
            </td>
            <td>
              <button class="edit-btn" @click="openPhotoPopup(person)">
                Photo
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No people added yet.</p>
    </div>

    <div v-if="activeTab === 'Memories'">
      <button class="add-memory-button" @click="addMemoryClicked()">
        + Add Memory
      </button>

      <div v-if="memories.length" class="memories-feed">
        <div
          v-for="memory in memories"
          :key="memory.memory_id"
          class="memory-item"
        >
          <p class="memory-location-date">
            <strong>{{ memory.location }}</strong
            >, {{ memory.date }}
          </p>

          <img
            :src="'http://127.0.0.1:8000' + memory.memory_photo"
            alt="Memory Photo"
            class="memory-photo"
            :style="{ width: memory.memory_photo_width > 600 ? '50%' : '40%' }"
          />

          <p class="memory-caption">{{ memory.caption }}</p>

          <div class="memory-buttons">
            <button class="edit-btn" @click="openEditMemoryPopup(memory)">
              Edit
            </button>
            <button class="delete-btn" @click="deleteMemory(memory.memory_id)">
              Delete
            </button>
          </div>

          <hr class="memory-separator" />
        </div>
      </div>

      <p v-else>No memories added yet.</p>
    </div>

    <div v-if="showPopup" class="popup-overlay">
      <div class="popup">
        <h2>{{ isEditing ? "Edit Expense" : "Add Expense" }}</h2>
        <input v-model="newExpense.label" placeholder="Label" />
        <input v-model="newExpense.expense" placeholder="$0" type="number" />
        <select v-model="newExpense.category">
          <option>Food and Drink</option>
          <option>Activity</option>
          <option>Air Fare</option>
          <option>Accommodations</option>
          <option>Transportation</option>
          <option>Shopping</option>
          <option>Other</option>
        </select>
        <input v-model="newExpense.location" placeholder="Location" />
        <input v-model="newExpense.date" type="date" />
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <div class="popup-buttons">
          <button @click="showPopup = false">Cancel</button>
          <button @click="saveExpense" class="save-btn">Save</button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="showPeoplePopup" class="popup-overlay">
    <div class="popup">
      <h2>Add Person</h2>
      <input v-model="newPerson.name" placeholder="Name" />
      <input v-model="newPerson.contact" placeholder="Contact" />
      <input v-model="newPerson.met_location" placeholder="Met Location" />
      <input v-model="newPerson.met_date" type="date" />
      <p v-if="errorMessagePeople" class="error-message">
        {{ errorMessagePeople }}
      </p>
      <div class="popup-buttons">
        <button @click="showPeoplePopup = false">Cancel</button>
        <button @click="savePerson" class="save-btn">Save</button>
      </div>
    </div>
  </div>

  <div v-if="showPhotoPopup" class="popup-overlay">
    <div class="popup">
      <h2>Manage Photo for {{ selectedPerson.name }}</h2>

      <div v-if="personPhoto">
        <img
          :src="'http://127.0.0.1:8000' + personPhoto"
          alt="Person Photo"
          class="photo-preview"
        />
      </div>
      <p v-else>No photo available.</p>

      <input type="file" @change="handlePhotoChange" accept="image/*" />
      <p v-if="errorMessagePhoto" class="error-message">
        {{ errorMessagePhoto }}
      </p>

      <div class="popup-buttons">
        <button @click="showPhotoPopup = false">Close</button>
        <button @click="uploadPhoto" class="save-btn">Upload</button>
        <button v-if="personPhoto" @click="deletePhoto" class="delete-btn">
          Delete
        </button>
      </div>
    </div>
  </div>

  <div v-if="showMemoryPopup" class="popup-overlay">
    <div class="popup">
      <h2>{{ isEditingMemory ? "Edit Memory" : "Add Memory" }}</h2>

      <input v-model="newMemory.location" placeholder="Location" />
      <input v-model="newMemory.date" type="date" />
      <textarea v-model="newMemory.caption" placeholder="Caption"></textarea>

      <input type="file" @change="handleMemoryPhotoChange" accept="image/*" />
      <p v-if="errorMessageMemory" class="error-message">
        {{ errorMessageMemory }}
      </p>

      <div class="popup-buttons">
        <button @click="showMemoryPopup = false">Cancel</button>
        <button @click="saveMemory" class="save-btn">Save</button>
      </div>
    </div>
  </div>

  <div v-if="showSettingsPopup" class="popup-overlay">
    <div class="popup">
      <h2>Edit Trip</h2>

      <input v-model="newTripName" placeholder="Trip Name" />
      <p v-if="errorMessageTrip" class="error-message">
        {{ errorMessageTrip }}
      </p>

      <div class="popup-buttons">
        <button @click="showSettingsPopup = false">Cancel</button>
        <button @click="updateTripName" class="save-btn">Save</button>
      </div>

      <hr />
      <button @click="deleteTrip" class="delete-trip-btn">🗑 Delete Trip</button>
    </div>
  </div>
</template>

<style>
.container {
  text-align: center;
  max-width: 800px;
  margin: auto;
  font-family: Arial, sans-serif;
}
.tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}
.tabs button {
  padding: 10px 20px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}
.tabs .active {
  background-color: #42b983;
  color: white;
}
.add-button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  margin-bottom: 15px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
th,
td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}
th {
  background-color: #f4f4f4;
}
.edit-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  margin-right: 5px;
  cursor: pointer;
}
.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
}
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.popup {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}
.popup input,
.popup select {
  display: block;
  margin: 10px auto;
  padding: 8px;
  width: 80%;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.popup-buttons {
  margin-top: 10px;
}
.popup-buttons button {
  padding: 10px 15px;
  margin: 5px;
  border: none;
  cursor: pointer;
}
.save-btn {
  background-color: #42b983;
  color: white;
}

.popup input {
  display: block;
  margin: 10px auto;
  padding: 8px;
  width: 80%;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.photo-preview {
  width: 100%;
  max-width: 300px;
  margin: 10px auto;
  display: block;
  border-radius: 5px;
}

.memories-feed {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 10px;
}

.memory-item {
  text-align: center;
  padding: 15px;
}

.memory-location-date {
  font-size: 16px;
  color: #333;
}

.memory-photo {
  max-width: 100%;
  border-radius: 5px;
  margin: 10px 0;
}

.memory-caption {
  font-size: 14px;
  color: #555;
}

.memory-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.memory-separator {
  border: none;
  height: 1px;
  background-color: #ccc;
  margin: 15px 0;
}

.add-memory-button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  margin-bottom: 15px;
}

.settings-button {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  background-color: #333;
}

.delete-trip-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
  margin-top: 10px;
}

.delete-trip-btn:hover {
  background-color: #b02a37;
}

.goback-button {
  /* left top corner */
  position: absolute;
  top: 15px;
  left: 20px;
  background-color: #333;
  color: white;
  border: none;
  padding: 10px 15px;
}

</style>
