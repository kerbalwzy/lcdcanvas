import { parseGIF, decompressFrames, ParsedFrame } from "gifuct-js";

/**
 * An asynchronous function that converts a GIF to a sprite sheet.
 * @param {string|File} gif - Can be a URL, dataURL, or a file object.
 * @param {number} [maxWidth] - Optional, scale to the maximum width.
 * @param {number} [maxHeight] - Optional, scale to the maximum height.
 * @param {number} [maxDuration] - Optional, reduce the number of GIF frames to the maximum duration in milliseconds.
 * @returns {Promise<{ error: string } | { dataUrl: string, frameWidth: number, framesLength: number, delay: number }>} - Returns an object containing error information if there is an error, otherwise returns an object containing the sprite sheet's dataURL, frame width, number of frames, and delay time.
 */
export const gifToSprite = async (
  gif: string | File,
  maxWidth?: number,
  maxHeight?: number,
  maxDuration?: number
): Promise<
  { error: string; dataUrl: string; frameWidth: number; framesLength: number; delay: number }
> => {
  let arrayBuffer: ArrayBuffer | undefined;
  let error: string = "";
  let frames: ParsedFrame[] = [];

  // If gif is a file object, use FileReader to get the arrayBuffer.
  if (gif instanceof File) {
    const reader = new FileReader();
    try {
      arrayBuffer = await new Promise((resolve, reject) => {
        reader.onload = () => resolve(reader.result as ArrayBuffer);
        reader.onerror = () => reject(reader.error);
        reader.readAsArrayBuffer(gif);
      });
    } catch (err) {
      error = err as string;
    }
  }
  // If gif is a URL or dataURL, use fetch to get the arrayBuffer.
  else {
    try {
      arrayBuffer = await fetch(gif).then((resp) => resp.arrayBuffer());
    } catch (err) {
      error = err as string;
    }
  }

  // Use the "gifuct-js" library to parse and decompress the GIF's arrayBuffer into frame data.
  if (!error) frames = decompressFrames(parseGIF(arrayBuffer!), true);
  if (!error && !frames.length) error = "No_frame_error";
  if (error) {
    console.error(error);
    return { error, dataUrl: "", frameWidth: 0, framesLength: 0, delay: 0 };
  }

  // Create the required canvas elements.
  const dataCanvas = document.createElement("canvas");
  const dataCtx = dataCanvas.getContext("2d")!;
  const frameCanvas = document.createElement("canvas");
  const frameCtx = frameCanvas.getContext("2d")!;
  const spriteCanvas = document.createElement("canvas");
  const spriteCtx = spriteCanvas.getContext("2d")!;

  // Get the frame dimensions and delay time.
  let [width, height, delay] = [
    frames[0].dims.width,
    frames[0].dims.height,
    frames.reduce((acc, cur) => acc + cur.delay, 0) / frames.length,
  ];

  // Set the maximum duration of the GIF (if any).
  // FIXME Handle the delay time of each frame.
  const duration = frames.length * delay;
  maxDuration = maxDuration || duration;
  if (duration > maxDuration) frames.splice(Math.ceil(maxDuration / delay));

  // Set the scaling ratio (if any).
  maxWidth = maxWidth || width;
  maxHeight = maxHeight || height;
  const scale = Math.min(maxWidth / width, maxHeight / height);
  width = width * scale;
  height = height * scale;
  // Set the dimensions of the frame and sprite sheet canvases.
  frameCanvas.width = width;
  frameCanvas.height = height;
  spriteCanvas.width = width * frames.length;
  spriteCanvas.height = height;

  frames.forEach((frame, i) => {
    // Get the imageData of the frame from "frame.patch".
    const frameImageData = dataCtx.createImageData(
      frame.dims.width,
      frame.dims.height
    );
    frameImageData.data.set(frame.patch);
    dataCanvas.width = frame.dims.width;
    dataCanvas.height = frame.dims.height;
    dataCtx.putImageData(frameImageData, 0, 0);

    // Draw the frame from the imageData.
    if (frame.disposalType === 2) frameCtx.clearRect(0, 0, width, height);
    frameCtx.drawImage(
      dataCanvas,
      frame.dims.left * scale,
      frame.dims.top * scale,
      frame.dims.width * scale,
      frame.dims.height * scale
    );

    // Add the frame to the sprite sheet.
    spriteCtx.drawImage(frameCanvas, width * i, 0);
  });

  // Get the dataUrl of the sprite sheet.
  const dataUrl = spriteCanvas.toDataURL();

  // Clean up the DOM and release unused canvases.
  dataCanvas.remove();
  frameCanvas.remove();
  spriteCanvas.remove();

  return {
    error: "",
    dataUrl,
    frameWidth: width,
    framesLength: frames!.length,
    delay,
  };
};
