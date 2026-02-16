/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f3f9',
          100: '#d9e0f0',
          200: '#b3c1e1',
          300: '#8da2d2',
          400: '#6783c3',
          500: '#4164b4',
          600: '#1e3a5f',
          700: '#162d4a',
          800: '#0f2035',
          900: '#0a1628',
          950: '#060d18',
        },
      },
      minHeight: {
        11: '2.75rem',
      },
      minWidth: {
        11: '2.75rem',
      },
    },
  },
  plugins: [],
};
