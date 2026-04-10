<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="aside">
      <div class="logo">
        <el-icon><Message /></el-icon>
        <span>AI 客服</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/personas">
          <el-icon><User /></el-icon>
          <span>人设配置</span>
        </el-menu-item>
        <el-menu-item index="/tg-accounts">
          <el-icon><Connection /></el-icon>
          <span>Telegram</span>
        </el-menu-item>
        <el-menu-item index="/memories">
          <el-icon><Collection /></el-icon>
          <span>记忆管理</span>
        </el-menu-item>
        <el-menu-item index="/conversations">
          <el-icon><ChatDotRound /></el-icon>
          <span>对话记录</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <el-tag :type="tgStatusType">{{ tgStatusText }}</el-tag>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getTgAccounts } from '../api'

const route = useRoute()
const tgAccounts = ref([])

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '仪表盘',
    '/personas': '人设配置',
    '/personas/create': '创建人设',
    '/tg-accounts': 'Telegram 账号',
    '/memories': '记忆管理',
    '/conversations': '对话记录',
    '/settings': '系统设置'
  }
  return titles[route.path] || 'AI 客服'
})

const tgStatusType = computed(() => {
  const online = tgAccounts.value.some(a => a.status === 'online')
  return online ? 'success' : 'info'
})

const tgStatusText = computed(() => {
  const online = tgAccounts.value.filter(a => a.status === 'online').length
  const total = tgAccounts.value.length
  if (total === 0) return '未配置账号'
  return `${online}/${total} 账号在线`
})

onMounted(async () => {
  tgAccounts.value = await getTgAccounts()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid #3d4a5c;
}

.logo .el-icon {
  font-size: 24px;
}

.menu {
  border-right: none;
  background: transparent;
}

.menu :deep(.el-menu-item) {
  color: #bfcbd9;
}

.menu :deep(.el-menu-item:hover),
.menu :deep(.el-menu-item.is-active) {
  background: #263445;
  color: #409eff;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e6e6e6;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
