/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Fira Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['Fira Code', 'Courier New', 'monospace'],
      },
      colors: {
        primary: '#1E40AF',
        'primary-dark': '#1E3A8A',
        secondary: '#3B82F6',
        accent: '#D97706',
        destructive: '#DC2626',
        background: '#F8FAFC',
        card: '#FFFFFF',
        muted: '#E9EEF6',
        'muted-foreground': '#475569',
        border: '#DBEAFE',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        gray: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        }
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      }
    },
  },
  plugins: [],
}