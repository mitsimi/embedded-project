<template>
  <div>
    <CameraFeed
      ref="cameraFeedRef"
      :server-url="cameraServerUrl"
      :width="640"
      :height="480"
      :auto-reconnect="true"
      :reconnect-interval="3000"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import CameraFeed from "@/components/CameraFeed.vue";

const cameraServerUrl = ref("http://localhost:5000"); // Adjust to your server URL
const cameraFeedRef = ref<InstanceType<typeof CameraFeed>>();
</script>
