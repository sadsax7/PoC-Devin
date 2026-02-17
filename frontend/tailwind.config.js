/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        /** Token primario institucional — naranja Billetera Virtual */
        primary: '#FF6B00',
        /** Fondo oscuro institucional */
        'bg-dark': '#000000',
        /** Texto claro sobre fondos oscuros */
        'text-light': '#FFFFFF',
      },
      fontFamily: {
        /** Fuente institucional — Inter de Google Fonts */
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
