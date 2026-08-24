const viteBaseUrl =
  import.meta.env.BASE_URL && import.meta.env.BASE_URL !== "/"
    ? import.meta.env.BASE_URL
    : "/isaac/";

export const APP_BASE_PATH = `/${viteBaseUrl.replace(/^\/+|\/+$/g, "")}`;

const HTTP_URL_PATTERN = /^https?:\/\//i;
const URL_SCHEME_PATTERN = /^[a-z][a-z\d+.-]*:/i;

function isAllowedExternalUrl(value: string): boolean {
  return HTTP_URL_PATTERN.test(value) || value.startsWith("//");
}

export function staticUrl(path: string): string {
  const value = path.trim();
  if (!value) return "";
  if (isAllowedExternalUrl(value)) return value;
  if (URL_SCHEME_PATTERN.test(value)) return "";

  const absolutePath = value.startsWith("/") ? value : `/${value}`;
  if (
    absolutePath === APP_BASE_PATH ||
    absolutePath.startsWith(`${APP_BASE_PATH}/`)
  ) {
    return absolutePath;
  }

  return `${APP_BASE_PATH}${absolutePath}`;
}

export function normalizeMediaUrl(url: string): string {
  const value = url.trim();
  if (!value) return "";
  if (isAllowedExternalUrl(value)) return value;
  if (URL_SCHEME_PATTERN.test(value)) return "";
  return staticUrl(value);
}
