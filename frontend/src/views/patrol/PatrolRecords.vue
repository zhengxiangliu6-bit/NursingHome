<template>
  <div>
    <el-card>
      <template #header>巡更记录</template>
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="task_number" label="任务编号" width="150" />
        <el-table-column prop="route_name" label="路线" width="150" />
        <el-table-column prop="assigned_to_name" label="执行人" width="100" />
        <el-table-column prop="scheduled_start" label="计划时间" width="180" />
        <el-table-column prop="actual_start" label="实际开始" width="180" />
        <el-table-column prop="actual_end" label="实际结束" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="PATROL_STATUS[row.status]?.type" size="small">
              {{ PATROL_STATUS[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPatrolTasks } from '@/api/patrol'
import { PATROL_STATUS } from '@/utils/constants'

const tasks = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const data = await getPatrolTasks()
    tasks.value = data.results || data
  } finally { loading.value = false }
})
</script>
