import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const config = ref({
    minimax_api_key: '',
    tg_api_id: '',
    tg_api_hash: '',
    admin_username: 'admin',
    admin_password: 'admin123'
  })

  const personas = ref([])
  const tgAccounts = ref([])
  const currentPersona = ref(null)

  async function loadConfig() {
    const data = await getConfig()
    config.value = data
  }

  async function saveConfig(data) {
    await saveConfigApi(data)
    await loadConfig()
  }

  async function loadPersonas() {
    personas.value = await getPersonas()
  }

  async function loadTgAccounts() {
    tgAccounts.value = await getTgAccounts()
  }

  return {
    config,
    personas,
    tgAccounts,
    currentPersona,
    loadConfig,
    saveConfig,
    loadPersonas,
    loadTgAccounts
  }
})
