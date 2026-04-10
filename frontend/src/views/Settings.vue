<template>
  <div class="settings">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>

      <el-form :model="form" label-width="140px" class="settings-form">
        <el-divider content-position="left">MiniMax API 配置</el-divider>

        <el-form-item label="API Key">
          <el-input v-model="form.minimax_api_key" type="password" show-password 
                    placeholder="输入 MiniMax API Key" />
        </el-form-item>

        <el-alert
          title="获取 API Key"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          <p>1. 访问 <a href="https://www.minimax.io/" target="_blank">MiniMax 官网</a> 注册账号</p>
          <p>2. 进入控制台创建 API Key</p>
          <p>3. 将 Key 填入上方输入框</p>
        </el-alert>

        <el-divider content-position="left">Telegram API 配置</el-divider>

        <el-form-item label="API ID">
          <el-input v-model="form.tg_api_id" type="number" 
                    placeholder="从 my.telegram.org 获取" />
        </el-form-item>

        <el-form-item label="API Hash">
          <el-input v-model="form.tg_api_hash" type="password" show-password 
                    placeholder="从 my.telegram.org 获取" />
        </el-form-item>

        <el-alert
          title="获取 Telegram API"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          <p>1. 访问 <a href="https://my.telegram.org/" target="_blank">my.telegram.org</a></p>
          <p>2. 登录后进入 "API development tools"</p>
          <p>3. 创建一个应用，获取 App api_id 和 api_hash</p>
        </el-alert>

        <el-divider content-position="left">管理后台设置</el-divider>

        <el-form-item label="管理员用户名">
          <el-input v-model="form.admin_username" placeholder="管理员用户名" />
        </el-form-item>

        <el-form-item label="管理员密码">
          <el-input v-model="form.admin_password" type="password" show-password 
                    placeholder="管理员密码" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="save" :loading="saving">
            保存配置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getConfig, saveConfig } from '../api'

const saving = ref(false)

const form = reactive({
  minimax_api_key: '',
  tg_api_id: '',
  tg_api_hash: '',
  admin_username: 'admin',
  admin_password: 'admin123'
})

async function loadConfig() {
  const data = await getConfig()
  Object.assign(form, data)
}

async function save() {
  saving.value = true
  try {
    await saveConfig(form)
    ElMessage.success('配置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.settings-form {
  max-width: 600px;
}

.settings-form a {
  color: #409eff;
}
</style>
