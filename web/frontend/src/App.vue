<template>
  <div class="bg-background flex min-h-screen flex-col">
    <AppHeader />
    <main class="grow">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import { onMounted } from "vue";
import { useThemeStore } from "@/stores/themeStore";
import AppFooter from "./components/layout/AppFooter.vue";
const themeStore = useThemeStore();

onMounted(() => {
  // Initialize theme based on user preference
  themeStore.initTheme();
});
</script>
