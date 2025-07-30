import { createApp } from 'vue'
import { createPinia } from 'pinia'
// import { createVuetify } from 'vuetify' // 移除 Vuetify 导入
// import { aliases, mdi } from 'vuetify/iconsets/mdi' // 移除 Vuetify 导入
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'
import axios from 'axios'; // 导入 axios

// Element Plus 导入
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 全局表格字体大小调整
import './assets/global.css'

// Vuetify styles // 移除 Vuetify 样式
// import 'vuetify/styles'
// import '@mdi/font/css/materialdesignicons.css'

// KaTeX styles for LaTeX rendering
import 'katex/dist/katex.min.css'

// Highlight.js styles for code syntax highlighting  
import 'highlight.js/styles/github.css'

const app = createApp(App)

// Create Vuetify instance // 移除 Vuetify 实例创建
// const vuetify = createVuetify({
//   theme: {
//     defaultTheme: 'light',
//     themes: {
//       light: {
//         colors: {
//           primary: '#1976D2',
//           secondary: '#424242',
//           accent: '#82B1FF',
//           error: '#FF5252',
//           info: '#2196F3',
//           success: '#4CAF50',
//           warning: '#FFC107',
//         },
//       },
//       dark: {
//         colors: {
//           primary: '#2196F3',
//           secondary: '#424242',
//           accent: '#FF4081',
//           error: '#FF5252',
//           info: '#2196F3',
//           success: '#4CAF50',
//           warning: '#FB8C00',
//         },
//       },
//     },
//   },
//   icons: {
//     defaultSet: 'mdi',
//     aliases,
//     sets: {
//       mdi,
//     },
//   },
// })

// Create Pinia store
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus) // 使用 Element Plus
// app.use(vuetify) // 移除 Vuetify 使用

// 配置 axios 默认基础 URL
axios.defaults.baseURL = 'http://127.0.0.1:8000';

// 挂载应用
app.mount('#app')