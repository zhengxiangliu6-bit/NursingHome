<template>
  <div class="alert-center">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value danger">{{ stats.pending_count || 0 }}</div>
          <div class="stat-label">待处理告警</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value warning">{{ stats.today_count || 0 }}</div>
          <div class="stat-label">今日告警</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value primary">{{ stats.critical_count || 0 }}</div>
          <div class="stat-label">严重告警</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value success">{{ stats.avg_handle_minutes ? stats.avg_handle_minutes + ' 分钟' : '--' }}</div>
          <div class="stat-label">平均处理时长</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 过滤栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" size="default">
        <el-form-item label="类型">
          <el-select v-model="filters.alert_type" clearable placeholder="全部">
            <el-option v-for="(item, key) in ALERT_TYPE" :key="key" :label="item.label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="级别">
          <el-select v-model="filters.severity" clearable placeholder="全部">
            <el-option v-for="(item, key) in ALERT_SEVERITY" :key="key" :label="item.label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部">
            <el-option v-for="(item, key) in ALERT_STATUS" :key="key" :label="item.label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="老人姓名" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadAlerts">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 告警表格 -->
    <el-card>
      <el-table :data="alerts" v-loading="loading" stripe>
        <el-table-column label="级别" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="ALERT_SEVERITY[row.severity]?.type || 'info'" size="small" effect="dark">
              {{ ALERT_SEVERITY[row.severity]?.label || row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            {{ ALERT_TYPE[row.alert_type]?.label || row.alert_type }}
          </template>
        </el-table-column>
        <el-table-column label="标题" prop="title" min-width="160" show-overflow-tooltip />
        <el-table-column label="老人" width="100">
          <template #default="{ row }">
            {{ row.resident_name || '--' }}
          </template>
        </el-table-column>
        <el-table-column label="位置" prop="location_description" width="140" show-overflow-tooltip />
        <el-table-column label="告警时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.alert_time) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="ALERT_STATUS[row.status]?.type || 'info'" size="small">
              {{ ALERT_STATUS[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理人" width="100">
          <template #default="{ row }">
            {{ row.assigned_to_name || '--' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="primary" size="small" link @click="handleAssign(row)">
              指派
            </el-button>
            <el-button v-if="row.status === 'assigned'" type="warning" size="small" link @click="handleStartProcess(row)">
              开始处理
            </el-button>
            <el-button v-if="['assigned','processing'].includes(row.status)" type="success" size="small" link @click="handleResolve(row)">
              解决
            </el-button>
            <el-button v-if="['pending','assigned'].includes(row.status)" type="info" size="small" link @click="handleDismiss(row)">
              忽略
            </el-button>
            <el-button type="primary" size="small" link @click="handleDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadAlerts"
          @current-change="loadAlerts"
        />
      </div>
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="告警详情" size="480px">
      <template v-if="currentAlert">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="告警类型">
            {{ ALERT_TYPE[currentAlert.alert_type]?.label }}
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="ALERT_SEVERITY[currentAlert.severity]?.type" size="small">
              {{ ALERT_SEVERITY[currentAlert.severity]?.label }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="ALERT_STATUS[currentAlert.status]?.type" size="small">
              {{ ALERT_STATUS[currentAlert.status]?.label }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题">{{ currentAlert.title }}</el-descriptions-item>
          <el-descriptions-item label="内容">{{ currentAlert.content }}</el-descriptions-item>
          <el-descriptions-item label="老人">{{ currentAlert.resident_name || '--' }}</el-descriptions-item>
          <el-descriptions-item label="位置">{{ currentAlert.location_description || '--' }}</el-descriptions-item>
          <el-descriptions-item label="告警时间">{{ formatDateTime(currentAlert.alert_time) }}</el-descriptions-item>
          <el-descriptions-item label="处理人">{{ currentAlert.assigned_to_name || '--' }}</el-descriptions-item>
          <el-descriptions-item label="处理结论">{{ currentAlert.resolution || '--' }}</el-descriptions-item>
        </el-descriptions>

        <div class="timeline-section">
          <h4>处理时间线</h4>
          <el-timeline>
            <el-timeline-item
              v-for="log in currentAlert.handle_logs || []"
              :key="log.id"
              :timestamp="formatDateTime(log.created_at)"
              placement="top"
            >
              <p><strong>{{ log.operator_name || '系统' }}</strong> {{ log.action }}</p>
              <p v-if="log.remark" class="log-remark">{{ log.remark }}</p>
              <p class="log-status">{{ log.from_status }} → {{ log.to_status }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </template>
    </el-drawer>

    <!-- 指派弹窗 -->
    <el-dialog v-model="assignVisible" title="指派告警" width="400px">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="指派给">
          <el-select v-model="assignForm.assigned_to" placeholder="选择处理人" filterable>
            <el-option v-for="s in staffList" :key="s.id" :label="s.full_name || s.username" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAssign">确认指派</el-button>
      </template>
    </el-dialog>

    <!-- 解决弹窗 -->
    <el-dialog v-model="resolveVisible" title="解决告警" width="400px">
      <el-form :model="resolveForm" label-width="80px">
        <el-form-item label="处理结论">
          <el-input v-model="resolveForm.resolution" type="textarea" :rows="3" placeholder="请输入处理结论" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmResolve">确认解决</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  getAlerts, getAlert, getAlertStatistics,
  assignAlert, startProcessAlert, resolveAlert, dismissAlert
} from '@/api/alertCenter'
import { useWebSocket } from '@/composables/useWebSocket'
import { formatDateTime } from '@/utils/formatters'
import { ALERT_TYPE, ALERT_SEVERITY, ALERT_STATUS } from '@/utils/constants'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/index'

const loading = ref(false)
const alerts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const stats = ref({})

const filters = ref({
  alert_type: '',
  severity: '',
  status: '',
  dateRange: null,
  search: '',
})

const detailVisible = ref(false)
const currentAlert = ref(null)

const assignVisible = ref(false)
const assignForm = ref({ assigned_to: '' })
const staffList = ref([])
let assigningAlert = null

const resolveVisible = ref(false)
const resolveForm = ref({ resolution: '' })
let resolvingAlert = null

// WebSocket 实时更新
const { messages, connect, disconnect } = useWebSocket('alerts')

async function loadAlerts() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.value.alert_type) params.alert_type = filters.value.alert_type
    if (filters.value.severity) params.severity = filters.value.severity
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.dateRange?.length === 2) {
      params.alert_time_after = filters.value.dateRange[0]
      params.alert_time_before = filters.value.dateRange[1]
    }
    const res = await getAlerts(params)
    alerts.value = res.results || res
    total.value = res.count || alerts.value.length
  } catch { /* empty */ }
  loading.value = false
}

async function loadStats() {
  try {
    stats.value = await getAlertStatistics()
  } catch { /* empty */ }
}

function resetFilters() {
  filters.value = { alert_type: '', severity: '', status: '', dateRange: null, search: '' }
  page.value = 1
  loadAlerts()
}

async function handleDetail(row) {
  try {
    currentAlert.value = await getAlert(row.id)
  } catch {
    currentAlert.value = row
  }
  detailVisible.value = true
}

async function handleAssign(row) {
  assigningAlert = row
  assignForm.value.assigned_to = ''
  // 加载员工列表
  try {
    const res = await request.get('/auth/users/', { params: { role: 'care_worker,nurse,admin', page_size: 100 } })
    staffList.value = res.results || res
  } catch { /* empty */ }
  assignVisible.value = true
}

async function confirmAssign() {
  if (!assignForm.value.assigned_to) {
    ElMessage.warning('请选择处理人')
    return
  }
  try {
    await assignAlert(assigningAlert.id, assignForm.value)
    ElMessage.success('指派成功')
    assignVisible.value = false
    loadAlerts()
    loadStats()
  } catch {
    ElMessage.error('指派失败')
  }
}

async function handleStartProcess(row) {
  try {
    await startProcessAlert(row.id)
    ElMessage.success('已开始处理')
    loadAlerts()
  } catch {
    ElMessage.error('操作失败')
  }
}

function handleResolve(row) {
  resolvingAlert = row
  resolveForm.value.resolution = ''
  resolveVisible.value = true
}

async function confirmResolve() {
  try {
    await resolveAlert(resolvingAlert.id, resolveForm.value)
    ElMessage.success('告警已解决')
    resolveVisible.value = false
    loadAlerts()
    loadStats()
  } catch {
    ElMessage.error('解决失败')
  }
}

async function handleDismiss(row) {
  try {
    await ElMessageBox.confirm('确定忽略此告警？', '提示', { type: 'warning' })
    await dismissAlert(row.id, { remark: '手动忽略' })
    ElMessage.success('已忽略')
    loadAlerts()
    loadStats()
  } catch { /* 取消 */ }
}

// 监听 WS 消息，自动刷新列表
let wsWatcher = null
onMounted(() => {
  loadAlerts()
  loadStats()
  connect()
  wsWatcher = setInterval(() => {
    if (messages.value.length > 0) {
      messages.value = []
      loadAlerts()
      loadStats()
    }
  }, 2000)
})

onUnmounted(() => {
  disconnect()
  if (wsWatcher) clearInterval(wsWatcher)
})
</script>

<style lang="scss" scoped>
.alert-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-row {
  margin-bottom: 0;
}

.stat-card {
  text-align: center;
  .stat-value {
    font-size: 28px;
    font-weight: bold;
    &.danger { color: #F56C6C; }
    &.warning { color: #E6A23C; }
    &.primary { color: #409EFF; }
    &.success { color: #67C23A; }
  }
  .stat-label {
    font-size: 13px;
    color: #909399;
    margin-top: 4px;
  }
}

.filter-card {
  :deep(.el-card__body) {
    padding: 12px 16px;
  }
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.timeline-section {
  margin-top: 24px;
  h4 { margin-bottom: 12px; }
}

.log-remark {
  color: #606266;
  font-size: 13px;
}

.log-status {
  color: #909399;
  font-size: 12px;
}
</style>
