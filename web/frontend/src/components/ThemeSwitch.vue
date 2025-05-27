<template>
  <ContextMenu>
    <ContextMenuTrigger>
      <Button variant="ghost" size="icon">
        <span class="sr-only">Toggle Theme</span>
        <div class="flex flex-row items-center justify-center">
          <div class="">
            <span v-if="themeStore.theme === 'light'" class="theme-icon">
              <SunIcon />
            </span>
            <span v-else-if="themeStore.theme === 'dark'" class="theme-icon">
              <MoonIcon />
            </span>
            <span v-else class="size-8">
              <SunMoonIcon
                class="text-yellow-400/75 dark:text-neutral-300/50"
              />
            </span>
          </div>
        </div>
      </Button>
      <ContextMenuContent>
        <ContextMenuRadioGroup
          :model-value="themeStore.theme"
          @update:model-value="themeStore.changeTheme"
        >
          <ContextMenuRadioItem value="light">Light</ContextMenuRadioItem>
          <ContextMenuRadioItem value="dark">Dark</ContextMenuRadioItem>
          <ContextMenuRadioItem value="system">System</ContextMenuRadioItem>
        </ContextMenuRadioGroup>
      </ContextMenuContent>
    </ContextMenuTrigger>
  </ContextMenu>
</template>

<script lang="ts" setup>
import { SunIcon, MoonIcon, SunMoonIcon } from "lucide-vue-next";
import { useThemeStore } from "@/stores/themeStore";

const themeStore = useThemeStore();
</script>
