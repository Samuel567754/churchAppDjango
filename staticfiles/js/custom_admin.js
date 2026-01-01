// (function () {
//     const themeConfig = {
//       light: {
//         icon: '☀️',
//         label: 'Light Mode'
//       },
//       dark: {
//         icon: '🌙',
//         label: 'Dark Mode'
//       }
//     };
  
//     const btn = document.createElement('button');
//     btn.id = 'django-dark-toggle';
//     btn.title = 'Toggle Dark Mode';
//     btn.setAttribute('aria-label', 'Toggle Dark Mode');
//     document.body.appendChild(btn);
  
//     function getSystemPreference() {
//       return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
//     }
  
//     function applyTheme(theme) {
//       const isDark = theme === 'dark';
//       document.body.classList.toggle('dark-mode', isDark);
//       btn.innerHTML = isDark ? themeConfig.dark.icon : themeConfig.light.icon;
//       btn.title = isDark ? themeConfig.dark.label : themeConfig.light.label;
//       localStorage.setItem('djangoAdminTheme', theme);
//     }
  
//     const savedTheme = localStorage.getItem('djangoAdminTheme');
//     const systemPref = getSystemPreference();
//     const currentTheme = savedTheme || systemPref;
//     applyTheme(currentTheme);
  
//     btn.addEventListener('click', () => {
//       const isDark = document.body.classList.contains('dark-mode');
//       applyTheme(isDark ? 'light' : 'dark');
//     });
  
//     window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
//       if (!localStorage.getItem('djangoAdminTheme')) {
//         applyTheme(e.matches ? 'dark' : 'light');
//       }
//     });
//   })();
  