import { ref, onUnmounted } from 'vue'

export function useWebSocket(channel) {
  const socket = ref(null)
  const isConnected = ref(false)
  const messages = ref([])
  let reconnectTimer = null
  let reconnectAttempts = 0

  function connect() {
    const token = localStorage.getItem('access_token')
    const wsBase = import.meta.env.VITE_WS_BASE_URL || `ws://${location.host}/ws`
    const url = `${wsBase}/${channel}/?token=${token}`

    socket.value = new WebSocket(url)

    socket.value.onopen = () => {
      isConnected.value = true
      reconnectAttempts = 0
    }

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      messages.value.push(data)
    }

    socket.value.onclose = () => {
      isConnected.value = false
      // 指数退避重连
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
      reconnectAttempts++
      reconnectTimer = setTimeout(connect, delay)
    }

    socket.value.onerror = () => {
      socket.value?.close()
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    reconnectAttempts = Infinity // 阻止重连
    socket.value?.close()
  }

  function send(data) {
    if (socket.value?.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(data))
    }
  }

  onUnmounted(disconnect)

  return { socket, isConnected, messages, connect, disconnect, send }
}
