import { createI18n } from "vue-i18n";
import { zh, en } from "@/assets/lang";

// Get the current language from the browser
const currentLanguage = navigator.language;
const defaultLocale = currentLanguage.includes("zh") ? "zh" : "en";

export default createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: "en",
  messages: {
    en,
    zh,
  },
});
