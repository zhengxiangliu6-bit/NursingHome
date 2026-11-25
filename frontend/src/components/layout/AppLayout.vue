<template>
  <el-container class="app-layout">
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="sidebar">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header class="header">
        <HeaderBar />
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
    <!-- 全局呼叫弹窗 -->
    <CallAlertPopup />
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { useCallAlertStore } from '@/stores/callAlert'
import { useNotificationStore } from '@/stores/notification'
import { useWebSocket } from '@/composables/useWebSocket'
import Sidebar from './Sidebar.vue'
import HeaderBar from './HeaderBar.vue'
import CallAlertPopup from '@/components/common/CallAlertPopup.vue'

const appStore = useAppStore()
const callAlertStore = useCallAlertStore()
const notificationStore = useNotificationStore()
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)

// 全局告警WebSocket
const { messages: alertMessages, connect: connectAlerts, disconnect: disconnectAlerts } = useWebSocket('alerts')

// 告警消息推送到通知store
watch(alertMessages, (msgs) => {
  if (msgs.length > 0) {
    const latest = msgs[msgs.length - 1]
    if (latest.action === 'new_alert' || !latest.action) {
      notificationStore.addAlert(latest)
    }
  }
}, { deep: true })

onMounted(() => {
  callAlertStore.connect()
  connectAlerts()
})

onUnmounted(() => {
  callAlertStore.disconnect()
  disconnectAlerts()
})
</script>

<style lang="scss" scoped>
.app-layout {
  height: 100vh;
}

.sidebar {
  background: var(--sidebar-bg);
  transition: width 0.3s;
  overflow-x: hidden;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 56px;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
