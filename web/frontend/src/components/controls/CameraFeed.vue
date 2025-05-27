<template>
  <div class="card flex h-full flex-col">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-xl font-semibold">Camera Feed</h2>
    </div>
    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="border-muted-foreground bg-muted flex aspect-video w-full items-center justify-center rounded-lg border-2 border-dashed"
    >
      <div class="flex flex-col items-center gap-2">
        <LoaderCircleIcon class="text-muted-foreground animate-spin" />
        <p class="text-muted-foreground text-sm">Loading camera feed...</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      class="border-destructive bg-destructive/10 flex aspect-video w-full items-center justify-center rounded-lg border-2 border-dashed"
    >
      <div class="p-4 text-center">
        <svg
          class="text-destructive mx-auto mb-2 h-12 w-12"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.962-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
          />
        </svg>
        <p class="text-destructive mb-2 text-sm">{{ errorMessage }}</p>
        <button
          @click="reconnect"
          class="bg-destructive/10 text-destructive hover:bg-destructive/20 rounded px-3 py-1 text-xs transition-colors"
        >
          Retry Connection
        </button>
      </div>
    </div>

    <!-- Camera Feed -->
    <div v-else class="relative">
      <img
        ref="videoElement"
        :src="streamUrl"
        :alt="alt"
        class="border-accent aspect-video w-full rounded-lg border-2 border-dashed object-cover shadow-lg"
        @error="() => onImageError()"
        @loadstart="onLoadStart"
        @loadeddata="onImageLoad"
        @canplay="onImageLoad"
      />

      <!-- Connection Status Indicator -->
      <div
        class="bg-opacity-50 bg-background/80 absolute top-2 right-2 flex items-center space-x-1 rounded-full px-2 py-1"
      >
        <div
          :class="[
            'h-2 w-2 rounded-full',
            isConnected ? 'bg-green-400' : 'bg-destructive',
          ]"
        ></div>
        <span class="text-foreground text-xs">
          {{ isConnected ? "Live" : "Disconnected" }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LoaderCircleIcon } from "lucide-vue-next";
import { ref, onMounted, onUnmounted, computed } from "vue";

interface Props {
  serverUrl?: string;
  width?: number;
  height?: number;
  alt?: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  loadTimeout?: number;
}

const props = withDefaults(defineProps<Props>(), {
  serverUrl: "http://localhost:5000",
  width: 640,
  height: 480,
  alt: "Camera Feed",
  autoReconnect: true,
  reconnectInterval: 10000, // 10 seconds
  loadTimeout: 10000, // 10 seconds timeout for loading
});

const isLoading = ref(true);
const hasError = ref(false);
const isConnected = ref(false);
const errorMessage = ref("");
const videoElement = ref<HTMLImageElement>();
const reconnectTimer = ref<NodeJS.Timeout>();
const loadTimeoutTimer = ref<NodeJS.Timeout>();

const streamUrl = computed(() => `${props.serverUrl}/video`);

const clearLoadTimeout = () => {
  if (loadTimeoutTimer.value) {
    clearTimeout(loadTimeoutTimer.value);
    loadTimeoutTimer.value = undefined;
  }
};

const startLoadTimeout = () => {
  clearLoadTimeout();
  loadTimeoutTimer.value = setTimeout(() => {
    if (isLoading.value) {
      onImageError("Connection timeout");
    }
  }, props.loadTimeout);
};

const onLoadStart = () => {
  isLoading.value = true;
  hasError.value = false;
  startLoadTimeout();
};

const onImageLoad = () => {
  clearLoadTimeout();
  isLoading.value = false;
  hasError.value = false;
  isConnected.value = true;

  // Clear any existing reconnect timer since we're connected
  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value);
    reconnectTimer.value = undefined;
  }
};

const onImageError = (customMessage?: string) => {
  clearLoadTimeout();
  isLoading.value = false;
  hasError.value = true;
  isConnected.value = false;
  errorMessage.value = customMessage || "Failed to connect to camera feed";

  // Auto-reconnect if enabled
  if (props.autoReconnect && !reconnectTimer.value) {
    scheduleReconnect();
  }
};

const scheduleReconnect = () => {
  reconnectTimer.value = setTimeout(() => {
    reconnect();
  }, props.reconnectInterval);
};

const reconnect = () => {
  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value);
    reconnectTimer.value = undefined;
  }

  clearLoadTimeout();
  isLoading.value = true;
  hasError.value = false;

  // Force reload the image by updating the src with a cache-busting parameter
  if (videoElement.value) {
    const url = new URL(streamUrl.value);
    url.searchParams.set("t", Date.now().toString());
    videoElement.value.src = url.toString();
  }

  startLoadTimeout();
};

// Alternative approach: Check if stream is working by testing the endpoint
const testStreamConnection = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    const response = await fetch(streamUrl.value, {
      method: "HEAD",
      signal: controller.signal,
    }).finally(() => clearTimeout(timeoutId));

    if (response.ok) {
      // If HEAD request succeeds, the stream should work
      // Set a shorter timeout and assume success after a brief moment
      setTimeout(() => {
        if (isLoading.value && !hasError.value) {
          onImageLoad();
        }
      }, 2000); // Give it 2 seconds to start streaming
    } else {
      onImageError("Stream endpoint not available");
    }
  } catch (error) {
    onImageError("Cannot reach camera server");
  }
};

// Check connection status periodically
const checkConnection = () => {
  if (!hasError.value && isConnected.value) {
    // Ping the server to check if it's still available
    fetch(`${props.serverUrl}/`, { method: "HEAD" }).catch(() => {
      // If ping fails, trigger error state
      onImageError("Connection lost");
    });
  }
};

let connectionCheckInterval: NodeJS.Timeout;

onMounted(() => {
  // Test the stream connection first
  testStreamConnection();

  // Start periodic connection checks
  connectionCheckInterval = setInterval(checkConnection, 10000); // Check every 10 seconds
});

onUnmounted(() => {
  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value);
  }
  if (connectionCheckInterval) {
    clearInterval(connectionCheckInterval);
  }
  clearLoadTimeout();
});

// Expose methods for parent components
defineExpose({
  reconnect,
  isConnected: computed(() => isConnected.value),
  hasError: computed(() => hasError.value),
  isLoading: computed(() => isLoading.value),
});
</script>
