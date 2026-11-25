<template>
  <Teleport to="body">
    <Transition name="slide-down">
      <div v-if="store.popupVisible && store.currentPopupCall" class="call-alert-popup">
        <div class="popup-card" :class="priorityClass">
          <div class="popup-header">
            <el-icon class="pulse-icon" :size="20"><Bell /></el-icon>
            <span class="popup-title">
              {{ store.currentPopupCall.isEscalation ? '呼叫升级' : '新呼叫' }}
            </span>
            <el-tag :type="priorityTagType" size="small">
              {{ priorityLabel }}
            </el-tag>
            <el-icon class="close-btn" @click="handleDismiss"><Close /></el-icon>
          </div>
          <div class="popup-body">
            <div class="info-row">
              <el-icon><User /></el-icon>
              <span>{{ store.currentPopupCall.caller_name }}</span>
            </div>
            <div v-if="store.currentPopupCall.location_description" class="info-row">
              <el-icon><Location /></el-icon>
              <span>{{ store.currentPopupCall.location_description }}</span>
            </div>
            <div v-if="store.currentPopupCall.isEscalation" class="info-row escalation">
              <el-icon><Warning /></el-icon>
              <span>已升级至: {{ roleLabel(store.currentPopupCall.target_role) }}</span>
            </div>
            <div class="info-row time">
              <el-icon><Clock /></el-icon>
              <span>{{ timeAgo }}</span>
            </div>
          </div>
          <div class="popup-actions">
            <el-button type="primary" size="small" @click="handleAccept">
              <el-icon><Check /></el-icon> 接受处理
            </el-button>
            <el-button size="small" @click="handleDismiss">稍后处理</el-button>
            <el-button size="small" text @click="handleViewCenter">查看详情</el-button>
          </div>
          <div v-if="store.popupQueue.length > 0" class="queue-indicator">
            还有 {{ store.popupQueue.length }} 个呼叫等待查看
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCallAlertStore } from '@/stores/callAlert'
import { acceptCall } from '@/api/callResponse'
import { CALL_PRIORITY } from '@/utils/constants'
import { ElMessage } from 'element-plus'

const store = useCallAlertStore()
const router = useRouter()

const ROLE_LABELS = {
  care_worker: '护工',
  nurse: '护士',
  admin: '管理员',
  super_admin: '超级管理员',
}

const priorityClass = computed(() => store.currentPopupCall?.priority || 'normal')
const priorityTagType = computed(() => CALL_PRIORITY[store.currentPopupCall?.priority]?.type || 'info')
const priorityLabel = computed(() => CALL_PRIORITY[store.currentPopupCall?.priority]?.label || '')
const roleLabel = (role) => ROLE_LABELS[role] || role

const timeAgo = computed(() => {
  const callTime = store.currentPopupCall?.call_time || store.currentPopupCall?.escalated_at
  if (!callTime) return ''
  const diff = Math.floor((Date.now() - new Date(callTime).getTime()) / 1000)
  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  return `${Math.floor(diff / 3600)}小时前`
})

async function handleAccept() {
  const callId = store.currentPopupCall?.id || store.currentPopupCall?.call_id
  if (!callId) return
  try {
    await acceptCall(callId)
    ElMessage.success('已接受呼叫')
    store.dismissPopup()
  } catch {
    ElMessage.error('接受呼叫失败')
  }
}

function handleDismiss() {
  store.dismissPopup()
}

function handleViewCenter() {
  store.dismissPopup()
  router.push('/call-response')
}
</script>

<style lang="scss" scoped>
.call-alert-popup {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  width: 360px;
}

.popup-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  overflow: hidden;
  border-top: 4px solid #409EFF;

  &.emergency { border-top-color: #F56C6C; }
  &.normal { border-top-color: #E6A23C; }
  &.consultation { border-top-color: #409EFF; }
}

.popup-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px 8px;
  font-weight: bold;
  font-size: 15px;

  .close-btn {
    margin-left: auto;
    cursor: pointer;
    color: #909399;
    &:hover { color: #303133; }
  }
}

.pulse-icon {
  color: #F56C6C;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.popup-body {
  padding: 4px 16px 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  padding: 4px 0;
  color: #606266;

  &.escalation { color: #F56C6C; font-weight: 500; }
  &.time { color: #909399; font-size: 12px; }
}

.popup-actions {
  padding: 8px 16px 12px;
  display: flex;
  gap: 8px;
}

.queue-indicator {
  text-align: center;
  padding: 8px;
  background: #f5f7fa;
  font-size: 12px;
  color: #909399;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}
.slide-down-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
