// Plugins
import Components from "unplugin-vue-components/vite";
import Vue from "@vitejs/plugin-vue";
import Vuetify, { transformAssetUrls } from "vite-plugin-vuetify";
// import ViteFonts from "unplugin-fonts/vite";

// Utilities
import { defineConfig } from "vite";
import { fileURLToPath, URL } from "node:url";
import path from "node:path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    Vue({
      template: { transformAssetUrls },
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
    Vuetify({ autoImport: true }),
    Components(),
    // ViteFonts({
    //   google: {
    //     families: [
    //       // {
    //       //   name: "Roboto",
    //       //   styles: "wght@100;300;400;500;700;900",
    //       // },
    //     ],
    //   },
    // }),
  ],
  define: { "process.env": {} },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
    extensions: [".js", ".json", ".jsx", ".mjs", ".ts", ".tsx", ".vue"],
  },
  server: {
    host: "0.0.0.0",
    port: 3000,
    fs: {
      strict: false,
      allow: [path.resolve(__dirname, "../dist")], 
    },
    watch: {
      usePolling: true,
    },
  },
  base: "./", 
  build: {
    emptyOutDir: true,
    outDir: "../static", 
    watch: {
      include: "src/**",
    },
    rollupOptions: {
      output: {
        assetFileNames: "[name].[ext]",
        chunkFileNames: "[name].js",
        entryFileNames: "[name].js",
      },
    },
  },
});
