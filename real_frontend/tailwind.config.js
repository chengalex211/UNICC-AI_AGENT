/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      colors: {
        apple: {
          blue: '#0071e3',
          'blue-hover': '#0077ed',
          'blue-light': '#e8f0fe',
          green: '#34c759',
          'green-bg': '#e8faf0',
          red: '#ff3b30',
          'red-bg': '#fff2f2',
          orange: '#ff9500',
          'orange-bg': '#fff8ec',
          gray: {
            50: '#f5f5f7',
            100: '#e8e8ed',
            200: '#d1d1d6',
            300: '#aeaeb2',
            400: '#8e8e93',
            500: '#6e6e73',
            600: '#48484a',
            700: '#3a3a3c',
            800: '#2c2c2e',
            900: '#1c1c1e',
          },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'apple-sm': '0 2px 8px rgba(0,0,0,0.06)',
        'apple': '0 4px 16px rgba(0,0,0,0.08)',
        'apple-lg': '0 8px 32px rgba(0,0,0,0.10)',
        'apple-card': '0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.06)',
      },
      borderRadius: {
        'apple': '12px',
        'apple-lg': '18px',
        'apple-xl': '24px',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'pulse-dot': 'pulseDot 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(16px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        slideIn: { from: { opacity: 0, transform: 'translateX(-12px)' }, to: { opacity: 1, transform: 'translateX(0)' } },
        pulseDot: { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.4 } },
      },
    },
  },
  plugins: [],
}
