import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 响应拦截
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 配置相关
export const getConfig = () => api.get('/config')
export const saveConfig = (data) => api.post('/config', data)

// 人设相关
export const getPersonas = () => api.get('/personas')
export const getPersona = (id) => api.get(`/personas/${id}`)
export const createPersona = (data) => api.post('/personas', data)
export const updatePersona = (id, data) => api.put(`/personas/${id}`, data)
export const getPersonalityOptions = () => api.get('/personas/options/personalities')
export const getStyleOptions = () => api.get('/personas/options/styles')

// TG账号相关
export const getTgAccounts = () => api.get('/tg-accounts')
export const createTgAccount = (data) => api.post('/tg-accounts', data)
export const updateTgAccount = (id, data) => api.put(`/tg-accounts/${id}`, data)
export const connectTgAccount = (id) => api.post(`/tg-accounts/${id}/connect`)
export const disconnectTgAccount = (id) => api.post(`/tg-accounts/${id}/disconnect`)
export const sendTgCode = (id, phone) => api.post(`/tg-accounts/${id}/send-code`, { phone })
export const verifyTgCode = (id, code) => api.post(`/tg-accounts/${id}/verify-code`, { code })

// 记忆相关
export const getMemories = (userId, personaId) => api.get('/memories', { params: { user_id: userId, persona_id: personaId } })
export const addMemory = (data) => api.post('/memories', data)

// 对话相关
export const getConversations = (userId, platform) => api.get('/conversations', { params: { user_id: userId, platform } })
export const getAllConversations = (userId) => api.get('/conversations', { params: { user_id: userId, all: true } })

// 情绪相关
export const getEmotion = (userId, personaId) => api.get('/emotions', { params: { user_id: userId, persona_id: personaId } })

export default api
