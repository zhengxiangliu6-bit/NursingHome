<template>
  <div class="call-center">
    <el-row :gutter="20">
      <!-- 待响应 -->
      <el-col :span="8">
        <el-card class="status-column pending">
          <template #header>
            <div class="column-header">
              <el-badge :value="pendingCalls.length" type="danger">
                <span>待响应</span>
              </el-badge>
            </div>
          </template>
          <div v-for="call in pendingCalls" :key="call.id" class="call-card" :class="call.priority">
            <div class="call-info">
              <el-tag :type="priorityType(call.priority)" size="small">{{ priorityLabel(call.priority) }}</el-tag>
              <span class="caller">{{ call.caller_name }}</span>
              <el-tag v-if="call.current_escalation_level > 0" type="danger" size="small" effect="dark">
                升级 L{{ call.current_escalation_level }}
              </el-tag>
            </div>
            <div class="call-meta">
              <span>{{ call.location_description }}</span>
              <span>{{ formatDateTime(call.call_time) }}</span>
            </div>
            <div class="call-actions">
              <el-button type="primary" size="small" @click="handleAccept(call.id)">接受</el-button>
              <el-button v-if="canEscalate" size="small" type="warning" @click="handleEscalate(call.id)">
                手动升级
              </el-button>
            </div>
          </div>
          <el-empty v-if="!pendingCalls.length" description="暂无待响应呼叫" />
        </el-card>
      </el-col>

      <!-- 处理中 -->
      <el-col :span="8">
        <el-card class="status-column processing">
          <template #header>
            <span>处理中 ({{ processingCalls.length }})</span>
          </template>
          <div v-for="call in processingCalls" :key="call.id" class="call-card">
            <div class="call-info">
              <el-tag :type="priorityType(call.priority)" size="small">{{ priorityLabel(call.priority) }}</el-tag>
              <span class="caller">{{ call.caller_name }}</span>
            </div>
            <div class="call-meta">
              <span>{{ call.location_description }}</span>
            </div>
            <el-button type="success" size="small" @click="handleResolve(call.id)">完成</el-button>
          </div>
          <el-empty v-if="!processingCalls.length" description="暂无处理中呼叫" />
        </el-card>
      </el-col>

      <!-- 已解决 -->
      <el-col :span="8">
        <el-card class="status-column resolved">
          <template #header>
            <span>已解决 ({{ resolvedCalls.length }})</span>
          </template>
          <div v-for="call in resolvedCalls" :key="call.id" class="call-card">
            <div class="call-info">
              <el-tag type="success" size="small">已解决</el-tag>
              <span class="caller">{{ call.caller_name }}</span>
            </div>
            <div class="call-meta">
              <span>响应时长: {{ formatDuration(call.response_duration) }}</span>
            </div>
          </div>
          <el-empty v-if="!resolvedCalls.length" description="暂无已解决呼叫" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCalls, acceptCall, resolveCall, escalateCall } from '@/api/callResponse'
import { useCallAlertStore } from '@/stores/callAlert'
import { useAuthStore } from '@/stores/auth'
import { formatDateTime, formatDuration } from '@/utils/formatters'
import { CALL_PRIORITY } from '@/utils/constants'
import { ElMessage } from 'element-plus'

const callAlertStore = useCallAlertStore()
const authStore = useAuthStore()
const recentResolved = ref([])

// 使用全局 store 的实时数据（通过 WebSocket 自动更新）
const pendingCalls = computed(() =>
  callAlertStore.activeCalls.filter(c => c.status === 'pending')
)
const processingCalls = computed(() =>
  callAlertStore.activeCalls.filter(c => ['accepted', 'in_progress'].includes(c.status))
)
const resolvedCalls = computed(() => recentResolved.value.slice(0, 10))

const canEscalate = computed(() => {
  const role = authStore.user?.role
  return ['nurse', 'admin', 'super_admin'].includes(role)
})

const priorityLabel = (p) => CALL_PRIORITY[p]?.label || p
const priorityType = (p) => CALL_PRIORITY[p]?.type || 'info'

async function loadRecentResolved() {
  try {
    const res = await getCalls({ status: 'resolved', page_size: 10, ordering: '-call_time' })
    recentResolved.value = res.results || res
  } catch { /* empty */ }
}

async function handleAccept(id) {
  try {
    await acceptCall(id)
    ElMessage.success('已接受呼叫')
    loadRecentResolved()
  } catch {
    ElMessage.error('接受呼叫失败')
  }
}

async function handleResolve(id) {
  try {
    await resolveCall(id, {})
    ElMessage.success('呼叫已解决')
    loadRecentResolved()
  } catch {
    ElMessage.error('解决呼叫失败')
  }
}

async function handleEscalate(id) {
  try {
    await escalateCall(id)
    ElMessage.success('已手动升级呼叫')
  } catch {
    ElMessage.error('升级呼叫失败')
  }
}

onMounted(() => {
  loadRecentResolved()
})
</script>

<style lang="scss" scoped>
.call-center {
  .status-column {
    min-height: 500px;
  }
  .column-header {
    font-weight: bold;
  }
  .call-card {
    padding: 12px;
    margin-bottom: 12px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    border-left: 4px solid #409EFF;
    &.emergency { border-left-color: #F56C6C; }
    &.normal { border-left-color: #E6A23C; }
    &.consultation { border-left-color: #409EFF; }
  }
  .call-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }
  .caller {
    font-weight: 500;
  }
  .call-meta {
    font-size: 12px;
    color: #909399;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
  }
  .call-actions {
    display: flex;
    gap: 8px;
  }
}
</style>
