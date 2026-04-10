<template>
  <div class="personas">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>人设列表</span>
          <el-button type="primary" @click="$router.push('/personas/create')">
            <el-icon><Plus /></el-icon> 创建人设
          </el-button>
        </div>
      </template>

      <el-table :data="personas" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="personality" label="性格" min-width="150">
          <template #default="{ row }">
            <el-tag v-for="p in parseList(row.personality)" :key="p" size="small" style="margin-right: 4px;">
              {{ p }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="speaking_style" label="风格" min-width="150">
          <template #default="{ row }">
            <el-tag v-for="s in parseList(row.speaking_style)" :key="s" size="small" type="info" style="margin-right: 4px;">
              {{ s }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="$router.push(`/personas/${row.id}/edit`)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="deletePersona(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPersonas, updatePersona } from '../api'

const personas = ref([])

function parseList(value) {
  if (!value) return []
  if (typeof value === 'string') {
    try {
      return JSON.parse(value)
    } catch {
      return value.split(',').map(s => s.trim()).filter(Boolean)
    }
  }
  return value
}

async function deletePersona(id) {
  try {
    await ElMessageBox.confirm('确定要删除这个人设吗？', '提示', {
      type: 'warning'
    })
    await updatePersona(id, { status: 'deleted' })
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 取消删除
  }
}

async function loadData() {
  personas.value = await getPersonas()
}

onMounted(loadData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
