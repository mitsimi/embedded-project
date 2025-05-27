<template>
  <header>
    <div
      class="container mx-auto flex flex-col items-center justify-between sm:flex-row"
    >
      <!-- Logo and title -->
      <div class="mb-4 flex items-center sm:mb-0">
        <div class="mr-3 flex h-10 w-10 items-center justify-center">
          <span class="text-xl font-bold text-white">R</span>
        </div>
        <h1 class="text-xl font-bold">Robotic Arm Control</h1>
      </div>

      <div class="flex items-center space-x-4">
        <!-- Theme toggle -->
        <ThemeSwitch />
      </div>
    </div>
  </header>
</template>
