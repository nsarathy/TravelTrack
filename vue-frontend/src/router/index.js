import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import TripDetailView from '../views/TripDetailView.vue';
import ReportView from '../views/ReportView.vue';

const routes = [
  { path: '/', component: HomeView },
  { path: '/trip/:tripId', component: TripDetailView, props: true },
  { path: '/report', component: ReportView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
