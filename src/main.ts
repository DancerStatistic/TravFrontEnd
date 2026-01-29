import 'uno.css'
import { createApp } from 'vue'
import App from './App.vue'
import { Quasar } from 'quasar'
import quasarUserOptions from './quasar-user-options'
import router from './router'
import { createPinia } from 'pinia'

const app = createApp(App)

// Use Quasar Framework
app.use(Quasar, quasarUserOptions)

// Use Pinia for state management
const pinia = createPinia()
app.use(pinia)

// Use Vue Router
app.use(router)

// Mount the application
app.mount('#q-app')
