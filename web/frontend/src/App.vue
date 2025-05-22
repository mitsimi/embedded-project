<template>
  <div id="app">
    <h1>Pi Camera Demo</h1>
    <Camera />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Camera from "./components/Camera.vue";

export default defineComponent({
  name: "App",
  components: { Camera }
});
</script>

<style>
#app {
  text-align: center;
  margin-top: 2rem;
  font-family: Avenir, Helvetica, Arial, sans-serif;
}
</style>
