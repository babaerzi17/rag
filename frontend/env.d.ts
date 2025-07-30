/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly TAURI_DEBUG: string
  readonly TAURI_PLATFORM: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}