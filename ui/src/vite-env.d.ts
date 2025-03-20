/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare const pywebview: any;

declare interface FontFaceSet {
  add(font: FontFace): void;
}
