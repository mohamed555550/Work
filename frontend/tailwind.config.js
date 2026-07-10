export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        stone: {
          400: '#57534e',
          500: '#44403c',
          600: '#292524',
          700: '#1c1917',
          800: '#0c0a09'
        },
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a'
        },
        forest: {
          50: '#f4f7f4',
          100: '#e3eadf',
          500: '#557047',
          600: '#465f3a',
          700: '#394d31',
          800: '#263626',
          900: '#172417'
        }
      },
      fontFamily: {
        sans: ['Cairo', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        card: '0 16px 45px rgba(32, 42, 40, 0.07)',
        float: '0 20px 60px rgba(32, 42, 40, 0.14)'
      }
    }
  },
  plugins: [],
}
