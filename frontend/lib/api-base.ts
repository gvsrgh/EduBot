const DEFAULT_API_BASE = 'https://edubot-backend-534287199772.asia-south1.run.app/api';

const LOCALHOST_API_RE = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/|$)/i;

function trimTrailingSlash(url: string): string {
  return url.replace(/\/+$/, '');
}

export function getApiBase(): string {
  const envBase = (process.env.NEXT_PUBLIC_API_URL || '').trim();
  if (!envBase) {
    return DEFAULT_API_BASE;
  }

  const normalized = trimTrailingSlash(envBase);

  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    const pageIsLocal = host === 'localhost' || host === '127.0.0.1';
    const apiIsLocalhost = LOCALHOST_API_RE.test(normalized);

    // Guard against misconfigured production builds that still point to localhost.
    if (!pageIsLocal && apiIsLocalhost) {
      return DEFAULT_API_BASE;
    }
  }

  return normalized;
}
