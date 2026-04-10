<template>
  <div class="conversations">
    <el-row :gutter="20">
      <!-- 左侧：对话列表 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>对话记录</span>
          </template>

          <div class="search-bar">
            <el-input v-model="searchUserId" placeholder="输入用户 ID 搜索对话" style="width: 100%;">
              <template #append>
                <el-button @click="searchConversations">搜索</el-button>
              </template>
            </el-input>
          </div>

          <el-table
            v-if="conversations.length"
            :data="conversations"
            stripe
            style="margin-top: 20px;"
            highlight-current-row
            @row-click="selectConversation"
          >
            <el-table-column prop="user_id" label="用户 ID" min-width="120" />
            <el-table-column prop="updated_at" label="最后活跃" width="150">
              <template #default="{ row }">
                {{ formatTime(row.updated_at) }}
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else-if="!searched" description="输入用户 ID 查看对话记录" />
          <el-empty v-else description="暂无对话记录" />
        </el-card>
      </el-col>

      <!-- 右侧：对话详情 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>对话详情</span>
          </template>

          <div v-if="currentConversation" class="chat-container">
            <div class="chat-messages">
              <div
                v-for="(msg, index) in chatMessages"
                :key="index"
                :class="['message', msg.role]"
              >
                <div class="message-role">{{ msg.role === 'user' ? '用户' : 'AI' }}</div>
                <div class="message-content">{{ msg.content }}</div>
              </div>
            </div>
          </div>

          <el-empty v-else description="选择一个对话查看详情" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getAllConversations } from '../api'
import { ElMessage } from 'element-plus'

const searchUserId = ref('')
const conversations = ref([])
const searched = ref(false)
const currentConversation = ref(null)

async function searchConversations() {
  if (!searchUserId.value.trim()) {
    ElMessage.warning('请输入用户 ID')
    return
  }
  try {
    const data = await getAllConversations(searchUserId.value)
    conversations.value = Array.isArray(data) ? data : [data].filter(Boolean)
    searched.value = true
  } catch (e) {
    ElMessage.error('获取对话记录失败')
  }
}

function selectConversation(row) {
  currentConversation.value = row
}

const chatMessages = computed(() => {
  if (!currentConversation.value || !currentConversation.value.messages) {
    return []
  }

  try {
    const messages = typeof currentConversation.value.messages === 'string'
      ? JSON.parse(currentConversation.value.messages)
      : currentConversation.value.messages

    return messages.map(msg => ({
      role: msg.role || 'unknown',
      content: msg.content || ''
    }))
  } catch (e) {
    return []
  }
})

function formatTime(timeStr) {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 0;
}

.chat-container {
  height: 500px;
  overflow-y: auto;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  position: relative;
}

.message.user {
  align-self: flex-end;
  background: #95ec69;
  color: #000;
}

.message.assistant {
  align-self: flex-start;
  background: #fff;
  color: #000;
  border: 1px solid #ddd;
}

.message-role {
  font-size: 11px;
  color: #999;
  margin-bottom: 4px;
}

.message-content {
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
