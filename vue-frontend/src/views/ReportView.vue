<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { Pie } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
} from "chart.js";

ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale);

const router = useRouter();
const trips = ref([]);
const locations = ref([]);
const categories = ref([]);

const selectedTrip = ref("");
const selectedLocation = ref("");
const selectedCategory = ref("");
const startDate = ref("");
const endDate = ref("");

const summary = ref(null);
const categoryPieData = ref(null);
const locationPieData = ref(null);
const errorMessage = ref("");
const tripNameToID = {};
const secondarySummary = ref(null);

const peoplePhotos = ref([]);
const memoryPhotos = ref([]);

// Utility: Generate distinct light pastel colors (non-repeating)
const generateLightColors = (n) => {
  const hueStep = 360 / n;
  return Array.from({ length: n }, (_, i) => {
    const hue = Math.round(i * hueStep);
    return `hsl(${hue}, 75%, 75%)`;
  });
};

const fetchFilters = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/trips/");
    trips.value = ["---", ...res.data.map((trip) => trip.trip_name)];
    res.data.forEach((trip) => {
      tripNameToID[trip.trip_name] = trip.trip_id;
    });
  } catch (e) {
    console.error("Error fetching trips:", e);
  }

  try {
    const res = await axios.get("http://127.0.0.1:8000/api/locations/");
    locations.value = ["---", ...res.data.map((loc) => loc.location)];
  } catch (e) {
    console.error("Error fetching locations:", e);
  }

  try {
    const res = await axios.get("http://127.0.0.1:8000/api/categories/");
    categories.value = ["---", ...res.data.map((cat) => cat.category)];
  } catch (e) {
    console.error("Error fetching categories:", e);
  }
};

const fetchReport = async () => {
  errorMessage.value = "";
  if (selectedTrip.value !== "---") {
    selectedTrip.value = selectedTrip.value;
  } else {
    selectedTrip.value = undefined;
  }
  const params = {
    trip_id:
      selectedTrip.value !== "---"
        ? tripNameToID[selectedTrip.value]
        : undefined,
    location:
      selectedLocation.value !== "---" ? selectedLocation.value : undefined,
    category:
      selectedCategory.value !== "---" ? selectedCategory.value : undefined,
    start_date: startDate.value || undefined,
    end_date: endDate.value || undefined,
  };

  try {
    const [summaryRes, categoryPieRes, locationPieRes, secondaryRes] =
      await Promise.all([
        axios.get("http://127.0.0.1:8000/api/report/summary/", { params }),
        axios.get("http://127.0.0.1:8000/api/report/category-pie/", { params }),
        axios.get("http://127.0.0.1:8000/api/report/location-pie/", { params }),
        axios.get("http://127.0.0.1:8000/api/report/secondary-summary/", {
          params,
        }),
      ]);

    summary.value = summaryRes.data;
    secondarySummary.value = secondaryRes.data;

    // Prepare category pie chart
    const categoryLabels = categoryPieRes.data.map((d) => d.category);
    const categoryValues = categoryPieRes.data.map((d) => d.total);
    const categoryColors = generateLightColors(categoryLabels.length);
    categoryPieData.value = {
      labels: categoryLabels,
      datasets: [{ data: categoryValues, backgroundColor: categoryColors }],
    };

    // Prepare location pie chart
    const locationLabels = locationPieRes.data.map((d) => d.location);
    const locationValues = locationPieRes.data.map((d) => d.total);
    const locationColors = generateLightColors(locationLabels.length);
    locationPieData.value = {
      labels: locationLabels,
      datasets: [{ data: locationValues, backgroundColor: locationColors }],
    };

    // Inside fetchReport
    const [peoplePhotoRes, memoryPhotoRes] = await Promise.all([
      axios.get("http://127.0.0.1:8000/api/report/people-photos/", { params }),
      axios.get("http://127.0.0.1:8000/api/report/memory-photos/", { params }),
    ]);
    peoplePhotos.value = peoplePhotoRes.data.photos || [];
    memoryPhotos.value = memoryPhotoRes.data.photos || [];
    const baseURL = "http://127.0.0.1:8000/media/";

    peoplePhotos.value = (peoplePhotoRes.data.photos || []).map(
      (src) => baseURL + src
    );
    memoryPhotos.value = (memoryPhotoRes.data.photos || []).map(
      (src) => baseURL + src
    );
  } catch (e) {
    console.error("Error fetching report:", e);
    errorMessage.value = "Failed to load report. Please try again.";
  }
};

const goBack = () => router.push("/");

onMounted(fetchFilters);
</script>

<template>
  <div class="container">
    <button class="goback-button" @click="goBack">⬅️ Go Back</button>
    <h1>📊 Trip Expense Report</h1>

    <!-- Filter Section -->
    <div class="filters">
      <label>Trip:</label>
      <select v-model="selectedTrip">
        <option v-for="trip in trips" :key="trip" :value="trip">
          {{ trip === "---" ? "All Trips" : `${trip}` }}
        </option>
      </select>

      <label>Location:</label>
      <select v-model="selectedLocation">
        <option v-for="location in locations" :key="location" :value="location">
          {{ location === "---" ? "All Locations" : location }}
        </option>
      </select>

      <label>Category:</label>
      <select v-model="selectedCategory">
        <option
          v-for="category in categories"
          :key="category"
          :value="category"
        >
          {{ category === "---" ? "All Categories" : category }}
        </option>
      </select>

      <label>Date Range:</label>
      <input type="date" v-model="startDate" />
      <input type="date" v-model="endDate" />

      <button @click="fetchReport">Generate Report</button>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <!-- Report Results -->

    <div v-if="summary">
      <h2>📌 Summary</h2>
      <table class="summary-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Total Expense</strong></td>
            <td>${{ summary.total_expense }}</td>
          </tr>
          <tr>
            <td><strong># of Expenses</strong></td>
            <td>{{ summary.number_of_expenses }}</td>
          </tr>
          <tr>
            <td><strong>Average Expense</strong></td>
            <td>${{ summary.average_expense }}</td>
          </tr>
          <tr>
            <td><strong>Highest Expense</strong></td>
            <td>${{ summary.max_expense }}</td>
          </tr>
          <tr>
            <td><strong>Lowest Expense</strong></td>
            <td>${{ summary.min_expense }}</td>
          </tr>
          <tr>
            <td><strong>Last Date</strong></td>
            <td>{{ summary.last_date || "N/A" }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="charts">
      <div v-if="categoryPieData">
        <h3>🛍 Expense by Category</h3>
        <Pie :data="categoryPieData" />
      </div>
      <div v-if="locationPieData">
        <h3>📍 Expense by Location</h3>
        <Pie :data="locationPieData" />
      </div>
    </div>
    <div v-if="secondarySummary">
      <h2>📍 Additional Insights</h2>
      <table class="summary-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong># of People Met</strong></td>
            <td>{{ secondarySummary.people_met }}</td>
          </tr>
          <tr>
            <td><strong># of Locations Visited</strong></td>
            <td>{{ secondarySummary.locations_visited }}</td>
          </tr>
          <tr>
            <td><strong># of Memories</strong></td>
            <td>{{ secondarySummary.memories }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="peoplePhotos.length || memoryPhotos.length">
      <h2>📸 People & Memories</h2>
      <div class="collage">
        <img
          v-for="src in [...peoplePhotos, ...memoryPhotos]"
          :src="src"
          :key="src"
          class="collage-img"
        />
      </div>
    </div>
  </div>
</template>

<style>
.container {
  text-align: center;
  max-width: 1200px;
  margin: auto;
  font-family: Arial, sans-serif;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}
select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.error-message {
  color: red;
  font-weight: bold;
}

.summary-table {
  margin: 20px auto;
  border-collapse: collapse;
  width: 60%;
  font-size: 16px;
}
.summary-table td {
  border: 1px solid #ddd;
  padding: 8px;
}
.summary-table tr:nth-child(even) {
  background-color: #f9f9f9;
}
.summary-table tr:hover {
  background-color: #f1f1f1;
}
.charts {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 40px;
  flex-wrap: wrap;
}

.collage {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}
.collage-img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ccc;
}
</style>
