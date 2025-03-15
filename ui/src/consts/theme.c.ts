const CPUBaseItem = {
  sensor: "cpu",
  sensorLabel: "CPU",
};

const GPUBaseItem = {
  sensor: "gpu",
  sensorLabel: "GPU",
};

const RAMBaseItem = {
  sensor: "ram",
  sensorLabel: "RAM",
};

const DISKBaseItem = {
  sensor: "disk",
  sensorLabel: "Disk",
};

const LoadBaseItem = {
  attribute: "load",
  attributeLabel: "Load",
  showType: "Text",
  showTypes: ["Text", "BarChart", "DonutChart"],
  value: 0.5,
  unit: "%",
  showUnit: true,
};

const FrequencyBaseItem = {
  attribute: "frequency",
  attributeLabel: "Frequency",
  showType: "Text",
  value: 1.23,
  unit: "GHz",
  showUnit: true,
};

const TemperatureBaseItem = {
  attribute: "temperature",
  attributeLabel: "Temperature",
  showType: "Text",
  value: 45,
  unit: "°C",
  showUnit: true,
};

const FanSpeedBaseItem = {
  attribute: "fan",
  attributeLabel: "FanSpeed",
  showType: "Text",
  value: 1300,
  unit: "RPM",
  showUnit: true,
};

const CPU_THEME_ITEMS = [
  { ...CPUBaseItem, ...LoadBaseItem },
  { ...CPUBaseItem, ...FrequencyBaseItem },
  { ...CPUBaseItem, ...TemperatureBaseItem },
  { ...CPUBaseItem, ...FanSpeedBaseItem },
];
const GPU_THEME_ITEMS = [
  { ...GPUBaseItem, ...LoadBaseItem },
  { ...GPUBaseItem, ...FrequencyBaseItem },
  { ...GPUBaseItem, ...TemperatureBaseItem },
  { ...GPUBaseItem, ...FanSpeedBaseItem },
  {
    ...GPUBaseItem,
    attribute: "total",
    attributeLabel: "TotalVRAM",
    showType: "Text",
    value: 6,
    unit: "GB",
    showUnit: true,
  },
  {
    ...GPUBaseItem,
    attribute: "used",
    attributeLabel: "UsedVRAM",
    showType: "Text",
    value: 0.6,
    unit: "GB",
    showUnit: true,
  },
  {
    ...GPUBaseItem,
    attribute: "free",
    attributeLabel: "FreeVRAM",
    showType: "Text",
    value: 5.4,
    unit: "GB",
    showUnit: true,
  },
];
const RAM_THEME_ITEMS = [
  { ...RAMBaseItem, ...LoadBaseItem },
  {
    ...RAMBaseItem,
    attribute: "free",
    attributeLabel: "FreeRAM",
    showType: "Text",
    value: 6.6,
    unit: "GB",
    showUnit: true,
  },
  {
    ...RAMBaseItem,
    attribute: "used",
    attributeLabel: "UsedRAM",
    showType: "Text",
    value: 9.4,
    unit: "GB",
    showUnit: true,
  },
  {
    ...RAMBaseItem,
    attribute: "total",
    attributeLabel: "TotalRAM",
    showType: "Text",
    value: 16,
    unit: "GB",
    showUnit: true,
  },
];
const DISK_THEME_ITMES = [
  { ...DISKBaseItem, ...LoadBaseItem },
  {
    ...DISKBaseItem,
    attribute: "free",
    attributeLabel: "FreeStorage",
    showType: "Text",
    value: 176.2,
    unit: "GB",
    showUnit: true,
  },
  {
    ...DISKBaseItem,
    attribute: "used",
    attributeLabel: "UsedStorage",
    showType: "Text",
    value: 299.8,
    unit: "GB",
    showUnit: true,
  },
  {
    ...DISKBaseItem,
    attribute: "total",
    attributeLabel: "TotalStorage",
    showType: "Text",
    value: 476,
    unit: "GB",
    showUnit: true,
  },
];
const NET_THEME_ITEMS = [
  {
    sensor: "net",
    sensorLabel: "NET",
    attribute: "upload_speed",
    attributeLabel: "UploadSpeed",
    showType: "Text",
    value: 183870,
    unit: "kb/s",
    units: ["kb/s", "mb/s"],
    showUnit: true,
  },
  {
    sensor: "net",
    sensorLabel: "NET",
    attribute: "download_speed",
    attributeLabel: "DownloadSpeed",
    showType: "Text",
    value: 183870,
    unit: "kb/s",
    units: ["kb/s", "mb/s"],
    showUnit: true,
  },
];
const OTHER_THEME_ITMES = [
  {
    sensor: "frontend",
    sensorLabel: "Other",
    attribute: "date",
    attributeLabel: "Date",
    showType: "Text",
    dateFormat: "%Y-%m-%d",
  },
  {
    sensor: "frontend",
    sensorLabel: "Other",
    attribute: "time",
    attributeLabel: "Time",
    showType: "Text",
    timeFormat: "%H:%M:%S",
  },
  {
    sensor: "weather",
    sensorLabel: "Other",
    attribute: "text",
    attributeLabel: "Weather",
    showType: "Text",
    value: "WatherFakeValue",
  },
  {
    sensor: "weather",
    sensorLabel: "Other",
    attribute: "icon",
    attributeLabel: "WeatherIcon",
    showType: "Image",
    value: "02d",
  },
  {
    sensor: "frontend",
    sensorLabel: "Other",
    attribute: "custom_text",
    attributeLabel: "CustomText",
    showType: "Text",
    value: "hello!",
  },
  {
    sensor: "frontend",
    sensorLabel: "Other",
    attribute: "custom_image",
    attributeLabel: "CustomImage",
    showType: "Image",
  },
];

const DEFAULT_THEME_GROUPS: ThemeGroup[] = [
  {
    icon: "mdi-cpu-64-bit",
    label: "CPU",
    items: CPU_THEME_ITEMS as ThemeItem[],
  },
  {
    icon: "mdi-expansion-card",
    label: "GPU",
    items: GPU_THEME_ITEMS as ThemeItem[],
  },
  {
    icon: "mdi-memory",
    label: "RAM",
    items: RAM_THEME_ITEMS as ThemeItem[],
  },
  {
    icon: "mdi-harddisk",
    label: "Disk",
    items: DISK_THEME_ITMES as ThemeItem[],
  },
  { icon: "mdi-wan", label: "NET", items: NET_THEME_ITEMS as ThemeItem[] },
  {
    icon: "mdi-dots-horizontal-circle-outline",
    label: "Other",
    items: OTHER_THEME_ITMES as ThemeItem[],
  },
];

const SUPPORT_FONTS = [
  { title: "MaterialDesign", value: "Material Design Icons" },
  { title: "LondrinaSolid", value: "LondrinaSolid" },
  { title: "LondrinaShadow", value: "LondrinaShadow" },
  { title: "BungeeSpice", value: "BungeeSpice" },
];

const DEFAULT_CANVAS_META: CanvasMeta = {
  shape: "rect" as CanvasShape,
  width: 480,
  height: 320,
  radius: 160,
};

const WEATHER_ICON_FILEPATH_MAP: WeatherIconFilepathMap = {
  "01d": "./weathericon/01d.png",
  "01n": "./weathericon/01n.png",
  "02d": "./weathericon/02d.png",
  "02n": "./weathericon/02n.png",
  "03d": "./weathericon/03d.png",
  "03n": "./weathericon/03d.png",
  "04d": "./weathericon/04d.png",
  "04n": "./weathericon/04n.png",
  "09d": "./weathericon/09d.png",
  "09n": "./weathericon/09n.png",
  "10d": "./weathericon/10d.png",
  "10n": "./weathericon/10n.png",
  "11d": "./weathericon/11d.png",
  "11n": "./weathericon/11n.png",
  "13d": "./weathericon/13d.png",
  "13n": "./weathericon/13n.png",
  "50d": "./weathericon/50d.png",
  "50n": "./weathericon/50n.png",
};

const SCREEN_SHPAES = [
  { title: "Rect", value: "rect" },
  { title: "Circle", value: "circle" },
];

export {
  DEFAULT_THEME_GROUPS,
  CPU_THEME_ITEMS,
  GPU_THEME_ITEMS,
  RAM_THEME_ITEMS,
  DISK_THEME_ITMES,
  NET_THEME_ITEMS,
  OTHER_THEME_ITMES,
  SUPPORT_FONTS,
  DEFAULT_CANVAS_META,
  WEATHER_ICON_FILEPATH_MAP,
  SCREEN_SHPAES,
};
