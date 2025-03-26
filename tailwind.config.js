/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './**/static/**/*.js',
    "./node_modules/flowbite/**/*.js"
  ],
  darkMode: 'class', // Enables dark mode based on a CSS class
  theme: {
    extend: {
      backdropBlur: {
        sm: '4px',
    },
      colors: {
        church: {
           brown: '#4A2F21',
           gold: '#998463',
        }
      }
    },
  },
  plugins: [
    require('flowbite/plugin'),
    require('@tailwindcss/forms'),
  ],
}

