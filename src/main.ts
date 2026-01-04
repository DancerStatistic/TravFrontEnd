import 'uno.css'
import { createApp } from 'vue'
import App from './App.vue'
import { Quasar } from 'quasar'
import quasarUserOptions from './quasar-user-options'
import router from './router'

const app = createApp(App)

// Use Quasar Framework
app.use(Quasar, quasarUserOptions)

// Use Vue Router
app.use(router)

// Mount the application
app.mount('#q-app')
