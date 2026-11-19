/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        panel: 'var(--panel)',
        line: 'var(--line)',
        cyan: 'var(--cyan)',
        ice: 'var(--ice)',
        muted: 'var(--muted)',
        amber: 'var(--amber)',
        green: 'var(--green)',
      },
      fontFamily: {
        display: ['var(--display)', 'sans-serif'],
        font: ['var(--font)', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
