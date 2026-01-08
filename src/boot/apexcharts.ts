import { boot } from 'quasar/wrappers'
import VueApexCharts from 'vue3-apexcharts'

export default boot(({ app }) => {
  // vue3-apexcharts registers the component via app.component
  app.use(VueApexCharts)
})
