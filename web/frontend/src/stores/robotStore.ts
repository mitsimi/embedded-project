import type { SystemStatus, Motor } from "@/types/robot";
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { mqttService } from "@/services/mqtt";

export const useRobotStore = defineStore("robot", () => {
  // System status
  const status = ref<SystemStatus>("offline");

  // Motors array
  const motorsData = ref<Motor[]>([
    {
      id: 0,
      name: "Gripper",
      position: 100,
      minPulse: 100,
      maxPulse: 380,
      defaultPosition: 100,
    },
    {
      id: 1,
      name: "Gripper Arm",
      position: 320,
      minPulse: 100,
      maxPulse: 500,
      defaultPosition: 320,
    },
    {
      id: 2,
      name: "Upper Arm",
      position: 100,
      minPulse: 100,
      maxPulse: 470,
      defaultPosition: 100,
    },
    {
      id: 3,
      name: "Middle Arm",
      position: 100,
      minPulse: 100,
      maxPulse: 520,
      defaultPosition: 100,
    },
    {
      id: 4,
      name: "Lower Arm",
      position: 350,
      minPulse: 220,
      maxPulse: 480,
      defaultPosition: 350,
    },
    {
      id: 6,
      name: "Stepper",
      position: 0,
      minPulse: 0,
      maxPulse: 650,
      defaultPosition: 0,
    },
  ]);

  // Computed property for system status
  const systemStatus = computed(() => status.value);

  // Computed property for motors
  const motors = computed(() => motorsData.value);

  // Initialize MQTT connection
  const initializeMQTT = async () => {
    try {
      await mqttService.connect();
      status.value = "online";
    } catch (error) {
      console.error("Failed to connect to MQTT broker:", error);
      status.value = "error";
    }
  };

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
      // Update the UI
      motorsData.value[motorIndex].position = position;

      // Publish the new position to MQTT
      mqttService.publishMotorPosition(motorId, position);
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
      mqttService.publishMotorPosition(motorId, defaultPosition);
    }
  };

  // Reset all motors to default positions
  const resetAllMotors = () => {
    motorsData.value.forEach((motor) => {
      motor.position = motor.defaultPosition;
      mqttService.publishMotorPosition(motor.id, motor.defaultPosition);
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

  // Initialize MQTT connection when the store is created
  initializeMQTT();

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
