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
              @click="startAuth(row)"
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

    <!-- 验证码对话框 -->
    <el-dialog v-model="showVerifyDialog" title="验证 Telegram 账号" width="400px" :close-on-click-modal="false">
      <div v-if="verifyStep === 'phone'">
        <p style="margin-bottom: 20px;">请输入手机号（需要与 Telegram 账号绑定）</p>
        <el-form :model="verifyForm" label-width="80px">
          <el-form-item label="手机号">
            <el-input v-model="verifyForm.phone" placeholder="+86138xxxxxxx" />
          </el-form-item>
        </el-form>
      </div>
      <div v-else-if="verifyStep === 'code'">
        <p style="margin-bottom: 20px;">验证码已发送，请输入收到的验证码</p>
        <el-form :model="verifyForm" label-width="80px">
          <el-form-item label="验证码">
            <el-input v-model="verifyForm.code" placeholder="12345" maxlength="5" />
          </el-form-item>
        </el-form>
      </div>
      <div v-else-if="verifyStep === '2fa'">
        <p style="margin-bottom: 20px;">您的账号开启了两步验证，请输入密码</p>
        <el-form :model="verifyForm" label-width="80px">
          <el-form-item label="2FA 密码">
            <el-input v-model="verifyForm.password" type="password" placeholder="输入密码" show-password />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showVerifyDialog = false; verifyStep = 'phone'">取消</el-button>
        <el-button v-if="verifyStep === 'phone'" type="primary" @click="sendCode" :loading="verifying">
          发送验证码
        </el-button>
        <el-button v-else type="primary" @click="submitCode" :loading="verifying">
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTgAccounts, createTgAccount, updateTgAccount, disconnectTgAccount, getPersonas } from '../api'

const accounts = ref([])
const personas = ref([])
const showAddDialog = ref(false)
const editingAccount = ref(null)
const saving = ref(false)
const showVerifyDialog = ref(false)
const verifyStep = ref(false)
const verifying = ref(false)
const currentAuthAccount = ref(null)

const verifyForm = reactive({
  phone: '',
  code: '',
  password: ''
})

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

function startAuth(account) {
  currentAuthAccount.value = account
  verifyStep.value = 'phone'
  verifyForm.phone = account.phone || ''
  verifyForm.code = ''
  verifyForm.password = ''
  showVerifyDialog.value = true
}

async function sendCode() {
  if (!verifyForm.phone) {
    ElMessage.warning('请输入手机号')
    return
  }

  verifying.value = true
  try {
    const result = await fetch(`/api/tg-accounts/${currentAuthAccount.value.id}/send-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: verifyForm.phone })
    }).then(r => r.json())

    if (result.success) {
      verifyStep.value = 'code'  // 切换到输入验证码步骤
      ElMessage.success('验证码已发送')
    } else {
      ElMessage.error(result.error || '发送失败')
    }
  } catch (e) {
    ElMessage.error('发送验证码失败')
  } finally {
    verifying.value = false
  }
}

async function submitCode() {
  if (verifyStep.value === 'code' && !verifyForm.code) {
    ElMessage.warning('请输入验证码')
    return
  }
  if (verifyStep.value === '2fa' && !verifyForm.password) {
    ElMessage.warning('请输入2FA密码')
    return
  }

  verifying.value = true
  try {
    const result = await fetch(`/api/tg-accounts/${currentAuthAccount.value.id}/verify-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: verifyForm.code,
        password: verifyForm.password || undefined
      })
    }).then(r => r.json())

    if (result.success) {
      showVerifyDialog.value = false
      verifyStep.value = 'phone'
      ElMessage.success('验证成功！')
      loadData()
    } else if (result.need_2fa) {
      // 需要2FA密码
      verifyStep.value = '2fa'
      verifyForm.password = ''
      ElMessage.info('请输入2FA密码')
    } else {
      ElMessage.error(result.error || '验证失败')
    }
  } catch (e) {
    ElMessage.error('验证失败')
  } finally {
    verifying.value = false
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
