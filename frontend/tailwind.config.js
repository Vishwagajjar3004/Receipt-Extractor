/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Brand accent gradient (indigo -> cyan), used sparingly on
        // primary actions and the receipt "printed" header strip.
        brand: {
          indigo: "#4F46E5",
          cyan: "#06B6D4",
        },
        paper: "#FBFAF7", // warm paper-white for the receipt card
        ink: "#1F2430", // near-black "printed ink" text color
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "'Courier New'", "monospace"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
      },
      boxShadow: {
        receipt: "0 10px 30px -12px rgba(31, 36, 48, 0.25)",
      },
    },
  },
  plugins: [],
};
