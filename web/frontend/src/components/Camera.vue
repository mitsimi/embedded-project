<template>
  <img :src="'/video'" alt="Live camera feed" class="feed" />
</template>

<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({
  name: "Camera"
});
</script>

<style scoped>
.feed {
  display: block;
  max-width: 100%;
  margin: 0 auto;
  border: 2px solid #333;
}
</style>
