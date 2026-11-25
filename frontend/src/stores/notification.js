import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const alerts = ref([])
  const unreadCount = ref(0)
  const maxAlerts = 50

  const recentAlerts = computed(() => alerts.value.slice(0, 10))

  function addAlert(alert) {
    alerts.value.unshift({
      ...alert,
      _read: false,
      _receivedAt: new Date().toISOString(),
    })
    if (alerts.value.length > maxAlerts) {
      alerts.value = alerts.value.slice(0, maxAlerts)
    }
    unreadCount.value++

    // 根据严重程度播放告警音
    if (alert.severity === 'critical' || alert.alert_type === 'fall' || alert.alert_type === 'sos') {
      playNotificationSound('emergency')
    } else if (alert.severity === 'warning') {
      playNotificationSound('normal')
    }
  }

  function clearAlerts() {
    alerts.value = []
    unreadCount.value = 0
  }

  function markRead() {
    unreadCount.value = 0
    alerts.value.forEach(a => { a._read = true })
  }

  let audioElement = null
  function playNotificationSound(type) {
    try {
      if (!audioElement) {
        audioElement = new Audio()
      }
      audioElement.src = type === 'emergency'
        ? '/audio/alert-emergency.mp3'
        : '/audio/alert-normal.mp3'
      audioElement.play().catch(() => {})
    } catch { /* 浏览器可能阻止自动播放 */ }
  }

  return { alerts, unreadCount, recentAlerts, addAlert, clearAlerts, markRead }
})
