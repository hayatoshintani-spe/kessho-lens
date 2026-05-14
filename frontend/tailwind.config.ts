import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette
        bg: {
          primary: '#0B0E14',
          card: '#141922',
          sidebar: '#0F1219',
          elevated: '#1A2233',
        },
        accent: {
          gold: '#C8860A',
          'gold-light': '#E8A020',
          'gold-muted': '#7A5208',
        },
        text: {
          primary: '#E2DDD5',
          secondary: '#7B7F8C',
          muted: '#4A4F5C',
        },
        profit: '#1D9E75',
        loss: '#D85A30',
        border: {
          DEFAULT: '#1E2535',
          light: '#2A3345',
        },
        // Agent colors
        agent: {
          buffett: '#4CAF50',
          soros: '#E91E63',
          lynch: '#2196F3',
          flat: '#9E9E9E',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-card': 'linear-gradient(135deg, #141922 0%, #1A2233 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slideIn 0.2s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
