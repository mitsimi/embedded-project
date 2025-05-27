import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";

const pinia = createPinia();

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("./views/Dashboard.vue"),
    },
  ],
});

const app = createApp(App);
app.use(pinia);
app.use(router);
app.mount("#app");
