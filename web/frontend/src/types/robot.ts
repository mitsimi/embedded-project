// System status types
export type SystemStatus = "online" | "offline" | "warning" | "error";

// Motor interface
export interface Motor {
  id: number;
  name: string;
  position: number;
  defaultPosition: number;
  minPulse: number;
  maxPulse: number;
}

// Motor control command
export interface MotorCommand {
  motorId: number;
  position: number;
}

// System error
export interface SystemError {
  code: string;
  message: string;
  severity: "low" | "medium" | "high" | "critical";
  timestamp: Date;
}

// Camera settings
export interface CameraSettings {
  brightness: number;
  contrast: number;
  saturation: number;
  resolution: string;
  fps: number;
}
