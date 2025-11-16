/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './_layouts/**/*.html',
    './_includes/**/*.html',
    './_articles/**/*.md',
    './*.html',
    './*.md',
    './index.html',
    './about/**/*.html',
    './contact/**/*.html',
    './research/**/*.html',
    './articles/**/*.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
