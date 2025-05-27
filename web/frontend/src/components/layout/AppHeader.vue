<template>
  <header class="border-border bg-background border-b px-4 py-3 sm:p-4">
    <div
      class="container mx-auto flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center sm:gap-0"
    >
      <!-- Logo and title -->
      <div class="flex w-full items-center justify-between sm:justify-start">
        <div
          class="border-border bg-muted hover:border-ring hover:bg-accent mr-3 flex h-10 w-10 items-center justify-center border-2 transition-colors"
        >
          <span class="text-foreground text-xl font-bold">R</span>
        </div>
        <div class="flex flex-col items-end sm:items-start">
          <h1 class="text-foreground text-xl font-bold">Robotic Arm Control</h1>
          <span class="text-muted-foreground text-xs">
            v1.0.0 • Connected
          </span>
        </div>
      </div>

      <!-- Right side controls -->
      <div
        class="flex w-full items-center justify-between sm:w-auto sm:space-x-4"
      >
        <!-- Status indicator -->
        <div class="flex items-center space-x-2">
          <div class="bg-primary h-2 w-2 animate-pulse rounded-full"></div>
          <span class="text-muted-foreground text-sm"> Online </span>
        </div>

        <!-- Divider -->
        <div class="bg-border hidden h-6 w-px sm:block"></div>

        <!-- Theme toggle -->
        <ThemeSwitch />
      </div>
    </div>
  </header>
</template>
