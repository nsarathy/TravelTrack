<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const tripName = ref("");
const trips = ref([]);
const errorMessage = ref("");

const fetchTrips = async () => {
  try {
    const response = await axios.get("http://127.0.0.1:8000/api/trips/");
    trips.value = response.data;
    errorMessage.value = ""; // Clear errors if successful
  } catch (error) {
    console.error("Error fetching trips:", error);
    errorMessage.value = "Failed to load trips. Please try again later.";
  }
};

const addTrip = async () => {
  if (tripName.value.trim() !== "") {
    try {
      await axios.post("http://127.0.0.1:8000/api/add_trip/", {
        trip_name: tripName.value,
      });
      tripName.value = "";
      fetchTrips();
    } catch (error) {
      console.error("Error adding trip:", error);
      errorMessage.value = error.response?.data?.error || "Failed to add trip.";
    }
  } else {
    errorMessage.value = "Trip name cannot be empty.";
  }
};

const cleanupUnusedImages = async () => {
  try {
    const response = await axios.delete("http://127.0.0.1:8000/api/cleanup_unused_images/");
    console.log("Cleanup completed:", response.data.deleted);
  } catch (error) {
    console.error("Error cleaning up images:", error);
  }
};

onMounted(cleanupUnusedImages);
onMounted(fetchTrips);

const goToReport = () => {
  router.push("/report");
};

</script>

<template>
  <div class="container">
    <h1 style="display: inline-flex; align-items: center; gap: 10px;">
      <img src="../assets/travel-icon.png" alt="Travel Icon" style="height: 4em;">
    </h1>
    <div class="input-container">
      <input v-model="tripName" placeholder="Trip Name" />
      <button @click="addTrip">+ Add Trip</button>
      <button @click="goToReport" class="report-button">See Report</button>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    
    <div class="trips-grid">
      <button v-for="trip in trips" :key="trip.trip_id" class="trip-button" @click="router.push(`/trip/${trip.trip_id}`)">
        {{ trip.trip_name }}
      </button>
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
.input-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
}
input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
}
.error-message {
  color: red;
  font-size: 14px;
  margin-bottom: 10px;
}
.trips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}
.trip-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px;
  font-weight: bold;
  border-radius: 5px;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.3s;
}
.trip-button:hover {
  background-color: #0056b3;
}
.report-button {
  background-color: #ff9800;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  margin-left: 10px;
}
.report-button:hover {
  background-color: #e68900;
}

</style>
