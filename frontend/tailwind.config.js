/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#111216',
        cardBg: '#181A20',
        borderColor: '#2D3139',
        accentGreen: '#00F29E',
        accentBlue: '#00D4FF',
        accentRed: '#FF4A6B',
        accentYellow: '#FFC837',
        accentPurple: '#D946EF',
      }
    },
  },
  plugins: [],
}
