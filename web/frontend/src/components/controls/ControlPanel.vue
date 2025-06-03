<script setup lang="ts">
import { useRobotStore } from "@/stores/robotStore";
import { CheckIcon, RefreshCcwIcon } from "lucide-vue-next";
import { computed } from "vue";

const robotStore = useRobotStore();
const motors = computed(() => robotStore.motors);

const resetAllMotors = () => {
  robotStore.resetAllMotors();
};

const setAllPositions = () => {
  motors.value.forEach((motor) => {
    robotStore.setMotorPosition(motor.id, motor.position);
  });
};
</script>

<template>
  <div class="card flex h-full flex-col">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="h-10 text-xl font-semibold">Motor Controls</h2>

      <div class="flex space-x-2">
        <!-- Set All button -->
        <Button variant="default" @click="setAllPositions" class="text-sm">
          <span class="flex items-center space-x-2">
            <CheckIcon />
            <span>Set All</span>
          </span>
        </Button>

        <!-- Reset All button -->
        <Button variant="secondary" @click="resetAllMotors" class="text-sm">
          <span class="flex items-center space-x-2">
            <RefreshCcwIcon />
            <span>Reset All</span>
          </span>
        </Button>
      </div>
    </div>

    <div
      class="grid flex-grow grid-cols-1 gap-4 overflow-y-auto lg:grid-cols-2"
    >
      <MotorControl
        v-for="motor in motors"
        :key="motor.id"
        :motor="motor"
        @update-position="robotStore.updateMotorPosition"
        @reset-motor="robotStore.resetMotor"
        @set-position="robotStore.setMotorPosition"
      />
    </div>
  </div>
</template>
