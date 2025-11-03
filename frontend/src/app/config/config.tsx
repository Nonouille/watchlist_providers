export const API_BASE_URL = (() => {
  const val = process.env.NEXT_PUBLIC_API_URL as string | undefined;
  if (!val) {
    throw new Error(
      'NEXT_PUBLIC_API_URL must be provided at build time. Set BACKEND_ENDPOINT in .env and rebuild the frontend image.'
    );
  }
  return val;
})();