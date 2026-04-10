<template>
  <div class="memories">
    <el-card>
      <template #header>
        <span>记忆管理</span>
      </template>

      <div class="search-bar">
        <el-input v-model="searchUserId" placeholder="输入用户 ID 搜索记忆" style="width: 300px;">
          <template #append>
            <el-button @click="searchMemories">搜索</el-button>
          </template>
        </el-input>
      </div>

      <el-table v-if="memories.length" :data="memories" stripe style="margin-top: 20px;">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="content" label="记忆内容" min-width="200" />
        <el-table-column prop="importance" label="重要性" width="100">
          <template #default="{ row }">
            <el-tag :type="importanceType(row.importance)" size="small">
              {{ importanceText(row.importance) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_pinned" label="置顶" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_pinned ? 'warning' : 'info'" size="small">
              {{ row.is_pinned ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
      </el-table>

      <el-empty v-else-if="!searched" description="输入用户 ID 查看记忆" />
      <el-empty v-else description="暂无记忆" />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getMemories } from '../api'

const searchUserId = ref('')
const memories = ref([])
const searched = ref(false)

function importanceType(imp) {
  const map = { critical: 'danger', high: 'warning', normal: 'info', low: 'info' }
  return map[imp] || 'info'
}

function importanceText(imp) {
  const map = { critical: '极重要', high: '重要', normal: '普通', low: '低' }
  return map[imp] || imp
}

async function searchMemories() {
  if (!searchUserId.value.trim()) return
  memories.value = await getMemories(searchUserId.value)
  searched.value = true
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 0;
}
</style>
