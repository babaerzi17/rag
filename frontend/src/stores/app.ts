import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export const useAppStore = defineStore('app', () => {
  const isDarkMode = ref(false)
  const sidebarCollapsed = ref(false)
  const loading = ref(false)
  const appVersion = ref('1.0.0')

  // 全局对话框状态
  const showDialog = ref(false)
  const dialogTitle = ref('')
  const dialogMessage = ref('')

  async function initializeApp() {
    try {
      loading.value = true
      
      // 初始化认证状态
      const authStore = useAuthStore()
      await authStore.initAuth()
      
      // 加载用户偏好设置
      await loadUserPreferences()
      
    } catch (error) {
      console.error('应用初始化失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function loadUserPreferences() {
    try {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        isDarkMode.value = savedTheme === 'dark'
      }

      const savedSidebar = localStorage.getItem('sidebarCollapsed')
      if (savedSidebar) {
        sidebarCollapsed.value = JSON.parse(savedSidebar)
      }
    } catch (error) {
      console.error('加载用户偏好设置失败:', error)
    }
  }

  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', JSON.stringify(sidebarCollapsed.value))
  }

  function setLoading(value: boolean) {
    loading.value = value
  }

  // 全局对话框操作
  function openDialog(title: string, message: string) {
    dialogTitle.value = title
    dialogMessage.value = message
    showDialog.value = true
  }

  function closeDialog() {
    showDialog.value = false
    dialogTitle.value = ''
    dialogMessage.value = ''
  }

  return {
    isDarkMode,
    sidebarCollapsed,
    loading,
    appVersion,
    showDialog,
    dialogTitle,
    dialogMessage,
    initializeApp,
    loadUserPreferences,
    toggleDarkMode,
    toggleSidebar,
    setLoading,
    openDialog,
    closeDialog
  }
})