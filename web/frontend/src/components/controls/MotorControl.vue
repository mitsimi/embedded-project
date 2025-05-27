<script setup lang="ts">
import type { Motor } from "@/types/robot";
import { ref, computed, watch } from "vue";

const props = defineProps<{
  motor: Motor;
}>();

const emit = defineEmits<{
  (e: "update-position", motorId: number, position: number): void;
  (e: "reset-motor", motorId: number): void;
  (e: "set-position", motorId: number, position: number): void;
}>();

const position = ref(props.motor.position);
const manualInput = ref(props.motor.position.toString());
const isLoading = ref(false);
const hasError = ref(false);

// Watch for prop changes
watch(
  () => props.motor.position,
  (newPosition) => {
    position.value = newPosition;
    manualInput.value = newPosition.toString();
  },
);

// Slider change handler
const handleSliderChange = (newPosition: number) => {
  position.value = newPosition;
  manualInput.value = newPosition.toString();
  updatePosition(newPosition);
};

// Input change handler
const handleInputChange = (event: Event) => {
  manualInput.value = (event.target as HTMLInputElement).value;
};

// Input blur handler
const handleInputBlur = () => {
  let newPosition = parseInt(manualInput.value, 10);

  // Validate position
  if (isNaN(newPosition)) {
    newPosition = props.motor.position;
    manualInput.value = newPosition.toString();
    return;
  }

  // Clamp value between 0 and 180
  newPosition = Math.max(0, Math.min(180, newPosition));
  position.value = newPosition;
  manualInput.value = newPosition.toString();
  updatePosition(newPosition);
};

// Reset motor
const resetMotor = () => {
  emit("reset-motor", props.motor.id);
};

// Set position
const setPosition = () => {
  isLoading.value = true;
  hasError.value = false;

  try {
    emit("set-position", props.motor.id, position.value);
    setTimeout(() => {
      isLoading.value = false;
    }, 500);
  } catch (error) {
    isLoading.value = false;
    hasError.value = true;
  }
};

// Update motor position
const updatePosition = (newPosition: number) => {
  isLoading.value = true;
  hasError.value = false;

  try {
    emit("update-position", props.motor.id, newPosition);
    isLoading.value = false;
  } catch (error) {
    isLoading.value = false;
    hasError.value = true;
  }
};

// Calculate position indicator left position
const positionIndicatorStyle = computed(() => {
  const percentage = (position.value / 180) * 100;
  return { left: `${percentage}%` };
});
</script>

<template>
  <div class="border p-4">
    <div class="mb-2 flex items-center justify-between">
      <div class="flex items-center">
        <h3 class="font-medium">{{ motor.name }}</h3>
      </div>
      <span class="text-xs">ID: {{ motor.id }}</span>
    </div>

    <!-- Current position display -->
    <div class="mb-3 flex items-center justify-between">
      <span class="text-sm">Current Position</span>
      <span class="font-medium">{{ position }}°</span>
    </div>

    <!-- Slider control -->
    <div class="relative mb-4">
      <div class="bg-foreground h-2 rounded-full"></div>
      <Slider
        type="range"
        :min="0"
        :max="180"
        :step="1"
        :model-value="[position]"
        @update:model-value="handleSliderChange"
        class="absolute top-0 left-0 h-2 w-full cursor-pointer px-0.5"
        :disabled="isLoading"
      />
      <!-- Slider tick marks -->
      <div class="mt-1 flex justify-between px-0.5">
        <span class="text-xs">0°</span>
        <span class="text-xs">90°</span>
        <span class="text-xs">180°</span>
      </div>
      <!-- Position indicator -->
      <!--div
        :style="positionIndicatorStyle"
        class="absolute top-0 size-4 -translate-1/2"
      >
        <CircleIcon fill="bg-foreground" />
      </div-->
    </div>

    <!-- Controls row -->
    <div class="flex space-x-2">
      <!-- Numeric input -->
      <div class="relative flex-grow">
        <Input
          type="number"
          min="0"
          max="180"
          :default-value="manualInput"
          :value="manualInput"
          @onUpdate="handleInputChange"
          @blur="handleInputBlur"
          class="input-field w-full pr-8"
          :disabled="isLoading"
        />
        <span class="absolute top-1/2 right-3 -translate-y-1/2 transform"
          >°</span
        >
      </div>

      <!-- Set button -->
      <Button @click="setPosition" :disabled="isLoading"> Set </Button>

      <!-- Reset button -->
      <Button variant="secondary" @click="resetMotor" :disabled="isLoading">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
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
      </Button>
    </div>

    <!-- Error message -->
    <div
      v-if="hasError"
      class="text-danger-600 dark:text-danger-400 mt-2 text-xs"
    >
      Failed to update position. Please try again.
    </div>
  </div>
</template>
