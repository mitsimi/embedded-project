import type { SystemStatus, Motor } from "@/types/robot";
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useRobotStore = defineStore("robot", () => {
  // System status
  const status = ref<SystemStatus>("online");

  // Motors array
  const motorsData = ref<Motor[]>([
    { id: 1, name: "Base", position: 90, defaultPosition: 90 },
    { id: 2, name: "Shoulder", position: 45, defaultPosition: 45 },
    { id: 3, name: "Elbow", position: 120, defaultPosition: 120 },
    { id: 4, name: "Wrist Pitch", position: 90, defaultPosition: 90 },
    { id: 5, name: "Wrist Roll", position: 0, defaultPosition: 0 },
    { id: 6, name: "Gripper", position: 60, defaultPosition: 60 },
  ]);

  // Computed property for system status
  const systemStatus = computed(() => status.value);

  // Computed property for motors
  const motors = computed(() => motorsData.value);

  // Update motor position (preview only)
  const updateMotorPosition = (motorId: number, position: number) => {
    const motorIndex = motorsData.value.findIndex(
      (motor) => motor.id === motorId,
    );
    if (motorIndex !== -1) {
      motorsData.value[motorIndex].position = position;
    }
  };

  // Set motor position (commit to robot)
  const setMotorPosition = (motorId: number, position: number) => {
    const motorIndex = motorsData.value.findIndex(
      (motor) => motor.id === motorId,
    );
    if (motorIndex !== -1) {
      // In a real implementation, this would send the command to the robot
      // and wait for confirmation before updating the UI
      motorsData.value[motorIndex].position = position;
    }
  };

  // Reset a single motor to default position
  const resetMotor = (motorId: number) => {
    const motorIndex = motorsData.value.findIndex(
      (motor) => motor.id === motorId,
    );
    if (motorIndex !== -1) {
      const defaultPosition = motorsData.value[motorIndex].defaultPosition;
      motorsData.value[motorIndex].position = defaultPosition;
    }
  };

  // Reset all motors to default positions
  const resetAllMotors = () => {
    motorsData.value.forEach((motor) => {
      motor.position = motor.defaultPosition;
    });
  };

  // Emergency stop function
  const emergencyStop = () => {
    // In a real implementation, this would send an immediate stop command
    // to the hardware and set the system to a safe state
    status.value = "offline";

    // Simulate system coming back online after a delay
    setTimeout(() => {
      status.value = "online";
    }, 3000);
  };

  return {
    systemStatus,
    motors,
    updateMotorPosition,
    setMotorPosition,
    resetMotor,
    resetAllMotors,
    emergencyStop,
  };
});
