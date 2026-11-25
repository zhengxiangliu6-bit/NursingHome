import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role_name || '')
  const userName = computed(() => {
    if (!user.value) return ''
    return user.value.last_name + user.value.first_name || user.value.username
  })

  async function login(credentials) {
    const data = await loginApi(credentials)
    accessToken.value = data.access
    refreshToken.value = data.refresh
    user.value = data.user
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    router.push('/')
  }

  async function fetchUser() {
    if (!accessToken.value) return
    try {
      const data = await getMe()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  }

  return {
    user, accessToken, refreshToken,
    isLoggedIn, userRole, userName,
    login, fetchUser, logout,
  }
})
