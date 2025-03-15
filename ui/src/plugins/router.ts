import { createRouter, createWebHashHistory, RouteRecordRaw } from "vue-router";
import HWMonitor from "@/pages/HWMonitor.vue";
import ThemePlayer from "@/pages/ThemePlayer.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/hwmonitor",
    name: "HWMonitor",
    component: HWMonitor,
  },
  {
    path: "/themeplayer",
    name: "ThemePlayer",
    component: ThemePlayer,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
