export default defineAppConfig({
  // https://ui.nuxt.com/getting-started/theme#design-system
  name: 'TrashMap',
  meta: {
    title: 'TrashMap',
    description: 'TrashMap — Suivi intelligent des déchets urbains grâce à l’IA.'
  },
  ui: {
    colors: {
      primary: 'emerald',
      neutral: 'slate',
    },
    button: {
      defaultVariants: {
        // Set default button color to neutral
        // color: 'neutral'
      }
    }
  }
})
