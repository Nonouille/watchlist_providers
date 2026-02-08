const DEFAULT_API_BASE_URL = "https://cine.pyarnaud.studio/api";
const LOCAL_API_BASE_URL = "http://localhost:5000";

const isLocalHost = (hostname: string) =>
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "::1";

export const API_BASE_URL = (() => {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    if (envUrl) return envUrl;
    if (typeof window !== "undefined" && isLocalHost(window.location.hostname)) {
        return LOCAL_API_BASE_URL;
    }
    return DEFAULT_API_BASE_URL;
})();
