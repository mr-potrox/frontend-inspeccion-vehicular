/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",   // azul amigable
        secondary: "#f97316", // naranja cálido
        neutral: "#f3f4f6",   // gris claro
      },
    },
  },
  plugins: [],
};