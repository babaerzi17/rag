<template>
  <div class="modern-auth-layout">
    <!-- 动态背景 -->
    <div class="background-wrapper">
      <div class="gradient-background"></div>
      <div class="animated-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
      <div class="grid-pattern"></div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="auth-main-content">
      <!-- 左侧品牌展示 -->
      <div class="brand-showcase d-none d-lg-flex">
        <div class="brand-content">
          <div class="brand-icon">🧠</div>
          <h1 class="brand-title">智能知识库</h1>
          <h2 class="brand-subtitle">RAG Knowledge Management</h2>
          <p class="brand-description">
            基于先进的检索增强生成技术，为企业提供智能化的知识管理解决方案
          </p>
          
          <div class="feature-list">
            <div class="feature-item">
              <span class="feature-icon">⚡</span>
              <span>智能检索与问答</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🛡️</span>
              <span>企业级安全保障</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">📈</span>
              <span>高性能处理引擎</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧登录表单 -->
      <div class="auth-form-section">
        <div class="form-container">
          <!-- 登录表单容器 -->
          <div class="login-container">
            <div class="form-wrapper">
              <router-view />
            </div>
            
            <!-- 底部信息 -->
            <div class="auth-footer">
              <div class="footer-stats">
                <div class="stat-item">
                  <span class="stat-icon">✅</span>
                  <span>99.9% 可用性</span>
                </div>
                <div class="stat-divider">•</div>
                <div class="stat-item">
                  <span class="stat-icon">🔒</span>
                  <span>企业级安全</span>
                </div>
                <div class="stat-divider">•</div>
                <div class="stat-item">
                  <span class="stat-icon">📞</span>
                  <span>24/7 支持</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 居中登录布局 - 无需额外JS逻辑
</script>

<style scoped>
/* 主布局容器 */
.modern-auth-layout {
  position: relative;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 动态背景系统 */
.background-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.gradient-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, 
    #667eea 0%, 
    #764ba2 25%, 
    #f093fb 50%, 
    #f5576c 75%, 
    #4facfe 100%);
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 动态几何形状 */
.animated-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(2px);
  animation: float-rotate 20s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: 5%;
  animation-delay: 0s;
  background: radial-gradient(circle at 30% 30%, 
    rgba(255, 255, 255, 0.2), 
    rgba(255, 255, 255, 0.05));
}

.shape-2 {
  width: 200px;
  height: 200px;
  top: 60%;
  right: 10%;
  animation-delay: 5s;
  background: radial-gradient(circle at 70% 70%, 
    rgba(255, 255, 255, 0.15), 
    rgba(255, 255, 255, 0.03));
}

.shape-3 {
  width: 150px;
  height: 150px;
  top: 20%;
  right: 25%;
  animation-delay: 10s;
  background: radial-gradient(circle at 50% 50%, 
    rgba(255, 255, 255, 0.18), 
    rgba(255, 255, 255, 0.04));
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 15%;
  left: 20%;
  animation-delay: 15s;
  background: radial-gradient(circle at 40% 60%, 
    rgba(255, 255, 255, 0.12), 
    rgba(255, 255, 255, 0.02));
}

@keyframes float-rotate {
  0%, 100% {
    transform: translate(0px, 0px) rotate(0deg) scale(1);
  }
  25% {
    transform: translate(30px, -30px) rotate(90deg) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) rotate(180deg) scale(0.9);
  }
  75% {
    transform: translate(40px, 10px) rotate(270deg) scale(1.05);
  }
}

/* 网格图案 */
.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 60px 60px;
  animation: grid-move 30s linear infinite;
}

@keyframes grid-move {
  0% { transform: translate(0, 0); }
  100% { transform: translate(60px, 60px); }
}

/* 主内容区域 */
.auth-main-content {
  position: relative;
  z-index: 10;
  display: flex;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  height: 100vh;
  max-height: 100vh;
  align-items: center;
  overflow: hidden;
}

/* 左侧品牌展示区域 */
.brand-showcase {
  flex: 1;
  padding: 80px 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-content {
  max-width: 500px;
  text-align: center;
}

.brand-icon {
  font-size: 64px;
  margin-bottom: 32px;
  animation: pulse-glow 3s ease-in-out infinite;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

@keyframes pulse-glow {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
  }
  50% {
    transform: scale(1.05);
    filter: drop-shadow(0 0 30px rgba(255, 255, 255, 0.5));
  }
}

.brand-title {
  font-size: 48px;
  font-weight: 800;
  color: white;
  margin-bottom: 16px;
  line-height: 1.2;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
  letter-spacing: -0.02em;
}

.brand-subtitle {
  font-size: 24px;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 32px;
  line-height: 1.4;
  text-shadow: 0 1px 10px rgba(0, 0, 0, 0.2);
}

.brand-description {
  font-size: 18px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 48px;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.2);
}

/* 功能特色列表 */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: flex-start;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateX(8px);
  color: white;
}

.feature-icon {
  font-size: 20px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.feature-item:hover .feature-icon {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

/* 右侧表单区域 */
.auth-form-section {
  flex: 0 0 500px;
  height: 100vh;
  max-height: 100vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.auth-form-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.6), 
    transparent);
}

.form-container {
  width: 100%;
  height: 100%;
  max-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 登录容器 */
.login-container {
  width: 80%;
  max-width: 400px;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
}

/* 表单包装器 */
.form-wrapper {
  width: 100%;
  margin-bottom: 40px;
}

/* 底部信息 */
.auth-footer {
  width: 100%;
  text-align: center;
}

.footer-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
  gap: 12px;
  font-size: 12px;
  color: rgba(44, 62, 80, 0.7);
  white-space: nowrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.stat-icon {
  font-size: 12px;
  margin-right: 4px;
}

.stat-divider {
  color: rgba(44, 62, 80, 0.3);
  font-weight: bold;
  margin: 0 4px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .brand-showcase {
    padding: 60px 40px;
  }
  
  .brand-title {
    font-size: 40px;
  }
  
  .brand-subtitle {
    font-size: 20px;
  }
}

@media (max-width: 960px) {
  .auth-main-content {
    flex-direction: column;
  }
  
  .brand-showcase {
    display: none !important;
  }
  
  .auth-form-section {
    flex: 1;
    height: 100vh;
    max-height: 100vh;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    overflow: hidden;
  }
  
  .form-container {
    padding: 40px 24px;
  }
}

@media (max-width: 600px) {
  .login-container {
    width: 90%;
  }
  
  .form-wrapper {
    margin-bottom: 32px;
  }
  
  .footer-stats {
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
  }
  
  .stat-item {
    font-size: 11px;
  }
  
  .stat-divider {
    display: none;
  }
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .gradient-background,
  .shape,
  .grid-pattern,
  .brand-icon {
    animation: none;
  }
  
  .feature-item:hover {
    transform: none;
  }
}
</style>