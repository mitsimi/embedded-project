<template>
  <footer class="border-border bg-background border-t p-4">
    <div class="container mx-auto">
      <div
        class="flex flex-col items-center justify-between space-y-2 sm:flex-row sm:space-y-0"
      >
        <!-- Left side - Copyright/Info -->
        <div class="flex items-center space-x-4">
          <span class="text-muted-foreground text-sm">
            © 2025 Robotic Arm Control
          </span>
          <div class="bg-border h-4 w-px"></div>
          <span class="text-muted-foreground text-xs"> Build 1.0.0-beta </span>
        </div>

        <!-- Right side - Status/Links -->
        <div class="flex items-center space-x-4">
          <!-- System status -->
          <div class="flex items-center space-x-2">
            <span class="text-muted-foreground text-xs">System:</span>
            <span class="text-foreground text-xs">Ready</span>
          </div>

          <div class="bg-border h-4 w-px"></div>

          <!-- Connection info -->
          <div class="flex items-center space-x-2">
            <span class="text-muted-foreground text-xs">Port:</span>
            <span class="text-foreground text-xs">COM3</span>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
