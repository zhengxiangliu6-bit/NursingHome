<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>巡更排班</span>
          <el-button type="primary" @click="dialogVisible = true">新建任务</el-button>
        </div>
      </template>
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="task_number" label="任务编号" width="150" />
        <el-table-column prop="route_name" label="巡更路线" width="150" />
        <el-table-column prop="assigned_to_name" label="执行人" width="100" />
        <el-table-column prop="scheduled_start" label="计划开始" width="180" />
        <el-table-column prop="scheduled_end" label="计划结束" width="180" />
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

    <el-dialog v-model="dialogVisible" title="新建巡更任务" width="500">
      <el-form :model="form" label-width="100px">
        <el-form-item label="巡更路线">
          <el-select v-model="form.route" placeholder="请选择">
            <el-option v-for="r in routes" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行人">
          <el-select v-model="form.assigned_to" filterable placeholder="请选择">
            <el-option v-for="u in staff" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始">
          <el-date-picker v-model="form.scheduled_start" type="datetime" />
        </el-form-item>
        <el-form-item label="计划结束">
          <el-date-picker v-model="form.scheduled_end" type="datetime" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getPatrolTasks, createPatrolTask, getPatrolRoutes } from '@/api/patrol'
import { getUsers } from '@/api/auth'
import { PATROL_STATUS } from '@/utils/constants'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const routes = ref([])
const staff = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ route: '', assigned_to: '', scheduled_start: '', scheduled_end: '' })

async function loadData() {
  loading.value = true
  try {
    const data = await getPatrolTasks()
    tasks.value = data.results || data
  } finally { loading.value = false }
}

async function handleSubmit() {
  await createPatrolTask(form)
  ElMessage.success('任务创建成功')
  dialogVisible.value = false
  loadData()
}

onMounted(async () => {
  loadData()
  const [routeData, userData] = await Promise.all([getPatrolRoutes(), getUsers()])
  routes.value = routeData.results || routeData
  staff.value = (userData.results || userData).filter(u => u.role_name !== '家属')
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
