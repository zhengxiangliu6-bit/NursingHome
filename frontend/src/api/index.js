import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
})

// 请求拦截器：自动携带 JWT Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：处理错误和Token刷新
request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const { response } = error
    if (response) {
      switch (response.status) {
        case 401:
          // Token 过期，尝试刷新
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken && !error.config._retry) {
            error.config._retry = true
            try {
              const res = await axios.post(
                `${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/auth/token/refresh/`,
                { refresh: refreshToken }
              )
              localStorage.setItem('access_token', res.data.access)
              error.config.headers.Authorization = `Bearer ${res.data.access}`
              return request(error.config)
            } catch {
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              router.push('/login')
            }
          } else {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            router.push('/login')
          }
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(response.data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request
