<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>广播控制台</span>
          <el-button type="primary" @click="dialogVisible = true">新建广播</el-button>
        </div>
      </template>
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="broadcast_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ { realtime: '实时', scheduled: '定时', emergency: '紧急' }[row.broadcast_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_type" label="来源" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'broadcasting' ? 'danger' : row.status === 'completed' ? 'success' : 'info'" size="small">
              {{ { draft: '草稿', scheduled: '已计划', broadcasting: '播放中', completed: '已完成', cancelled: '已取消' }[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="100" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button v-if="['draft', 'scheduled'].includes(row.status)" type="success" size="small" @click="handleStart(row.id)">开始播放</el-button>
            <el-button v-if="row.status === 'broadcasting'" type="danger" size="small" @click="handleStop(row.id)">停止</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建广播" width="600">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="广播类型">
          <el-select v-model="form.broadcast_type">
            <el-option label="实时广播" value="realtime" />
            <el-option label="定时广播" value="scheduled" />
            <el-option label="紧急广播" value="emergency" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源类型">
          <el-select v-model="form.source_type">
            <el-option label="语音转文字(TTS)" value="tts" />
            <el-option label="音频文件" value="audio_file" />
          </el-select>
        </el-form-item>
        <el-form-item label="文字内容" v-if="form.source_type === 'tts'">
          <el-input v-model="form.content_text" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="广播分区">
          <el-select v-model="form.zones" multiple>
            <el-option v-for="z in zones" :key="z.id" :label="z.name" :value="z.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getBroadcastTasks, createBroadcastTask, startBroadcast, stopBroadcast, getBroadcastZones } from '@/api/broadcasting'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const zones = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({
  title: '', broadcast_type: 'realtime', source_type: 'tts', content_text: '', zones: []
})

async function loadData() {
  loading.value = true
  try {
    const data = await getBroadcastTasks()
    tasks.value = data.results || data
  } finally { loading.value = false }
}

async function handleCreate() {
  await createBroadcastTask(form)
  ElMessage.success('广播任务创建成功')
  dialogVisible.value = false
  loadData()
}

async function handleStart(id) {
  await startBroadcast(id)
  ElMessage.success('开始播放')
  loadData()
}

async function handleStop(id) {
  await stopBroadcast(id)
  ElMessage.success('已停止')
  loadData()
}

onMounted(async () => {
  loadData()
  zones.value = (await getBroadcastZones()).results || await getBroadcastZones()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
