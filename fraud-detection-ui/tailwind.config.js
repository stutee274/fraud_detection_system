/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        danger: '#dc2626',
        success: '#16a34a',
        warning: '#eab308',
      }
    },
  },
  plugins: [],
}