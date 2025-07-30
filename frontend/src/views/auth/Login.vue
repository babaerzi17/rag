<template>
  <div class="simple-login-form">
    <!-- 表单标题 -->
    <div class="form-header">
      <h2 class="form-title">欢迎回来</h2>
      <p class="form-subtitle">请使用您的账户登录</p>
      
      <!--
      <div class="test-accounts">
        <p class="test-title">测试账户：</p>
        <p class="test-account">管理员：admin / admin</p>
        <p class="test-account">普通用户：user / user</p>
      </div>
      -->
    </div>

    <!-- 登录表单内容区域 -->
    <div class="form-content">
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- 用户名输入框 -->
        <div class="input-group">
          <input
            v-model="loginForm.username"
            type="text"
            placeholder="用户名"
            :disabled="loading"
            class="form-input"
            required
          />
        </div>

        <!-- 密码输入框 -->
        <div class="input-group">
          <input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            :disabled="loading"
            class="form-input"
            required
          />
        </div>

        <!-- 记住我选项 -->
        <div class="form-options">
          <label class="checkbox-wrapper">
            <input
              v-model="rememberMe"
              type="checkbox"
              :disabled="loading"
              @change="handleRememberMeChange"
            />
            <span class="checkbox-text">记住我（包括密码）</span>
          </label>
        </div>

        <!-- 登录按钮 -->
        <button
          type="submit"
          :disabled="loading || !loginForm.username || !loginForm.password"
          class="login-btn"
        >
          <span v-if="!loading">登录</span>
          <span v-else>登录中...</span>
        </button>
      </form>
    </div>

    <!-- 消息通知 -->
    <div v-if="showError" class="message error-message">
      <span>{{ errorMessage }}</span>
      <button @click="showError = false" class="close-btn">×</button>
    </div>

    <div v-if="showSuccess" class="message success-message">
      <span>{{ successMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { addDynamicRoutes } from '@/router/index';  // 假设导出

const router = useRouter()
const authStore = useAuthStore()

// 安全地获取localStorage值
const getLocalStorageItem = (key: string): string => {
  if (typeof window !== 'undefined' && window.localStorage) {
    return localStorage.getItem(key) || '';
  }
  return '';
};

// Form state
const loading = ref(false)
const showPassword = ref(false)
const rememberMe = ref(getLocalStorageItem('rememberedUsername') ? true : false) // 根据是否有记住的用户名设置初始状态

// Login form data
const loginForm = reactive({
  username: getLocalStorageItem('rememberedUsername'), // 从localStorage读取记住的用户名
  password: getLocalStorageItem('rememberedPassword') // 从localStorage读取记住的密码
})

// Message state
const showError = ref(false)
const errorMessage = ref('')
const showSuccess = ref(false)
const successMessage = ref('')

// Handle login
const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    showError.value = true
    errorMessage.value = '请输入用户名和密码。'
    return
  }

  loading.value = true
  showError.value = false
  showSuccess.value = false

  try {
    await authStore.login(loginForm.username, loginForm.password, rememberMe.value) // 传递rememberMe状态
    
    // 记住我的操作已经在复选框变化时处理，这里不需要重复处理

    successMessage.value = '登录成功，正在跳转...'
    showSuccess.value = true

    // 模拟异步操作
    setTimeout(() => {
      // 直接跳转到首页，因为用户信息已经在登录时获取了
      if (authStore.user) {
        addDynamicRoutes() // 根据用户权限添加路由
      }
      router.push('/')
    }, 1000) // 延迟1秒跳转，给用户看到成功信息的时间
  } catch (error: any) {
    errorMessage.value = error.message || '登录失败，请检查您的凭据。'
    showError.value = true
    console.error("登录失败", error)
  } finally {
    loading.value = false
  }
}

// 处理记住我复选框变化
const handleRememberMeChange = () => {
  if (rememberMe.value) {
    // 勾选时立即保存当前输入的用户名和密码
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('rememberedUsername', loginForm.username);
      localStorage.setItem('rememberedPassword', loginForm.password);
    }
    showSuccess.value = true;
    successMessage.value = '已记住登录信息';
    setTimeout(() => {
      showSuccess.value = false;
    }, 2000);
  } else {
    // 取消勾选时立即清除保存的信息
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('rememberedUsername');
      localStorage.removeItem('rememberedPassword');
    }
    showSuccess.value = true;
    successMessage.value = '已清除记住的信息';
    setTimeout(() => {
      showSuccess.value = false;
    }, 2000);
  }
}

// Lifecycle hook to load remembered username and password
onMounted(() => {
  if (rememberMe.value) {
    const rememberedUsername = getLocalStorageItem('rememberedUsername');
    const rememberedPassword = getLocalStorageItem('rememberedPassword');
    if (rememberedUsername) {
      loginForm.username = rememberedUsername;
    }
    if (rememberedPassword) {
      loginForm.password = rememberedPassword;
    }
  }
})

</script>

<style scoped>
/* 主容器 */
.simple-login-form {
  width: 100%;
  margin: 0 auto;
  overflow-x: hidden; /* 强制隐藏水平滚动条 */
  max-height: 100vh; /* 限制最大高度为视口高度 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 400px; /* 设置最小高度 */
}

/* 表单头部 */
.form-header {
  margin-bottom: 20px;
  text-align: center;
  width: 100%;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
  line-height: 1.2;
}

.form-subtitle {
  font-size: 13px;
  color: rgba(44, 62, 80, 0.7);
  font-weight: 400;
  margin: 0;
}

/* 测试账户提示 */
.test-accounts {
  margin-top: 20px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.test-title {
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
  margin: 0 0 6px 0;
}

.test-account {
  font-size: 11px;
  color: rgba(44, 62, 80, 0.8);
  margin: 2px 0;
  font-family: monospace;
}

/* 表单内容区域 */
.form-content {
  width: 80%;
  margin: 0 auto;
}

/* 登录表单 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 输入组 */
.input-group {
  display: flex;
  flex-direction: column;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 400;
  background: white;
  transition: all 0.2s ease;
  outline: none;
  color: #333;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f5f5f5;
}

.form-input::placeholder {
  color: #999;
  font-weight: 400;
}

/* 表单选项 */
.form-options {
  display: flex;
  align-items: center;
  margin: 2px 0;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.checkbox-wrapper input[type="checkbox"] {
  width: 14px;
  height: 14px;
  accent-color: #667eea;
}

.checkbox-text {
  font-size: 13px;
  color: #555;
  font-weight: 400;
}

/* 登录按钮 */
.login-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 6px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 消息通知 */
.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 10px 14px;
  border-radius: 6px;
  font-weight: 400;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 250px;
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.success-message {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
  transition: opacity 0.2s ease;
  padding: 0;
  margin-left: 8px;
}

.close-btn:hover {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .form-content {
    width: 85%;
  }
  
  .form-title {
    font-size: 20px;
  }
  
  .form-subtitle {
    font-size: 12px;
  }
  
  .form-input {
    padding: 9px 12px;
    font-size: 14px;
  }
  
  .login-btn {
    padding: 9px 12px;
    font-size: 13px;
  }

  .message {
    position: fixed;
    top: 10px;
    left: 10px;
    right: 10px;
    min-width: auto;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .form-title {
    color: #f8f9fa;
  }

  .form-subtitle {
    color: rgba(248, 249, 250, 0.8);
  }

  .checkbox-text {
    color: #e5e7eb;
  }

  .form-input {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.2);
    color: #f9fafb;
  }

  .form-input:disabled {
    background: rgba(255, 255, 255, 0.02);
  }

  .form-input::placeholder {
    color: rgba(255, 255, 255, 0.6);
  }
}
</style>