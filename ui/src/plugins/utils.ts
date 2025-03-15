// Throttle factory function (ensure the last trigger is executed)
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number = 500
): (...args: Parameters<T>) => void {
  let lastArgs: Parameters<T> | null = null;
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function (this: any, ...args: Parameters<T>) {
    lastArgs = args;

    if (!timeout) {
      timeout = setTimeout(() => {
        func.apply(this, lastArgs!);
        timeout = null;
        lastArgs = null;
      }, limit);
    }
  };
}

// Caching factory function
export function cachedFunc<T extends (...args: any[]) => any>(
  func: T,
  cacheTime: number = 5000 // Default cache time is 5 seconds
): CachedFunction<T> {
  let cache: Map<string, { result: ReturnType<T>; timestamp: number }> =
    new Map();

  const cachedFunction = function (
    this: ThisParameterType<T>,
    ...args: Parameters<T>
  ): ReturnType<T> {
    const key = JSON.stringify(args);
    const now = Date.now();

    if (cache.has(key)) {
      const cachedItem = cache.get(key)!;
      if (now - cachedItem.timestamp < cacheTime) {
        return cachedItem.result;
      }
    }

    const result = func.apply(this, args);
    cache.set(key, { result, timestamp: now });
    return result;
  };

  cachedFunction.clearCache = function () {
    cache.clear();
  };

  return cachedFunction as CachedFunction<T>;
}

// Get the current system theme
export function getSystemTheme(): "light" | "dark" {
  const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
  return darkModeQuery.matches ? "dark" : "light";
}

// Set up the theme change event listener callback
export function setupThemeChangeListener(
  onChange: (theme: "light" | "dark") => void
) {
  const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");

  // Initial theme
  onChange(getSystemTheme());

  // Listen for changes
  darkModeQuery.addEventListener("change", (event) => {
    onChange(event.matches ? "dark" : "light");
  });
}

// Extract the file name from the file path without the file extension
export function extractFileNameWithoutExtension(filePath: string) {
  // Extract the file name (including the suffix)
  const match = filePath.match(/[^\\/]+$/);
  if (match) {
    // Remove the file suffix
    return match[0].replace(/\.[^/.]+$/, "");
  }
  return null;
}

// Format the date and time
export function formatDatetime(
  date: Date,
  formatStr: string,
  regexp: RegExp
): string {
  // Define the mapping of formatting symbols
  const map: Record<string, string | number> = {
    // date
    Y: date.getFullYear(), // year
    m: (date.getMonth() + 1).toString().padStart(2, "0"), // month
    d: date.getDate().toString().padStart(2, "0"), // date
    B: date.toLocaleString("en-US", { month: "long" }), // the full month name
    b: date.toLocaleString("en-US", { month: "short" }), // the short month name
    A: date.toLocaleString("en-US", { weekday: "long" }), // the full weekday name
    a: date.toLocaleString("en-US", { weekday: "short" }), // the short weekday name
    // time
    H: date.getHours().toString().padStart(2, "0"), // 24-hour format hour
    M: date.getMinutes().toString().padStart(2, "0"), // minutes
    S: date.getSeconds().toString().padStart(2, "0"), // seconds
    I: (date.getHours() % 12 || 12).toString().padStart(2, "0"), // 12-hour format hour
    p: date.getHours() < 12 ? "AM" : "PM", // AM/PM
  };
  // Replace the format symbols
  return formatStr.replace(regexp, (match, key) => {
    const value = map[key];
    return value !== undefined ? value.toString() : match; // If not found in the mapping, return the original symbol
  });
}

export function formatDate(date: Date, formatStr: string): string {
  return formatDatetime(date, formatStr, /%(Y|m|d|B|b|A|a)/g);
}

export function formatTime(date: Date, formatStr: string): string {
  return formatDatetime(date, formatStr, /%(H|I|M|S|p)/g);
}

// Sleep for a specified number of milliseconds
export function sleep(ms: number): void {
  const startTime = Date.now();
  while (Date.now() - startTime < ms) {
    // do nothing
  }
}
