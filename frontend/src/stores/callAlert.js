import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCallAlertStore = defineStore('callAlert', () => {
  const activeCalls = ref([])
  const currentPopupCall = ref(null)
  const popupVisible = ref(false)
  const popupQueue = ref([])
  const isConnected = ref(false)
  const audioEnabled = ref(true)
  const userRole = ref('')

  let socket = null
  let reconnectTimer = null
  let reconnectAttempts = 0
  let audioElement = null

  function connect() {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const wsBase = import.meta.env.VITE_WS_BASE_URL || `ws://${location.host}/ws`
    const url = `${wsBase}/calls/?token=${token}`

    socket = new WebSocket(url)

    socket.onopen = () => {
      isConnected.value = true
      reconnectAttempts = 0
    }

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      handleMessage(msg)
    }

    socket.onclose = () => {
      isConnected.value = false
      if (reconnectAttempts < 10) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
        reconnectAttempts++
        reconnectTimer = setTimeout(connect, delay)
      }
    }

    socket.onerror = () => {
      socket?.close()
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    reconnectAttempts = Infinity
    socket?.close()
    socket = null
  }

  function handleMessage(msg) {
    switch (msg.type) {
      case 'init':
        activeCalls.value = msg.data.active_calls || []
        userRole.value = msg.data.role || ''
        break

      case 'new_call':
        activeCalls.value.unshift(msg.data)
        showPopup(msg.data)
        playAlertSound(msg.data.priority)
        break

      case 'call_accepted': {
        const idx = activeCalls.value.findIndex(c => c.id === msg.data.call_id)
        if (idx >= 0) activeCalls.value[idx].status = 'accepted'
        if (currentPopupCall.value?.id === msg.data.call_id) {
          dismissPopup()
        }
        break
      }

      case 'call_resolved':
        activeCalls.value = activeCalls.value.filter(c => c.id !== msg.data.call_id)
        if (currentPopupCall.value?.id === msg.data.call_id) dismissPopup()
        break

      case 'call_cancelled':
        activeCalls.value = activeCalls.value.filter(c => c.id !== msg.data.call_id)
        if (currentPopupCall.value?.id === msg.data.call_id) dismissPopup()
        break

      case 'call_escalated': {
        const idx2 = activeCalls.value.findIndex(c => c.id === msg.data.call_id)
        if (idx2 >= 0) {
          activeCalls.value[idx2].current_escalation_level = msg.data.to_level
        }
        showPopup({ ...msg.data, isEscalation: true })
        playAlertSound('emergency')
        break
      }

      case 'call_timeout': {
        const idx3 = activeCalls.value.findIndex(c => c.id === msg.data.call_id)
        if (idx3 >= 0) activeCalls.value[idx3].status = 'timeout'
        break
      }

      case 'pong':
        break
    }
  }

  function showPopup(callData) {
    if (popupVisible.value) {
      popupQueue.value.push(callData)
    } else {
      currentPopupCall.value = callData
      popupVisible.value = true
    }
  }

  function dismissPopup() {
    popupVisible.value = false
    currentPopupCall.value = null
    stopAlertSound()
    if (popupQueue.value.length > 0) {
      const next = popupQueue.value.shift()
      setTimeout(() => showPopup(next), 300)
    }
  }

  function playAlertSound(priority) {
    if (!audioEnabled.value) return
    try {
      if (!audioElement) {
        audioElement = new Audio()
      }
      const soundMap = {
        emergency: '/audio/alert-emergency.mp3',
        normal: '/audio/alert-normal.mp3',
        consultation: '/audio/alert-normal.mp3',
      }
      audioElement.src = soundMap[priority] || soundMap.normal
      audioElement.loop = true
      audioElement.play().catch(() => {})
    } catch {
      // 浏览器可能阻止自动播放
    }
  }

  function stopAlertSound() {
    if (audioElement) {
      audioElement.pause()
      audioElement.currentTime = 0
    }
  }

  const pendingCount = computed(
    () => activeCalls.value.filter(c => c.status === 'pending').length
  )

  return {
    activeCalls, currentPopupCall, popupVisible, popupQueue,
    isConnected, audioEnabled, userRole, pendingCount,
    connect, disconnect, dismissPopup, stopAlertSound,
  }
})
