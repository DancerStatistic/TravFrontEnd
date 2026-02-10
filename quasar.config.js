// quasar.config.js
/* eslint-env node */
const { configure } = require('quasar/wrappers')
const Unocss = require('unocss/vite').default
const { presetAttributify, presetUno } = require('unocss')
const { splitVendorChunkPlugin } = require('vite')

module.exports = configure(function () {
  return {
    boot: [
      'unocss',   // make sure this is listed *before* axios
      'axios',
      'auth',
      'apexcharts'
    ],

    build: {
      vueRouterMode: 'hash',
      extendViteConf (viteConf) {
        viteConf.plugins.unshift(
          Unocss({
            presets: [ presetUno(), presetAttributify() ],
            detect: {
              // force UnoCSS to scan these files for the import 'uno.css'
              entry: [
                'src/main.ts',
                'src/boot/unocss.ts'
              ]
            }
          }),
          splitVendorChunkPlugin()
        )
      }
    },

    devServer: {
      https: false,
      port: 8080,
      open: true
    },

    framework: {
      config: {},
      plugins: []
    }
  }
})
