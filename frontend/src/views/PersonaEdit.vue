<template>
  <div class="persona-edit">
    <el-card>
      <template #header>
        <span>{{ isEdit ? '编辑人设' : '创建人设' }}</span>
      </template>

      <el-form :model="form" label-width="100px" class="persona-form">
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="名称">
              <el-input v-model="form.name" placeholder="给AI起个名字" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" placeholder="选择性别" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
                <el-option label="未知" value="未知" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年龄">
              <el-input v-model="form.age" placeholder="年龄或年龄段" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业领域">
              <el-input v-model="form.expertise" placeholder="如：电商客服、金融咨询" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">性格配置</el-divider>

        <el-form-item label="性格标签">
          <el-select v-model="form.personality" multiple placeholder="选择性格特点" style="width: 100%">
            <el-option v-for="p in personalityOptions" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>

        <el-form-item label="说话风格">
          <el-select v-model="form.speaking_style" multiple placeholder="选择说话风格" style="width: 100%">
            <el-option v-for="s in styleOptions" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>

        <el-form-item label="性格描述">
          <el-input v-model="form.personality_desc" type="textarea" :rows="2" 
                    placeholder="补充描述AI的性格特点（可选）" />
        </el-form-item>

        <el-divider content-position="left">对话配置</el-divider>

        <el-form-item label="开场白">
          <el-input v-model="form.greeting" type="textarea" :rows="2" 
                    placeholder="AI 第一次对话时的开场白" />
        </el-form-item>

        <el-form-item label="结束语">
          <el-input v-model="form.farewell" type="textarea" :rows="2" 
                    placeholder="对话结束时说的话" />
        </el-form-item>

        <el-form-item label="未知回复">
          <el-input v-model="form.unknown_response" type="textarea" :rows="2" 
                    placeholder="遇到无法回答的问题时的回复" />
        </el-form-item>

        <el-divider content-position="left">个性化设置（让人设更独特）</el-divider>

        <el-form-item label="口头禅">
          <el-input v-model="form.habits" placeholder="如：哈哈哈、嘛、嗯嗯、卧槽（用顿号分隔）" />
          <div class="form-tip">设置AI常用的口头禅，让回复更有特色</div>
        </el-form-item>

        <el-form-item label="常用emoji">
          <el-input v-model="form.favorite_emoji" placeholder="如：😂、😏、😭（用顿号分隔）" />
          <div class="form-tip">AI会偶尔使用这些emoji</div>
        </el-form-item>

        <el-form-item label="说话节奏">
          <el-select v-model="form.speaking_speed" placeholder="选择说话节奏" style="width: 100%">
            <el-option label="快速" value="fast" />
            <el-option label="正常" value="normal" />
            <el-option label="慢悠悠" value="slow" />
          </el-select>
        </el-form-item>

        <el-form-item label="消息长度">
          <el-select v-model="form.message_length" placeholder="选择消息长度" style="width: 100%">
            <el-option label="很短（1句话）" value="very_short" />
            <el-option label="短（1-2句）" value="short" />
            <el-option label="正常（2-3句）" value="normal" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="save" :loading="saving">
            {{ isEdit ? '保存修改' : '创建人设' }}
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPersona, createPersona, updatePersona, getPersonalityOptions, getStyleOptions } from '../api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)

const form = reactive({
  name: '',
  gender: '未知',
  age: '',
  expertise: '',
  personality: [],
  speaking_style: [],
  personality_desc: '',
  greeting: '',
  farewell: '',
  unknown_response: '',
  habits: '',
  favorite_emoji: '',
  speaking_speed: 'normal',
  message_length: 'short'
})

const personalityOptions = ref([])
const styleOptions = ref([])

async function loadOptions() {
  personalityOptions.value = await getPersonalityOptions()
  styleOptions.value = await getStyleOptions()
}

async function loadData() {
  if (isEdit.value) {
    const data = await getPersona(route.params.id)
    form.name = data.name || ''
    form.gender = data.gender || '未知'
    form.age = data.age || ''
    form.expertise = data.expertise || ''
    form.personality = parseList(data.personality)
    form.speaking_style = parseList(data.speaking_style)
    form.greeting = data.greeting || ''
    form.farewell = data.farewell || ''
    form.unknown_response = data.unknown_response || ''
    form.habits = parseList(data.habits).join('、')
    form.favorite_emoji = parseList(data.favorite_emoji).join('、')
    form.speaking_speed = data.speaking_speed || 'normal'
    form.message_length = data.message_length || 'short'
  }
}

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

async function save() {
  if (!form.name) {
    ElMessage.warning('请输入名称')
    return
  }

  saving.value = true
  try {
    // 处理口头禅和emoji，转换为数组
    const habitsArray = form.habits ? form.habits.split('、').map(s => s.trim()).filter(Boolean) : []
    const emojiArray = form.favorite_emoji ? form.favorite_emoji.split('、').map(s => s.trim()).filter(Boolean) : []

    const data = {
      name: form.name,
      gender: form.gender,
      age: form.age,
      expertise: form.expertise,
      personality: JSON.stringify(form.personality),
      speaking_style: JSON.stringify(form.speaking_style),
      personality_desc: form.personality_desc,
      greeting: form.greeting,
      farewell: form.farewell,
      unknown_response: form.unknown_response,
      habits: JSON.stringify(habitsArray),
      favorite_emoji: JSON.stringify(emojiArray),
      speaking_speed: form.speaking_speed,
      message_length: form.message_length
    }

    if (isEdit.value) {
      await updatePersona(route.params.id, data)
      ElMessage.success('保存成功')
    } else {
      await createPersona(data)
      ElMessage.success('创建成功')
    }
    router.push('/personas')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  loadData()
})
</script>

<style scoped>
.persona-form {
  max-width: 800px;
}
.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
