<script setup lang="ts">
import type { Motor } from "@/types/robot";
import { RefreshCcwIcon } from "lucide-vue-next";
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
const isLoading = ref(false);
const hasError = ref(false);

// Watch for prop changes
watch(
  () => props.motor.position,
  (newPosition) => {
    position.value = newPosition;
  },
);

// Slider change handler
const handleSliderChange = (newPosition: number) => {
  position.value = newPosition;
  updatePosition(newPosition);
};

// Input blur handler
const handleInputBlur = (event: Event) => {
  const input = event.target as HTMLInputElement;
  let newPosition = parseInt(input.value, 10);

  // Validate position
  if (isNaN(newPosition)) {
    input.value = position.value.toString();
    return;
  }

  // Clamp value between min and max pulse
  newPosition = Math.max(
    props.motor.minPulse,
    Math.min(props.motor.maxPulse, newPosition),
  );
  position.value = newPosition;
  input.value = newPosition.toString();
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
  const percentage = (position.value / props.motor.maxPulse) * 100;
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
      <span class="font-medium">{{ position.toString() }}</span>
    </div>

    <!-- Slider control -->
    <div class="relative mb-4">
      <div class="bg-foreground h-2 rounded-full"></div>
      <Slider
        type="range"
        :min="props.motor.minPulse"
        :max="props.motor.maxPulse"
        :step="1"
        :model-value="[position]"
        @update:model-value="handleSliderChange"
        class="absolute top-0 left-0 h-2 w-full cursor-pointer px-0.5"
        :disabled="isLoading"
      />
      <!-- Slider tick marks -->
      <div class="mt-1 flex justify-between px-0.5">
        <span class="text-xs">{{ props.motor.minPulse }}</span>
        <span class="text-xs">{{
          (props.motor.maxPulse + props.motor.minPulse) / 2
        }}</span>
        <span class="text-xs">{{ props.motor.maxPulse }}</span>
      </div>
      <!-- Position indicator -->
    </div>

    <!-- Controls row -->
    <div class="flex space-x-2">
      <!-- Numeric input -->
      <div class="relative flex-grow">
        <Input
          type="number"
          :min="props.motor.minPulse"
          :max="props.motor.maxPulse"
          @blur="handleInputBlur"
          class="input-field w-full pr-8"
          :disabled="isLoading"
        />
      </div>

      <!-- Set button -->
      <Button @click="setPosition" :disabled="isLoading"> Set </Button>

      <!-- Reset button -->
      <Button variant="secondary" @click="resetMotor" :disabled="isLoading">
        <RefreshCcwIcon />
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
