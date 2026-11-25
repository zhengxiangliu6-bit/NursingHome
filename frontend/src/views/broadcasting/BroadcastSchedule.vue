<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>定时广播计划</span>
          <el-button type="primary" @click="dialogVisible = true">新建计划</el-button>
        </div>
      </template>
      <el-table :data="schedules" v-loading="loading" stripe>
        <el-table-column prop="name" label="计划名称" />
        <el-table-column prop="cron_expression" label="Cron表达式" width="150" />
        <el-table-column prop="source_type" label="来源" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" disabled />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建定时广播" width="500">
      <el-form :model="form" label-width="100px">
        <el-form-item label="计划名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Cron表达式"><el-input v-model="form.cron_expression" placeholder="例: 0 7 * * *" /></el-form-item>
        <el-form-item label="来源类型">
          <el-select v-model="form.source_type">
            <el-option label="TTS" value="tts" />
            <el-option label="音频文件" value="audio_file" />
          </el-select>
        </el-form-item>
        <el-form-item label="文字内容" v-if="form.source_type === 'tts'">
          <el-input v-model="form.content_text" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getBroadcastSchedules, createBroadcastSchedule } from '@/api/broadcasting'
import { ElMessage } from 'element-plus'

const schedules = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ name: '', cron_expression: '', source_type: 'tts', content_text: '' })

async function loadData() {
  loading.value = true
  try {
    const data = await getBroadcastSchedules()
    schedules.value = data.results || data
  } finally { loading.value = false }
}

async function handleCreate() {
  await createBroadcastSchedule(form)
  ElMessage.success('计划创建成功')
  dialogVisible.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
