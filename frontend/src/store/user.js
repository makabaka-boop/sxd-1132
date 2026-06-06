import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const login = async (loginData) => {
    const res = await loginApi(loginData)
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const fetchCurrentUser = async () => {
    if (token.value) {
      try {
        const res = await getCurrentUser()
        user.value = res
        localStorage.setItem('user', JSON.stringify(res))
      } catch (e) {
        logout()
      }
    }
  }

  const isAdmin = () => user.value?.role === 'admin'
  const isAuditor = () => user.value?.role === 'auditor'
  const isUser = () => user.value?.role === 'user'

  return {
    token,
    user,
    login,
    logout,
    fetchCurrentUser,
    isAdmin,
    isAuditor,
    isUser
  }
})
