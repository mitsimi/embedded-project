<template>
  <div class="px-4 py-3">
    <main
      class="container mx-auto flex flex-grow flex-col gap-4 overflow-hidden lg:flex-row"
    >
      <!-- Control Panel (40% on desktop, full width on mobile) -->
      <ControlPanel
        class="order-2 mt-4 w-full md:mt-0 md:mr-4 lg:order-1 lg:w-3/5"
      />

      <!-- Camera Feed (60% on desktop, full width on mobile) -->
      <CameraFeed
        class="order-1 w-full lg:order-2 lg:w-2/5"
        ref="cameraFeedRef"
        :server-url="cameraServerUrl"
        :width="cameraWidth"
        :height="cameraHeight"
        :auto-reconnect="true"
        :reconnect-interval="3000"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import CameraFeed from "@/components/controls/CameraFeed.vue";

const cameraServerUrl = ref(`http://${window.location.hostname}:5000`); // Use current hostname
const cameraFeedRef = ref<InstanceType<typeof CameraFeed>>();

const cameraWidth = 612;
const cameraHeight = (612 / 16) * 9;
</script>
