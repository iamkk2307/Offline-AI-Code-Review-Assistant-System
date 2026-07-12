/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary brand palette — deep indigo/violet
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        // Surface colors for dark mode
        surface: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          700: '#334155',
          800: '#1e293b',
          850: '#172033',
          900: '#0f172a',
          950: '#080f1e',
        },
        // Severity colors
        critical: '#ef4444',
        high:     '#f97316',
        medium:   '#eab308',
        low:      '#22c55e',
        info:     '#3b82f6',
        // Score colors
        excellent: '#10b981',
        good:      '#84cc16',
        fair:      '#f59e0b',
        poor:      '#ef4444',
      },
      fontFamily: {
        sans:  ['Inter', 'system-ui', 'sans-serif'],
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial':  'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':   'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'mesh-dark':        'radial-gradient(at 40% 20%, hsla(240,70%,20%,1) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(260,80%,15%,1) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(240,60%,10%,1) 0px, transparent 50%)',
      },
      animation: {
        'fade-in':      'fadeIn 0.3s ease-in-out',
        'slide-up':     'slideUp 0.4s ease-out',
        'slide-in':     'slideIn 0.3s ease-out',
        'pulse-slow':   'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow':    'spin 3s linear infinite',
        'bounce-soft':  'bounceSoft 1s ease-in-out infinite',
        'shimmer':      'shimmer 2s linear infinite',
        'scale-in':     'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { transform: 'translateY(16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)',    opacity: '1' },
        },
        slideIn: {
          '0%':   { transform: 'translateX(-16px)', opacity: '0' },
          '100%': { transform: 'translateX(0)',      opacity: '1' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':       { transform: 'translateY(-4px)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        scaleIn: {
          '0%':   { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)',     opacity: '1' },
        },
      },
      boxShadow: {
        'glow-primary':   '0 0 20px rgba(99, 102, 241, 0.3)',
        'glow-success':   '0 0 20px rgba(16, 185, 129, 0.3)',
        'glow-danger':    '0 0 20px rgba(239, 68, 68, 0.3)',
        'glass':          '0 8px 32px rgba(0, 0, 0, 0.37)',
        'card-dark':      '0 4px 24px rgba(0, 0, 0, 0.4)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
