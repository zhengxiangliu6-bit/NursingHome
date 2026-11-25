<template>
  <div>
    <el-card>
      <template #header>实时巡更监控</template>
      <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
        实时显示当前正在进行的巡更任务，巡更人员位置通过WebSocket推送更新。
      </el-alert>
      <el-table :data="activeTasks" v-loading="loading" stripe>
        <el-table-column prop="task_number" label="任务编号" width="150" />
        <el-table-column prop="route_name" label="路线" width="150" />
        <el-table-column prop="assigned_to_name" label="执行人" width="100" />
        <el-table-column prop="actual_start" label="开始时间" width="180" />
        <el-table-column prop="progress" label="完成进度" width="100" />
        <el-table-column label="状态" width="100">
          <template #default>
            <el-tag type="warning" effect="dark" size="small">巡更中</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPatrolTasks } from '@/api/patrol'
import { useWebSocket } from '@/composables/useWebSocket'

const activeTasks = ref([])
const loading = ref(false)
const { connect } = useWebSocket('patrol')

onMounted(async () => {
  loading.value = true
  try {
    const data = await getPatrolTasks({ status: 'in_progress' })
    activeTasks.value = data.results || data
  } finally { loading.value = false }
  connect()
})
</script>
