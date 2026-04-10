<template>
  <div class="tg-accounts">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Telegram 账号管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon> 添加账号
          </el-button>
        </div>
      </template>

      <el-table :data="accounts" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'info'" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="persona_id" label="绑定人设" width="100">
          <template #default="{ row }">
            {{ getPersonaName(row.persona_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="auto_reply" label="自动回复" width="100">
          <template #default="{ row }">
            <el-tag :type="row.auto_reply ? 'success' : 'info'" size="small">
              {{ row.auto_reply ? '开启' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status !== 'online'" 
              type="success" 
              link 
              size="small" 
              @click="connect(row)"
            >
              连接
            </el-button>
            <el-button 
              v-else 
              type="danger" 
              link 
              size="small" 
              @click="disconnect(row)"
            >
              断开
            </el-button>
            <el-button type="primary" link size="small" @click="editAccount(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="showAddDialog" :title="editingAccount ? '编辑账号' : '添加账号'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="账号名称">
          <el-input v-model="form.name" placeholder="给账号起个名字" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="+86xxxxxxxxxxx" />
        </el-form-item>
        <el-form-item label="API ID">
          <el-input v-model="form.api_id" type="number" placeholder="从 my.telegram.org 获取" />
        </el-form-item>
        <el-form-item label="API Hash">
          <el-input v-model="form.api_hash" placeholder="从 my.telegram.org 获取" />
        </el-form-item>
        <el-form-item label="绑定人设">
          <el-select v-model="form.persona_id" placeholder="选择人设" style="width: 100%">
            <el-option label="无" :value="null" />
            <el-option v-for="p in personas" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="自动回复">
          <el-switch v-model="form.auto_reply" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAccount" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTgAccounts, createTgAccount, updateTgAccount, connectTgAccount, disconnectTgAccount, getPersonas } from '../api'

const accounts = ref([])
const personas = ref([])
const showAddDialog = ref(false)
const editingAccount = ref(null)
const saving = ref(false)

const form = reactive({
  name: '',
  phone: '',
  api_id: '',
  api_hash: '',
  persona_id: null,
  auto_reply: true
})

function statusText(status) {
  const map = { online: '在线', offline: '离线', connecting: '连接中' }
  return map[status] || status
}

function getPersonaName(id) {
  if (!id) return '-'
  const p = personas.value.find(p => p.id === id)
  return p ? p.name : id
}

function resetForm() {
  Object.assign(form, {
    name: '',
    phone: '',
    api_id: '',
    api_hash: '',
    persona_id: null,
    auto_reply: true
  })
}

function editAccount(account) {
  editingAccount.value = account
  Object.assign(form, {
    name: account.name,
    phone: account.phone,
    api_id: account.api_id,
    api_hash: account.api_hash,
    persona_id: account.persona_id,
    auto_reply: !!account.auto_reply
  })
  showAddDialog.value = true
}

async function saveAccount() {
  if (!form.name) {
    ElMessage.warning('请输入账号名称')
    return
  }

  saving.value = true
  try {
    const data = {
      ...form,
      api_id: parseInt(form.api_id) || 0
    }

    if (editingAccount.value) {
      await updateTgAccount(editingAccount.value.id, data)
      ElMessage.success('保存成功')
    } else {
      await createTgAccount(data)
      ElMessage.success('添加成功')
    }

    showAddDialog.value = false
    editingAccount.value = null
    resetForm()
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function connect(account) {
  try {
    const result = await connectTgAccount(account.id)
    if (result.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(result.message || '连接失败')
    }
    loadData()
  } catch (e) {
    ElMessage.error('连接失败')
  }
}

async function disconnect(account) {
  try {
    await disconnectTgAccount(account.id)
    ElMessage.success('已断开')
    loadData()
  } catch (e) {
    ElMessage.error('断开失败')
  }
}

async function loadData() {
  accounts.value = await getTgAccounts()
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
