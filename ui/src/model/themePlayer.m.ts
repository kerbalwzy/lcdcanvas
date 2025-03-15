import { SUPPORT_FONTS, WEATHER_ICON_FILEPATH_MAP } from "@/consts/theme.c";
import { fabric } from "fabric";
import { markRaw } from "vue";
import { fabricGif } from "@/model/fabricGIF";
import { formatDate, formatTime } from "@/plugins";
import i18n from "@/plugins/i18n";

const { t } = i18n.global;

export class ThemePlayer {
  private tooltip: fabric.Text;
  public meta: CanvasMeta;
  public propertiesToInclude: string[] = ["name", "data"];
  public canvas: fabric.Canvas;

  constructor(
    element: HTMLCanvasElement,
    canvasMeta: CanvasMeta,
    hideTooltip: boolean = false
  ) {
    const canvas = new fabric.Canvas(element, {
      selection: false,
      backgroundColor: "rgba(0, 0, 0)",
    });
    // Must use markRaw to avoid Vue's reactivity system from tracking the canvas object.
    this.canvas = markRaw(canvas);
    this.initFonts();
    if (hideTooltip) {
      this.tooltip = new fabric.Text("", {
        opacity: 0, // hidden by default
        selectable: false,
        evented: false,
        excludeFromExport: true, // exclude from canvas export
      });
    } else {
      this.canvas.hoverCursor = "help";
      this.tooltip = this.initTooltip();
    }
    this.meta = this.fromCanvasMeta(canvasMeta);

    // Render loop
    fabric.util.requestAnimFrame(function render() {
      canvas.renderAll();
      setTimeout(() => {
        fabric.util.requestAnimFrame(render);
      }, 100); // 100ms interval for rendering
    });
  }

  public initFonts() {
    SUPPORT_FONTS.forEach((font) => {
      if (!font.value) return;
      const text = new fabric.Text("preloadFonts", {
        fontFamily: font.value,
        fontSize: 14,
        fill: "transparent",
      });
      this.canvas.add(text);
      this.canvas.remove(text);
    });
  }

  public initTooltip(): fabric.Text {
    const tooltip = new fabric.Text("", {
      name: "tooltip",
      data: undefined,
      fontSize: 14,
      fontStyle: "italic",
      fill: "black",
      backgroundColor: "white",
      shadow: "2px 2px 8px rgba(0, 0, 0, 0.3)", // add shadow effect
      opacity: 0, // hidden by default
      selectable: false,
      evented: false,
      excludeFromExport: true, // exclude from canvas export
    });
    this.canvas.add(tooltip);
    this.canvas.on("mouse:over", (e) => {
      if (e.target instanceof fabric.Object) {
        const obj = e.target as fabric.Object;
        const item = obj.data as ThemeItem;
        this.tooltip.data = item.uuid;
        this.tooltip.text =
          t(`label.${item.sensorLabel}`) +
          " - " +
          t(`label.${item.attributeLabel}`);
        this.tooltip.left =
          obj.left! -
          (obj.originX == "center" ? obj.width! / 2 : obj.width!) * obj.scaleX!;
        this.tooltip.top = obj.top! - 20;
        if (this.tooltip.left! + this.tooltip.width! > this.canvas.width!) {
          this.tooltip.left = this.canvas.width! - this.tooltip.width!;
        }
        if (this.tooltip.top < 0) {
          this.tooltip.top = 0;
        }
        this.tooltip.opacity = 1;
        this.canvas.bringToFront(this.tooltip);
        this.canvas.renderAll();
      }
      console.debug("handleObjMouseOver", e.target);
    });
    this.canvas.on("mouse:out", (e) => {
      if (e.target instanceof fabric.Object) {
        this.tooltip.opacity = 0;
        this.canvas.renderAll();
      }
      console.debug("handleObjMouseOut");
    });
    this.tooltip = tooltip;
    return tooltip;
  }

  public cavansSize() {
    return {
      width: this.canvas.getWidth(),
      height: this.canvas.getHeight(),
    };
  }

  public drawGIF(src: string, callback: (img: fabric.Image) => void) {
    const canvasSize = this.cavansSize();
    fabricGif(src, canvasSize.width, canvasSize.height).then(
      (res: fabric.Image | { error: string }) => {
        if (res instanceof fabric.Image) {
          callback(res);
        } else {
          console.error(res.error);
        }
      }
    );
  }

  public fromCanvasMeta(meta: CanvasMeta): CanvasMeta {
    if (meta.shape == "circle") {
      this.canvas.setWidth(meta.radius * 2);
      this.canvas.setHeight(meta.radius * 2);
      const clipPath = new fabric.Circle({
        radius: meta.radius,
        fill: "transparent",
        excludeFromExport: true,
      });
      this.canvas.clipPath = clipPath;
      this.canvas.renderAll();
    } else {
      this.canvas.setWidth(meta.width);
      this.canvas.setHeight(meta.height);
      this.canvas.clipPath = undefined;
    }
    if (meta.canvasJSON) {
      this.canvas.clear();
      this.canvas.loadFromJSON(meta.canvasJSON, () => {
        this.canvas.renderAll();

        this.canvas.getObjects().forEach((obj) => {
          // IF the obj is an gif, we need to rebuild it.
          if (obj.data.value?.type == "image/gif") {
            this.drawGIF(obj.data.value.src, (gif: fabric.Image) => {
              console.debug("rebuild gif");
              gif.setOptions(obj.toDatalessObject(this.propertiesToInclude));
              gif.selectable = false;
              this.canvas.add(gif);
              console.debug(gif.scaleX, gif.scaleY);
              this.canvas.remove(obj);
            });
          } else {
            obj.selectable = false;
          }
        });
      });
    }
    this.meta = meta;
    return meta;
  }

  public fromThemeFileContent(contentStr: string) {
    const meta = JSON.parse(contentStr) as CanvasMeta;
    // fix the data of canvasJSON for version diff
    if (meta.canvasJSON.objects) {
      meta.canvasJSON.objects.forEach((obj: any) => {
        // fix the weather icon image src
        let data = obj.data as ThemeItem;
        if (data.sensor == "weather" && data.attribute == "icon") {
          obj.src = WEATHER_ICON_FILEPATH_MAP[data.value];
        }
      });
    }
    this.fromCanvasMeta(meta);
  }

  public toImageSrc(): string {
    return this.canvas.renderAll().toDataURL({
      format: "jpg",
      quality: 0.8,
    });
  }

  public themeSensors(): string[] {
    const sensors = new Set<string>();
    this.meta.canvasJSON?.objects.forEach((obj: any) => {
      const themeItem = obj.data as ThemeItem;
      if (themeItem.sensor && themeItem.sensor != "frontend") {
        sensors.add(themeItem.sensor);
      }
    });
    return [...sensors];
  }

  public getfrontendSensorValue(item: ThemeItem): any {
    switch (item.attribute) {
      case "date":
        return formatDate(new Date(), item.dateFormat || "%Y-%m-%d");
      case "time":
        return formatTime(new Date(), item.timeFormat || "%H:%M:%S");
      case "custom_text":
        return item.value || "hello world";
      default:
        return item.value;
    }
  }

  public handleTextValueAndUnit(item: ThemeItem, value: any): string {
    switch (item.attribute) {
      case "load":
        value = Math.round(value * 100).toFixed(0);
        break;
      case "upload_speed":
      case "download_speed":
        if (item.unit == "kb/s") {
          value = (value / 1e3).toFixed(2); // kb/s
        } else {
          value = (value / 1e6).toFixed(2); // mb/s
        }
        break;
    }
    if (item.showUnit) {
      value = value + ` ${item.unit}`;
    }
    if (item.sensor == "weather" && item.attribute == "text") {
      if (item.value == "WatherFakeValue") {
        value = t("label.WatherFakeValue");
      }
      // replace temperature unit character
      value = value.replace(/℃/g, "°C");
    }
    return value.toString();
  }

  public updateText(text: fabric.Text, value: string) {
    const item = text.data as ThemeItem;
    value = this.handleTextValueAndUnit(item, value);
    if (text.text == value) return;
    text.set({
      text: value || "",
    });
    text.data.value = value;
  }

  public updateBarChart(barChart: fabric.Group, value: number) {
    const background = barChart.getObjects()[0] as fabric.Rect;
    const foreground = barChart.getObjects()[1] as fabric.Rect;
    const width = Math.min(background.width! * value, background.width!);
    if (foreground.width == width) return;
    // Update the width of the foreground object
    foreground.set({ width: width });
    barChart.data.value = value;
  }

  public updateDonutChart(donutChart: fabric.Group, value: number) {
    const background = donutChart.getObjects()[0] as fabric.Circle;
    const foreground = donutChart.getObjects()[1] as fabric.Circle;
    const item = donutChart.data as ThemeItem;

    // compute the dash array of the foreground object
    const segmentWidth = item.segmentWidth || 5;
    const gapWidth = item.segmentGap || 0;
    const circumference =
      2 * Math.PI * background.radius! * (background.endAngle! / 360);
    let progressLength = value * circumference;
    const processDashArray = [];
    while (progressLength > 0) {
      if (progressLength <= segmentWidth) {
        processDashArray.push(progressLength);
        break;
      }
      processDashArray.push(segmentWidth);
      processDashArray.push(gapWidth);
      progressLength -= segmentWidth + gapWidth;
    }
    // Update the strokeDashArray and endAngle of the foreground object
    foreground.set({
      strokeDashArray: processDashArray,
      endAngle: background.endAngle! * value,
    });
    donutChart.data.value = value;
  }

  public updateImage(image: fabric.Image, value: any) {
    const themeItem = image.data as ThemeItem;
    const imageSrc =
      themeItem.sensor == "weather" ? WEATHER_ICON_FILEPATH_MAP[value] : value;
    if (themeItem.value == imageSrc) return;
    // Reset the image src when the image src is changed.
    image.setSrc(imageSrc, () => {
      image.data.value = imageSrc;
    });
  }

  public updateObjectValue(obj: fabric.Object, value: any) {
    // Update obj by showType
    switch (obj.data.showType) {
      case "Text":
        this.updateText(obj as fabric.Text, value);
        break;
      case "BarChart":
        this.updateBarChart(obj as fabric.Group, value);
        break;
      case "DonutChart":
        this.updateDonutChart(obj as fabric.Group, value);
        break;
      case "Image":
        this.updateImage(obj as fabric.Image, value);
        break;
    }
    console.debug(
      `Update ${obj.data.sensor} - ${obj.data.attribute} to ${value}`
    );
  }

  public loadSensorsValue(values: any) {
    console.debug("Load sensors value", values);
    this.canvas.getObjects().forEach((obj) => {
      const item = obj.data as ThemeItem;
      // Skip if the object is not a theme item or is a custom item
      if (!item || !item.sensor || item.attribute.includes("custom")) return;

      let value: any;
      // Handle frontend sensor values separately
      if (item.sensor == "frontend") {
        value = this.getfrontendSensorValue(item);
      } else {
        value = values[item.sensor]?.[item.attribute];
      }
      // If the value is undefined or null, skip
      if (value == undefined || value == null) return;
      // If the value has not changed, skip (except for weather)
      if (item.sensor != "weather" && item.value == value) return;
      //
      this.updateObjectValue(obj, value);
    });
    this.canvas.renderAll();
  }
}
