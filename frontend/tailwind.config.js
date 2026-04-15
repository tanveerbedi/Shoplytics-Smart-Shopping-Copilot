/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2563EB",
          light: "#EFF6FF",
          dark: "#1D4ED8",
        },
        success: {
          DEFAULT: "#16A34A",
          light: "#F0FDF4",
        },
        error: "#DC2626",
        warning: "#D97706",
        terminal: "#0F172A",
        bg: {
          DEFAULT: "#FAFAFA",
          panel: "#FFFFFF",
          muted: "#F1F5F9",
        },
        border: "#E2E8F0",
        text: {
          primary: "#0F172A",
          muted: "#64748B",
          dim: "#94A3B8",
        },
      },
      fontFamily: {
        display: ['"Instrument Serif"', "serif"],
        sans: ['"DM Sans"', "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      boxShadow: {
        soft: "0 4px 24px rgba(0,0,0,0.06)",
        panel: "0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.04)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "blink": "blink 1s step-end infinite",
      },
      keyframes: {
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
      },
    },
  },
  plugins: [],
};
