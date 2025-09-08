<template>
  <v-menu open-on-hover location="bottom">
    <template v-slot:activator="{ props }">
      <v-btn
        v-bind="props"
        icon="mdi-translate"
        variant="text"
        tabindex="0"
      ></v-btn>
    </template>

    <v-list>
      <v-list-item
        v-for="lang in languages"
        :key="lang.code"
        :value="lang.code"
        @click="selectLanguage(lang.code)"
      >
        <v-list-item-title>{{ lang.name }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script lang="ts" setup>
import { useI18n } from "vue-i18n";
interface Language {
  name: string;
  code: string;
}

const { locale } = useI18n();

const languages: Language[] = [
  { name: "English", code: "en" },
  { name: "中文", code: "zh" },
];

const selectLanguage = (code: string) => {
  console.debug("Selected language:", code);
  locale.value = code;
  pywebview.api.setLanguageLocale(code);
};
</script>

<style scoped>
</style>
