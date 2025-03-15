<template>
  <canvas class="pywebview-drag-region" ref="canvasRef"></canvas>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ThemePlayer } from "@/model/themePlayer.m";
import { DEFAULT_CANVAS_META } from "@/consts/theme.c";

const canvasRef = ref<HTMLCanvasElement | null>(null);
const player = ref<ThemePlayer | null>(null);
const sensors = ref<string[]>([]);

declare global {
  interface Window {
    loadTheme: (theme: string) => void;
    playerToImageSrc: () => string;
  }
}
const loadTheme = (theme: string) => {
  pywebview.api.loadTheme(theme).then((content: string) => {
    if (!player.value || !content) {
      return;
    }
    player.value!.fromThemeFileContent(content);
    sensors.value.length = 0;
    sensors.value.push(...player.value!.themeSensors());
    pywebview.api.loadSensorsValue(sensors.value).then((res: any) => {
      player.value!.loadSensorsValue(res);
    });
    console.log("Load theme:", theme);
  });
};

const playerToImageSrc = () => {
  pywebview.api.loadSensorsValue(sensors.value).then((res: any) => {
    player.value!.loadSensorsValue(res);
  });
  return player.value!.toImageSrc();
};

onMounted(() => {
  if (canvasRef.value) {
    player.value = new ThemePlayer(canvasRef.value, DEFAULT_CANVAS_META, true);
  }
});

window.addEventListener("pywebviewready", function () {
  // expose methods for backend app
  window.loadTheme = loadTheme;
  window.playerToImageSrc = playerToImageSrc;
});
</script>

<style scoped></style>
