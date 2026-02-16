"use client";

import { useEffect, useState } from "react";

type ThemeMode = "light" | "dark";

const STORAGE_KEY = "theme";

const getSystemTheme = (): ThemeMode => {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

export const ThemeToggle = () => {
  const [theme, setTheme] = useState<ThemeMode>("light");

  const applyTheme = (mode: ThemeMode) => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(mode);
    localStorage.setItem(STORAGE_KEY, mode);
    setTheme(mode);
  };

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
    applyTheme(stored ?? getSystemTheme());

    if (!stored) {
      const media = window.matchMedia("(prefers-color-scheme: dark)");
      const handler = () => applyTheme(media.matches ? "dark" : "light");
      media.addEventListener("change", handler);
      return () => media.removeEventListener("change", handler);
    }
  }, []);

  return (
    <button
      type="button"
      aria-label="Toggle theme"
      onClick={() => applyTheme(theme === "dark" ? "light" : "dark")}
      className={`theme-switcher-grid ${theme === "dark" ? "night-theme" : ""}`}
    >
      <div className="sun" aria-hidden="true"></div>
      <div className="moon-overlay" aria-hidden="true"></div>
      <div className="cloud-ball cloud-ball-left" id="ball1" aria-hidden="true"></div>
      <div className="cloud-ball cloud-ball-middle" id="ball2" aria-hidden="true"></div>
      <div className="cloud-ball cloud-ball-right" id="ball3" aria-hidden="true"></div>
      <div className="cloud-ball cloud-ball-top" id="ball4" aria-hidden="true"></div>
      <div className="star" id="star1" aria-hidden="true"></div>
      <div className="star" id="star2" aria-hidden="true"></div>
      <div className="star" id="star3" aria-hidden="true"></div>
      <div className="star" id="star4" aria-hidden="true"></div>
    </button>
  );
};
