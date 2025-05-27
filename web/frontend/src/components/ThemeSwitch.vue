<template>
  <ContextMenu>
    <ContextMenuTrigger asChild>
      <Button variant="ghost" size="icon" @click="toggleTheme">
        <span class="sr-only">Toggle Theme</span>
        <div class="flex flex-row items-center justify-center">
          <div class="">
            <span v-if="themeStore.theme === 'light'" class="theme-icon">
              <SunIcon />
            </span>
            <span v-else-if="themeStore.theme === 'dark'" class="theme-icon">
              <MoonIcon />
            </span>
            <span v-else>
              <SunMoonIcon />
            </span>
          </div>
        </div>
      </Button>
    </ContextMenuTrigger>

    <ContextMenuContent>
      <ContextMenuGroup>
        <ContextMenuItem
          value="light"
          @click="themeStore.changeTheme('light')"
          class="flex items-center justify-between"
        >
          <div class="flex items-center gap-2"><SunIcon /> Light</div>
          <CheckIcon v-if="themeStore.theme === 'light'" class="size-4" />
        </ContextMenuItem>
        <ContextMenuItem
          value="dark"
          @click="themeStore.changeTheme('dark')"
          class="flex items-center justify-between"
        >
          <div class="flex items-center gap-2"><MoonIcon /> Dark</div>
          <CheckIcon v-if="themeStore.theme === 'dark'" class="size-4" />
        </ContextMenuItem>
        <ContextMenuItem
          value="system"
          @click="themeStore.changeTheme('system')"
          class="flex items-center justify-between"
        >
          <div class="flex items-center gap-2"><SunMoonIcon /> System</div>
          <CheckIcon v-if="themeStore.theme === 'system'" class="size-4" />
        </ContextMenuItem>
      </ContextMenuGroup>
    </ContextMenuContent>
  </ContextMenu>
</template>

<script lang="ts" setup>
import { SunIcon, MoonIcon, SunMoonIcon } from "lucide-vue-next";
import { useThemeStore } from "@/stores/themeStore";
import ContextMenuGroup from "./ui/context-menu/ContextMenuGroup.vue";
import { CheckIcon } from "lucide-vue-next";

const themeStore = useThemeStore();

const toggleTheme = () => {
  const newTheme = themeStore.resolvedTheme === "light" ? "dark" : "light";
  themeStore.changeTheme(newTheme);
};
</script>
