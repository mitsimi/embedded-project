<script setup lang="ts">
defineProps<{
  message?: string;
}>();

const emit = defineEmits<{
  (e: "retry"): void;
}>();

const handleRetry = () => {
  emit("retry");
};
</script>

<template>
  <div class="p-4 text-center">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="text-danger-500 mx-auto mb-4 h-12 w-12"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
      />
    </svg>
    <h3 class="text-danger-600 dark:text-danger-400 text-lg font-medium">
      Connection Error
    </h3>
    <p class="text-industrial-600 dark:text-industrial-300 mt-1">
      {{ message || "Unable to connect to the camera feed." }}
    </p>
    <Button @click="handleRetry">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="mr-2 h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
        />
      </svg>
      Try Again
    </Button>
  </div>
</template>
