import { fabric } from "fabric";
import { gifToSprite } from "./gif2sprite";

/**
 * Convert a GIF to a fabric.Image instance and add play, pause, and stop methods.
 * @param {string|File} gif - Can be a URL, dataURL, or a file object.
 * @param {number} [maxWidth] - Optional, scale to the maximum width.
 * @param {number} [maxHeight] - Optional, scale to the maximum height.
 * @param {number} [maxDuration] - Optional, reduce the number of GIF frames to the maximum duration in milliseconds.
 * @returns {Promise<{ error: string } | fabric.Image>} - Returns an object containing error information if there is an error, otherwise returns a fabric.Image instance with new play, pause, and stop methods.
 */
export const fabricGif = async (
  gif: string,
  maxWidth?: number,
  maxHeight?: number,
  maxDuration?: number
): Promise<{ error: string } | fabric.Image> => {
  // Call the gifToSprite function and wait for its result.
  const { error, dataUrl, delay, frameWidth, framesLength } = await gifToSprite(
    gif,
    maxWidth,
    maxHeight,
    maxDuration
  );

  // If there is an error, return an object containing the error information.
  if (error) return { error };

  // Create a new Promise to handle the image in the callback of fabric.Image.fromURL.
  return new Promise((resolve) => {
    fabric.Image.fromURL(dataUrl, (img: fabric.Image) => {
      // Get the image element.
      const sprite = img.getElement();
      img.width = frameWidth;
      img.height = sprite.height;
      // Initialize the frame index.
      let framesIndex = 0;
      // Record the start time.
      let start = performance.now();
      /**
       * Override the image's rendering method to draw the current frame based on the current state and frame index.
       * @param {CanvasRenderingContext2D} ctx - The 2D rendering context of the canvas.
       */
      img._render = function (ctx: CanvasRenderingContext2D) {
        // Get the current time.
        const now = performance.now();
        // Calculate the time difference.
        const delta = now - start;
        // If the time difference is greater than the delay time, update the frame index.
        if (delta > delay) {
          start = now;
          framesIndex++;
        }
        // If the frame index reaches the total number of frames or the state is stopped, reset the frame index.
        if (framesIndex === framesLength) framesIndex = 0;
        // Draw the current frame on the canvas.
        ctx.drawImage(
          sprite,
          frameWidth * framesIndex,
          0,
          frameWidth,
          sprite.height,
          -this.width! / 2,
          -this.height! / 2,
          frameWidth,
          sprite.height
        );
      };
      // Return the image instance through resolve.
      resolve(img);
    });
  });
};
