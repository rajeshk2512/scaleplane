/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: 'var(--color-navy)',
        'deep-blue': 'var(--color-deep-blue)',
        teal: 'var(--color-teal)',
        amber: 'var(--color-amber)',
        slate: 'var(--color-slate)',
        mist: 'var(--color-mist)',
        cloud: 'var(--color-cloud)',
        alert: 'var(--color-alert)',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        brand: '8px',
      },
    },
  },
  plugins: [],
}
