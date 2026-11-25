<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>跌倒预警</span>
          <el-radio-group v-model="filter" @change="loadData">
            <el-radio-button value="active">活跃告警</el-radio-button>
            <el-radio-button value="all">全部</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table :data="alerts" v-loading="loading" stripe>
        <el-table-column prop="resident_name" label="老人" width="100" />
        <el-table-column prop="alert_time" label="告警时间" width="180" :formatter="(r) => formatDateTime(r.alert_time)" />
        <el-table-column prop="severity" label="严重程度" width="120">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'confirmed' ? 'danger' : 'warning'" size="small">
              {{ { suspected: '疑似', confirmed: '确认', false_alarm: '误报' }[row.severity] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="FALL_ALERT_STATUS[row.status]?.type" size="small">
              {{ FALL_ALERT_STATUS[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location_description" label="位置" />
        <el-table-column prop="handler_name" label="处理人" width="100" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button v-if="row.status === 'alerting'" type="warning" size="small" @click="handleRespond(row.id)">响应</el-button>
            <el-button v-if="row.status === 'responding'" type="success" size="small" @click="handleResolve(row.id)">处理完成</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFallAlerts, getActiveFallAlerts, respondFallAlert, resolveFallAlert } from '@/api/smartDetection'
import { FALL_ALERT_STATUS } from '@/utils/constants'
import { formatDateTime } from '@/utils/formatters'
import { ElMessage } from 'element-plus'

const alerts = ref([])
const loading = ref(false)
const filter = ref('active')

async function loadData() {
  loading.value = true
  try {
    if (filter.value === 'active') {
      alerts.value = await getActiveFallAlerts()
    } else {
      const data = await getFallAlerts()
      alerts.value = data.results || data
    }
  } finally { loading.value = false }
}

async function handleRespond(id) {
  await respondFallAlert(id)
  ElMessage.success('已响应')
  loadData()
}

async function handleResolve(id) {
  await resolveFallAlert(id, { status: 'resolved' })
  ElMessage.success('已处理')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
