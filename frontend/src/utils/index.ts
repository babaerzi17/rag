// 通用工具函数库

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @param decimals 小数位数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * 格式化日期时间
 * @param date 日期对象或时间戳
 * @param format 格式化选项
 * @returns 格式化后的日期字符串
 */
export function formatDate(
  date: Date | string | number,
  format: 'short' | 'medium' | 'long' | 'relative' = 'medium'
): string {
  const dateObj = new Date(date)
  const now = new Date()
  const diff = now.getTime() - dateObj.getTime()

  if (format === 'relative') {
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    const weeks = Math.floor(days / 7)
    const months = Math.floor(days / 30)
    const years = Math.floor(days / 365)

    if (seconds < 60) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    if (weeks < 4) return `${weeks}周前`
    if (months < 12) return `${months}个月前`
    return `${years}年前`
  }

  const options: Intl.DateTimeFormatOptions = {
    short: {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    },
    medium: {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    },
    long: {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }
  }

  return dateObj.toLocaleString('zh-CN', options[format])
}

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param wait 等待时间（毫秒）
 * @param immediate 是否立即执行
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate = false
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }

    const callNow = immediate && !timeout

    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)

    if (callNow) func(...args)
  }
}

/**
 * 节流函数
 * @param func 要节流的函数
 * @param limit 时间限制（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  return function (...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * 深拷贝对象
 * @param obj 要拷贝的对象
 * @returns 深拷贝后的对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as unknown as T
  if (typeof obj === 'object') {
    const clonedObj = {} as { [key in keyof T]: T[key] }
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
  return obj
}

/**
 * 生成唯一ID
 * @param prefix 前缀
 * @returns 唯一ID字符串
 */
export function generateId(prefix = ''): string {
  const timestamp = Date.now().toString(36)
  const randomStr = Math.random().toString(36).substring(2, 8)
  return prefix + timestamp + randomStr
}

/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 是否为有效邮箱
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证手机号格式（中国大陆）
 * @param phone 手机号
 * @returns 是否为有效手机号
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 密码强度等级和提示
 */
export function validatePassword(password: string): {
  level: 'weak' | 'medium' | 'strong'
  score: number
  suggestions: string[]
} {
  let score = 0
  const suggestions: string[] = []

  // 长度检查
  if (password.length >= 8) {
    score += 25
  } else {
    suggestions.push('密码长度至少8位')
  }

  // 包含小写字母
  if (/[a-z]/.test(password)) {
    score += 25
  } else {
    suggestions.push('包含小写字母')
  }

  // 包含大写字母
  if (/[A-Z]/.test(password)) {
    score += 25
  } else {
    suggestions.push('包含大写字母')
  }

  // 包含数字
  if (/\d/.test(password)) {
    score += 25
  } else {
    suggestions.push('包含数字')
  }

  // 包含特殊字符
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    score += 25
  }

  // 额外长度奖励
  if (password.length >= 12) {
    score += 10
  }

  let level: 'weak' | 'medium' | 'strong'
  if (score < 50) {
    level = 'weak'
  } else if (score < 75) {
    level = 'medium'
  } else {
    level = 'strong'
  }

  return { level, score: Math.min(score, 100), suggestions }
}

/**
 * 复制文本到剪贴板
 * @param text 要复制的文本
 * @returns 是否复制成功
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    // 降级处理
    try {
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      return true
    } catch (fallbackErr) {
      console.error('复制到剪贴板失败:', fallbackErr)
      return false
    }
  }
}

/**
 * 下载文件
 * @param url 文件URL或Blob对象
 * @param filename 文件名
 */
export function downloadFile(url: string | Blob, filename: string): void {
  const link = document.createElement('a')
  
  if (url instanceof Blob) {
    link.href = URL.createObjectURL(url)
  } else {
    link.href = url
  }
  
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  if (url instanceof Blob) {
    URL.revokeObjectURL(link.href)
  }
}

/**
 * 获取文件扩展名
 * @param filename 文件名
 * @returns 文件扩展名（小写，不含点）
 */
export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || ''
}

/**
 * 检查文件类型
 * @param filename 文件名
 * @param allowedTypes 允许的文件类型数组
 * @returns 是否为允许的文件类型
 */
export function isAllowedFileType(filename: string, allowedTypes: string[]): boolean {
  const extension = getFileExtension(filename)
  return allowedTypes.includes(extension)
}

/**
 * 格式化数字
 * @param num 数字
 * @param options 格式化选项
 * @returns 格式化后的数字字符串
 */
export function formatNumber(
  num: number,
  options: {
    decimals?: number
    separator?: string
    prefix?: string
    suffix?: string
    compact?: boolean
  } = {}
): string {
  const {
    decimals = 0,
    separator = ',',
    prefix = '',
    suffix = '',
    compact = false
  } = options

  if (compact) {
    const units = ['', 'K', 'M', 'B', 'T']
    let unitIndex = 0
    let value = num

    while (value >= 1000 && unitIndex < units.length - 1) {
      value /= 1000
      unitIndex++
    }

    return prefix + value.toFixed(decimals) + units[unitIndex] + suffix
  }

  const parts = num.toFixed(decimals).split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, separator)

  return prefix + parts.join('.') + suffix
}

/**
 * 获取随机颜色
 * @param type 颜色类型
 * @returns 颜色值
 */
export function getRandomColor(type: 'hex' | 'rgb' | 'hsl' = 'hex'): string {
  switch (type) {
    case 'hex':
      return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')
    case 'rgb':
      const r = Math.floor(Math.random() * 256)
      const g = Math.floor(Math.random() * 256)
      const b = Math.floor(Math.random() * 256)
      return `rgb(${r}, ${g}, ${b})`
    case 'hsl':
      const h = Math.floor(Math.random() * 360)
      const s = Math.floor(Math.random() * 101)
      const l = Math.floor(Math.random() * 101)
      return `hsl(${h}, ${s}%, ${l}%)`
    default:
      return '#000000'
  }
}

/**
 * 本地存储封装
 */
export const storage = {
  /**
   * 设置本地存储
   * @param key 键名
   * @param value 值
   * @param expiry 过期时间（毫秒）
   */
  set(key: string, value: any, expiry?: number): void {
    const item = {
      value,
      expiry: expiry ? Date.now() + expiry : null
    }
    localStorage.setItem(key, JSON.stringify(item))
  },

  /**
   * 获取本地存储
   * @param key 键名
   * @returns 存储的值或null
   */
  get<T = any>(key: string): T | null {
    try {
      const itemStr = localStorage.getItem(key)
      if (!itemStr) return null

      const item = JSON.parse(itemStr)
      
      // 检查是否过期
      if (item.expiry && Date.now() > item.expiry) {
        localStorage.removeItem(key)
        return null
      }

      return item.value
    } catch (err) {
      console.error('获取本地存储失败:', err)
      return null
    }
  },

  /**
   * 删除本地存储
   * @param key 键名
   */
  remove(key: string): void {
    localStorage.removeItem(key)
  },

  /**
   * 清空本地存储
   */
  clear(): void {
    localStorage.clear()
  }
}

/**
 * URL参数处理
 */
export const urlParams = {
  /**
   * 获取URL参数
   * @param name 参数名
   * @param url URL字符串（可选，默认当前页面）
   * @returns 参数值或null
   */
  get(name: string, url?: string): string | null {
    const urlObj = new URL(url || window.location.href)
    return urlObj.searchParams.get(name)
  },

  /**
   * 设置URL参数
   * @param params 参数对象
   * @param replace 是否替换当前历史记录
   */
  set(params: Record<string, string>, replace = false): void {
    const url = new URL(window.location.href)
    
    Object.entries(params).forEach(([key, value]) => {
      if (value) {
        url.searchParams.set(key, value)
      } else {
        url.searchParams.delete(key)
      }
    })

    if (replace) {
      window.history.replaceState({}, '', url.toString())
    } else {
      window.history.pushState({}, '', url.toString())
    }
  },

  /**
   * 删除URL参数
   * @param names 参数名数组
   * @param replace 是否替换当前历史记录
   */
  remove(names: string[], replace = false): void {
    const url = new URL(window.location.href)
    
    names.forEach(name => {
      url.searchParams.delete(name)
    })

    if (replace) {
      window.history.replaceState({}, '', url.toString())
    } else {
      window.history.pushState({}, '', url.toString())
    }
  },

  /**
   * 获取所有URL参数
   * @param url URL字符串（可选，默认当前页面）
   * @returns 参数对象
   */
  getAll(url?: string): Record<string, string> {
    const urlObj = new URL(url || window.location.href)
    const params: Record<string, string> = {}
    
    urlObj.searchParams.forEach((value, key) => {
      params[key] = value
    })
    
    return params
  }
}

/**
 * 颜色工具
 */
export const colorUtils = {
  /**
   * 十六进制转RGB
   * @param hex 十六进制颜色值
   * @returns RGB对象
   */
  hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  },

  /**
   * RGB转十六进制
   * @param r 红色值
   * @param g 绿色值
   * @param b 蓝色值
   * @returns 十六进制颜色值
   */
  rgbToHex(r: number, g: number, b: number): string {
    return '#' + [r, g, b].map(x => {
      const hex = Math.round(x).toString(16)
      return hex.length === 1 ? '0' + hex : hex
    }).join('')
  },

  /**
   * 获取颜色亮度
   * @param color 颜色值（支持hex和rgb）
   * @returns 亮度值（0-255）
   */
  getLuminance(color: string): number {
    let r: number, g: number, b: number

    if (color.startsWith('#')) {
      const rgb = this.hexToRgb(color)
      if (!rgb) return 0
      r = rgb.r
      g = rgb.g
      b = rgb.b
    } else if (color.startsWith('rgb')) {
      const matches = color.match(/\d+/g)
      if (!matches || matches.length < 3) return 0
      r = parseInt(matches[0])
      g = parseInt(matches[1])
      b = parseInt(matches[2])
    } else {
      return 0
    }

    return 0.299 * r + 0.587 * g + 0.114 * b
  },

  /**
   * 判断颜色是否为深色
   * @param color 颜色值
   * @returns 是否为深色
   */
  isDark(color: string): boolean {
    return this.getLuminance(color) < 128
  }
}