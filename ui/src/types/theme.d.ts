declare interface ThemeItem {
  [key: string]: any;
  sensor: string;
  sensorLabel: string;
  attribute: string;
  attributeLabel: string;
  showType: string;
  // Optional properties
  showTypes?: string[];
  value?: any;
  uuid?: string;
  unit?: "kb/s" | "mb/s" | "%" | "GHz" | "℃" | "RPM" | "GB";
  units?: string[];
  showUnit?: boolean | undefined;
  dateFormat?: string; // for date show style
  timeFormat?: string; // for time show style
  segmentGap?: number; // for donut chart show style
  segmentWidth?: number; // for donut chart show style
}

declare interface ThemeGroup {
  icon?: string;
  label: string;
  items: ThemeItem[];
}

declare enum CanvasShape {
  Rect = "rect",
  Circle = "circle",
}

declare interface CanvasMeta {
  shape: CanvasShape;
  width: number;
  height: number;
  radius: number;
  canvasJSON?: any; // The json data of the fabricjs cavans
  customFonts?: { [fontFamily: string]: string } = {}; // Custom fonts, key is fontFamily, value is fontDataHex
}

declare interface SensorData extends Map<string, any> {
  [key: string]: any;
  beauty: Map<string, any>;
}

declare type CachedFunction<T extends (...args: any[]) => any> = {
  (this: ThisParameterType<T>, ...args: Parameters<T>): ReturnType<T>;
  clearCache: () => void;
};

declare type WeatherIconFilepathMap = {
  [key: string]: string;
};
