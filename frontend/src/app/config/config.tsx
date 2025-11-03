export const API_BASE_URL = (() => {
  // client runtime injection (public/env.js)
  if (typeof window !== 'undefined') {
    const w = (window as Window & { __env__?: { BACKEND_ENDPOINT?: string } }).__env__;
    if (w?.BACKEND_ENDPOINT) return w.BACKEND_ENDPOINT;
  }

  // server/runtime env available to the Node server
  if (process.env.BACKEND_ENDPOINT) return process.env.BACKEND_ENDPOINT;
  // optional compatibility with NEXT_PUBLIC_* if still used on server
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;

  // fallback to localhost (port your backend listens on)
  return 'http://localhost:5000';
})();