<template>
  <div>
    <el-card>
      <template #header>广播日志</template>
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="task_title" label="广播任务" />
        <el-table-column prop="action" label="操作" width="120" />
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="details" label="详情" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getBroadcastLogs } from '@/api/broadcasting'

const logs = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const data = await getBroadcastLogs()
    logs.value = data.results || data
  } finally { loading.value = false }
})
</script>
