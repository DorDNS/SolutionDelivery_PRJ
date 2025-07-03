// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  app: {
    head: {
      title: 'TrashMap',
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/images/icone-trashmap.svg' }
      ]
    }
  },

  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxt/eslint',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/fonts',
    '@vueuse/motion/nuxt',
    '@nuxtjs/color-mode',
  ],

  ui: {},

  css: ['~/assets/css/main.css'],

  future: {
    compatibilityVersion: 4
  },

  compatibilityDate: '2024-11-27',

  vite: {
    server: {
      proxy: {
        '/media': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/media/, '/media')
        }
      }
    }
  },

  colorMode: {
    preference: 'light',       // Défaut : light
    fallback: 'light',         // Si aucune préférence détectée
    dataValue: 'light',        // Valeur injectée dans l'attribut data-theme
    classSuffix: '',           // Pas de suffixe : 'light' => .light
    storageKey: 'color-mode'   // Nom dans le localStorage (optionnel)
  }
})
