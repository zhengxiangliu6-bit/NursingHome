<template>
  <div class="header-bar">
    <div class="left">
      <el-icon class="collapse-btn" @click="appStore.toggleSidebar">
        <Fold v-if="!appStore.sidebarCollapsed" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="route.meta.title">
          {{ route.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="right">
      <!-- 呼叫待处理数 -->
      <el-badge :value="callAlertStore.pendingCount" :hidden="callAlertStore.pendingCount === 0" class="action-badge">
        <el-icon class="action-icon" @click="$router.push('/call-response')">
          <Phone />
        </el-icon>
      </el-badge>

      <!-- 告警通知铃铛 -->
      <el-popover placement="bottom-end" :width="360" trigger="click" @show="notificationStore.markRead">
        <template #reference>
          <el-badge :value="notificationStore.unreadCount" :hidden="notificationStore.unreadCount === 0" class="action-badge">
            <el-icon class="action-icon">
              <Bell />
            </el-icon>
          </el-badge>
        </template>
        <div class="notification-panel">
          <div class="panel-header">
            <span>通知</span>
            <el-button type="primary" link size="small" @click="notificationStore.clearAlerts">清空</el-button>
          </div>
          <div class="panel-body">
            <div v-if="notificationStore.recentAlerts.length === 0" class="empty-tip">暂无通知</div>
            <div
              v-for="(alert, idx) in notificationStore.recentAlerts"
              :key="idx"
              class="notification-item"
              :class="{ unread: !alert._read }"
            >
              <div class="notif-title">
                <el-tag :type="severityType(alert.severity)" size="small" effect="dark">
                  {{ severityLabel(alert.severity) }}
                </el-tag>
                <span>{{ alert.title || alertTypeLabel(alert.alert_type) || '新告警' }}</span>
              </div>
              <div class="notif-content">{{ alert.content || alert.location_description || '' }}</div>
              <div class="notif-time">{{ formatTime(alert._receivedAt || alert.alert_time) }}</div>
            </div>
          </div>
          <div class="panel-footer">
            <el-button type="primary" link @click="$router.push('/smart-detection/alert-center')">
              查看全部
            </el-button>
          </div>
        </div>
      </el-popover>

      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" icon="UserFilled" />
          <span class="username">{{ authStore.userName }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人信息</el-dropdown-item>
            <el-dropdown-item command="password">修改密码</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { useCallAlertStore } from '@/stores/callAlert'
import { ALERT_SEVERITY, ALERT_TYPE } from '@/utils/constants'

const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const callAlertStore = useCallAlertStore()

const severityType = (s) => ALERT_SEVERITY[s]?.type || 'info'
const severityLabel = (s) => ALERT_SEVERITY[s]?.label || s || ''
const alertTypeLabel = (t) => ALERT_TYPE[t]?.label || t || ''

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffMin < 1440) return `${Math.floor(diffMin / 60)}小时前`
  return d.toLocaleDateString()
}

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
  }
}
</script>

<style lang="scss" scoped>
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  &:hover { color: var(--el-color-primary); }
}

.right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-icon {
  font-size: 20px;
  cursor: pointer;
  &:hover { color: var(--el-color-primary); }
}

.action-badge {
  line-height: 1;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
}

/* 通知面板 */
.notification-panel {
  margin: -12px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  font-weight: bold;
  font-size: 14px;
}

.panel-body {
  max-height: 360px;
  overflow-y: auto;
}

.empty-tip {
  padding: 40px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}

.notification-item {
  padding: 10px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  &:hover { background: #f5f7fa; }
  &.unread { background: #ecf5ff; }
}

.notif-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
}

.notif-content {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notif-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
}

.panel-footer {
  text-align: center;
  padding: 8px;
  border-top: 1px solid #ebeef5;
}
</style>
