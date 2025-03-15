<template>
  <v-container v-show="showPage" fluid>
    <div
      class="d-flex flex-wrap justify-center align-center"
      style="height: 100%"
    >
      <div class="align-self-stretch" style="flex-grow: 1">
        <v-card flat style="height: 100%">
          <v-card-subtitle>{{ t("label.Preview") }}</v-card-subtitle>
          <div v-if="screenSettings.lastTheme" class="d-flex align-center mb-2">
            <v-tooltip :text="t('label.ThemeName')" location="bottom">
              <template v-slot:activator="{ props }">
                <v-chip v-bind="props" color="primary">{{
                  screenSettings.lastTheme
                }}</v-chip>
              </template>
            </v-tooltip>
            <v-spacer></v-spacer>
            <v-tooltip
              v-if="themeMeta.shape == 'rect'"
              :text="t('label.ScreenSize')"
              location="bottom"
            >
              <template v-slot:activator="{ props }">
                <v-chip v-bind="props" color="primary">
                  {{ themeMeta.width }} X {{ themeMeta.height }}
                </v-chip>
              </template>
            </v-tooltip>
            <v-tooltip v-else :text="t('label.ScreenRadius')" location="bottom">
              <template v-slot:activator="{ props }">
                <v-chip v-bind="props" color="primary">{{
                  themeMeta.raduis
                }}</v-chip>
              </template>
            </v-tooltip>
          </div>
          <div class="canvasWrapper d-flex justify-center align-center">
            <canvas class="canvas" ref="canvasRef"></canvas>
          </div>
        </v-card>
      </div>
      <div
        class="align-self-stretch"
        style="max-width: 500px; min-width: 300px"
      >
        <v-card flat>
          <v-card-subtitle>{{ t("label.Setting") }}</v-card-subtitle>
          <v-form ref="settingForm" validate-on="lazy">
            <v-card-text>
              <v-select
                clearable
                density="compact"
                :label="t('label.Screen')"
                :items="screens"
                :loading="!monitorSettings.lastScreen"
                :rules="[formRuleRequire]"
                :no-data-text="t('label.NoScreen')"
                v-model="monitorSettings.lastScreen"
                @update:modelValue="selectScreen"
              >
                <template v-slot:prepend>
                  <v-tooltip :text="t('label.ClickToFlush')">
                    <template v-slot:activator="{ props }">
                      <v-chip
                        v-bind="props"
                        color="success"
                        @click="loadScreens"
                        >{{ screens.length }}</v-chip
                      >
                    </template>
                  </v-tooltip>
                </template>
                <template v-slot:append>
                  <LanguageBtn></LanguageBtn>
                </template>
              </v-select>
              <v-select
                clearable
                density="compact"
                :label="t('label.Theme')"
                :items="themes"
                :loading="!screenSettings.lastTheme"
                :rules="[formRuleRequire]"
                :no-data-text="t('label.NoTheme')"
                v-model="screenSettings.lastTheme"
                @update:modelValue="selectTheme"
              >
                <template v-slot:prepend>
                  <v-tooltip :text="t('label.ClickToFlush')">
                    <template v-slot:activator="{ props }">
                      <v-chip
                        v-bind="props"
                        color="success"
                        @click="loadThemes"
                        >{{ themes.length }}</v-chip
                      >
                    </template>
                  </v-tooltip>
                </template>
                <template v-slot:append>
                  <v-tooltip :text="t('label.ImportTheme')">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        class="ml-2"
                        v-bind="props"
                        size="x-small"
                        icon="mdi-plus"
                        color="primary"
                        flat
                        @click="importTheme"
                      ></v-btn>
                    </template>
                  </v-tooltip>
                </template>
              </v-select>
              <div class="text-caption">{{ t("label.Brightness") }}</div>
              <v-slider
                density="compact"
                prepend-icon="mdi-brightness-6"
                thumb-label="always"
                v-model.number="screenSettings.brightness"
                :disabled="!monitorSettings.lastScreen"
                :max="100"
                :min="10"
                :step="10"
                @update:modelValue="setScreenSettings()"
              ></v-slider>
              <div class="text-caption">{{ t("label.Rotation") }}</div>
              <v-slider
                density="compact"
                prepend-icon="mdi-screen-rotation"
                thumb-label="always"
                v-model.number="screenSettings.rotation"
                :disabled="!monitorSettings.lastScreen"
                :max="270"
                :min="0"
                :step="90"
                @update:modelValue="setScreenSettings()"
              >
                <template v-slot:thumb-label="{ modelValue }">
                  {{ `${modelValue}°` }}
                </template>
              </v-slider>
              <div class="text-caption">{{ t("label.Other") }}</div>
              <div>
                <v-text-field
                  variant="outlined"
                  class="my-2"
                  :label="t('label.Weather') + ' APIKey'"
                  type="text"
                  density="compact"
                  hide-details
                  v-model="monitorSettings.weather.apiKey"
                  @blur="setMonitorSettings()"
                  @keydown.enter="setMonitorSettings()"
                >
                  <template v-slot:append>
                    <v-tooltip location="left">
                      <template v-slot:activator="{ props }">
                        <v-icon
                          class="cursor-pointer"
                          v-bind="props"
                          icon="mdi-help-circle-outline"
                          @click="toOpenWeatherOrg"
                        ></v-icon>
                      </template>
                      {{ t("label.GetYourOwnAPIKey") }}
                    </v-tooltip>
                  </template>
                </v-text-field>
              </div>
              <div class="d-flex" style="width: 100%">
                <v-text-field
                  variant="outlined"
                  class="my-2"
                  max-width="120"
                  :label="t('label.Lat')"
                  type="number"
                  density="compact"
                  hide-details
                  v-model.number="monitorSettings.weather.lat"
                  :min="-90"
                  :max="90"
                  :step="0.0001"
                  @blur="setMonitorSettings()"
                  @keydown.enter="setMonitorSettings()"
                ></v-text-field>
                <v-text-field
                  variant="outlined"
                  class="my-2 ml-2"
                  max-width="120"
                  :label="t('label.Lon')"
                  type="number"
                  density="compact"
                  hide-details
                  v-model.number="monitorSettings.weather.lon"
                  :min="-180"
                  :max="180"
                  :step="0.0001"
                  @blur="setMonitorSettings()"
                  @keydown.enter="setMonitorSettings()"
                ></v-text-field>
              </div>
              <div class="d-flex">
                <v-switch
                  inset
                  density="compact"
                  class="my-2"
                  :label="t('label.AutoStartup')"
                  v-model="monitorSettings.startup"
                  base-color="secondary"
                  color="success"
                  @update:modelValue="setMonitorSettings()"
                ></v-switch>
              </div>
              <v-btn
                class="ma-2"
                block
                size="large"
                :loading="displayStateUpdating"
                :color="displayState ? 'warning' : 'success'"
                :disabled="
                  !monitorSettings.lastScreen ||
                  !screenSettings.lastTheme ||
                  screens.length == 0 ||
                  themes.length == 0 ||
                  displayStateUpdating
                "
                @click="toggleDisplay()"
                >{{
                  displayState
                    ? t("label.StopDisplay")
                    : t("label.StartDisplay")
                }}</v-btn
              >
            </v-card-text>
          </v-form>
        </v-card>
      </div>
    </div>
  </v-container>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import { throttle } from "@/plugins/utils";
import { ThemePlayer } from "@/model/themePlayer.m";
import { DEFAULT_CANVAS_META } from "@/consts/theme.c";
import LanguageBtn from "@/components/LanguageBtn.vue";
const { t, locale } = useI18n();
const showPage = ref(false);
const settingForm = ref();
const displayStateUpdating = ref(false);
const canvasRef = ref<HTMLCanvasElement | null>(null);
const player = ref<ThemePlayer | null>(null);
const formRuleRequire = (v: any) => !!v || t("msg.Required");
const screens = reactive<string[]>([]);
const themes = reactive<string[]>([]);
const themeMeta = reactive<{ [key: string]: any }>({});
const sensors = ref<string[]>([]);
const monitorSettings = reactive({
  lang: "",
  lastScreen: "",
  startup: false,
  weather: {
    apiKey: "5796abbde9106b7da4febfae8c44c232",
    lat: 0,
    lon: 0,
  },
});
const screenSettings = reactive({
  rotation: 0,
  brightness: 100,
  lastTheme: "",
});
const displayState = ref(false);

const loadScreens = () => {
  pywebview.api.loadScreens().then((res: any) => {
    screens.length = 0;
    screens.push(...res);
    if (screens.length == 0) {
      monitorSettings.lastScreen = "";
    }
  });
};

const loadThemes = () => {
  pywebview.api.loadThemes().then((res: any) => {
    themes.length = 0;
    themes.push(...res);
    if (themes.length == 0) {
      screenSettings.lastTheme = "";
    }
  });
};

const importTheme = throttle(() => {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".json";
  input.onchange = (event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      const file = target.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result) {
          const themeContent = reader.result as string;
          const cavansDom = document.createElement("canvas");
          try {
            // validate theme by theme player
            const tempPlayer = new ThemePlayer(cavansDom, {
              ...DEFAULT_CANVAS_META,
            });
            tempPlayer.fromThemeFileContent(themeContent);
            pywebview.api.importTheme(themeContent, file.name).then(loadThemes);
            tempPlayer.canvas.dispose();
          } catch {
            pywebview.api.showerror(t("msg.InvalidThemeFile"));
          } finally {
            cavansDom.remove();
            input.remove();
          }
        }
      };
      reader.readAsText(file);
    }
  };
  input.click();
}, 1000);

const selectScreen = (screen: string) => {
  if (!screen) {
    screen = "";
    stopDisplay();
  }
  pywebview.api.selectScreen(screen).then((success: boolean) => {
    if (success && screen) {
      // Get the screen settings
      pywebview.api.getScreenSettings(screen).then((res: any) => {
        screenSettings.brightness = res.brightness || 100;
        screenSettings.rotation = res.rotation || 0;
        screenSettings.lastTheme = res.lastTheme || "";
        // If the last theme is in the theme list, select it
        if (themes.includes(screenSettings.lastTheme)) {
          selectTheme(screenSettings.lastTheme);
        } else {
          selectTheme("");
        }
      });
    } else {
      monitorSettings.lastScreen = "";
    }
  });
};

const selectTheme = (theme: string) => {
  if (theme == null) {
    theme = "";
    player.value!.canvas.clear();
    stopDisplay();
  }
  pywebview.api.selectTheme(theme).then((content: string) => {
    if (content) {
      try {
        player.value!.fromThemeFileContent(content);
        sensors.value.length = 0;
        sensors.value.push(...player.value!.themeSensors());
        pywebview.api.getSensorsValue(sensors.value).then((res: any) => {
          player.value!.loadSensorsValue(res);
        });
        Object.assign(themeMeta, player.value!.meta);
      } catch (e) {
        console.error(e);
        pywebview.api.showerror(t("msg.InvalidThemeFile"));
        selectTheme("");
      }
    }
  });
};

const toOpenWeatherOrg = () => {
  window.open("https://openweathermap.org/price#freeaccess", "_blank");
};

const setScreenSettings = () => {
  if (monitorSettings.lastScreen) {
    pywebview.api.setScreenSettings(monitorSettings.lastScreen, screenSettings);
  }
};

const setMonitorSettings = () => {
  pywebview.api.setMonitorSettings(monitorSettings);
};

const toggleDisplay = () => {
  displayStateUpdating.value = true;
  displayState.value = !displayState.value;
  pywebview.api.toggleDisplay(displayState.value).finally(() => {
    displayStateUpdating.value = false;
  });
};

const stopDisplay = () => {
  // Only when the display is on, stop it
  if (displayState.value) {
    toggleDisplay();
  }
};

let themePreviewT: any = null;

const startThemePreview = () => {
  themePreviewT = setInterval(() => {
    if (
      !player.value ||
      !monitorSettings.lastScreen ||
      !screenSettings.lastTheme ||
      sensors.value.length == 0
    ) {
      return;
    }
    pywebview.api.getSensorsValue(sensors.value).then((res: any) => {
      player.value!.loadSensorsValue(res);
    });
  }, 1000);
};

const stopThemePreview = () => {
  if (themePreviewT) {
    clearInterval(themePreviewT);
    themePreviewT = null;
  }
};

declare global {
  interface Window {
    flushDisplay: (display: 0 | 1) => void;
  }
}

onMounted(() => {
  if (canvasRef.value) {
    player.value = new ThemePlayer(canvasRef.value, DEFAULT_CANVAS_META);
    window.flushDisplay = (display: 0 | 1) => {
      displayState.value = display === 1;
    };
  }
});

onUnmounted(() => {
  stopThemePreview();
});

window.addEventListener("pywebviewready", function () {
  loadScreens();
  loadThemes();
  setTimeout(() => {
    // Get the monitor settings
    pywebview.api
      .getMonitorSettings()
      .then((res: any) => {
        monitorSettings.lang = res.lang || "";
        monitorSettings.startup = res.startup || false;
        monitorSettings.lastScreen = res.lastScreen || "";
        res.weather = res.weather || {
          apiKey: "5796abbde9106b7da4febfae8c44c232",
          lat: 0,
          lon: 0,
        };
        Object.assign(monitorSettings.weather, res.weather);
        // If the last screen is in the screens list, select it
        if (screens.includes(monitorSettings.lastScreen)) {
          selectScreen(monitorSettings.lastScreen);
        } else {
          selectScreen("");
        }
        if (monitorSettings.lang) {
          locale.value = monitorSettings.lang;
        }
        displayState.value = res.displayState || false;
        // Start theme preview interval
        // startThemePreview();
      })
      .finally(() => {
        // Show the ready page
        showPage.value = true;
      });
  }, 100);

  // window.addEventListener("visibilitychange", () => {
  //   if (document.visibilityState === "visible") {
  //     startThemePreview();
  //   } else {
  //     stopThemePreview();
  //   }
  // });
});
</script>

<style scoped>
.canvasWrapper {
  width: 100%;
  height: auto;
  padding: 20px;
  background-color: rgba(109, 106, 106, 0.103);
  position: relative !important;
  pointer-events: auto;
  z-index: 1000;
  overflow: auto;
}
</style>
