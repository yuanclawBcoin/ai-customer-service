<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon"><el-icon><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.personas }}</div>
            <div class="stat-label">人设数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon online"><el-icon><Connection /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.tgOnline }}</div>
            <div class="stat-label">TG 在线</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon warning"><el-icon><Warning /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.memories }}</div>
            <div class="stat-label">记忆条目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon success"><el-icon><CircleCheck /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.configured ? '已配置' : '未配置' }}</div>
            <div class="stat-label">API 状态</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>快速开始</span>
          </template>
          <el-steps direction="vertical" :space="60" :active="4">
            <el-step title="配置系统设置" description="在系统设置中填入 MiniMax API Key 和 Telegram API 信息" />
            <el-step title="创建 AI 人设" description="在" />
            <el-step title="连接 Telegram" description="添加 Telegram 账号并连接" />
            <el-step title="开始使用" description="配置完成后，AI 将自动回复消息" />
          </el-steps>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>系统状态</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="API Key">
              <el-tag :type="hasApiKey ? 'success' : 'danger'" size="small">
                {{ hasApiKey ? '已配置' : '未配置' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="TG API">
              <el-tag :type="hasTgApi ? 'success' : 'danger'" size="small">
                {{ hasTgApi ? '已配置' : '未配置' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据库">
              <el-tag type="success" size="small">正常</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getConfig, getPersonas, getTgAccounts } from '../api'

const config = ref({})
const personas = ref([])
const tgAccounts = ref([])

const hasApiKey = computed(() => !!config.value.minimax_api_key)
const hasTgApi = computed(() => !!(config.value.tg_api_id && config.value.tg_api_hash))

const stats = computed(() => ({
  personas: personas.value.length,
  tgOnline: tgAccounts.value.filter(a => a.status === 'online').length,
  memories: 0,
  configured: hasApiKey.value
}))

onMounted(async () => {
  config.value = await getConfig()
  personas.value = await getPersonas()
  tgAccounts.value = await getTgAccounts()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
}

.stat-icon.online {
  background: #67c23a;
}

.stat-icon.warning {
  background: #e6a23c;
}

.stat-icon.success {
  background: #909399;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
</style>
