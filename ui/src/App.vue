<template>
  <v-app>
    <v-layout class="rounded rounded-md">
      <v-main class="d-flex justify-center" style="min-height: 300px">
        <router-view></router-view>
      </v-main>
    </v-layout>
  </v-app>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTheme } from "vuetify";

import { getSystemTheme, setupThemeChangeListener } from "@/plugins";

const theme = useTheme();
onMounted(() => {
  // 主题设置 - 跟随系统主题
  theme.global.name.value = getSystemTheme();
  setupThemeChangeListener((sysTheme: string) => {
    theme.global.name.value = sysTheme;
  });
});
</script>

<style>
/* 隐藏浏览器自带的滚动条 */
body::-webkit-scrollbar {
  width: 0; /* 调整滚动条宽度 */
}

body::-webkit-scrollbar-track {
  background-color: transparent; /* 设置滚动条轨道背景色为透明 */
}

body::-webkit-scrollbar-thumb {
  /* 设置滚动条滑块颜色 */
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 0.25em; /* 设置滚动条滑块圆角 */
}
</style>
