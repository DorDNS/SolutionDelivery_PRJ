import { ref } from 'vue'

export const useWebSocket = (url = "ws://localhost:8000/ws/dashboard") => {
  const data = ref(null)
  const socket = new WebSocket(url)

  socket.onmessage = (event) => {
    data.value = JSON.parse(event.data)
  }

  socket.onerror = (e) => {
    console.error("WebSocket error:", e)
  }

  return { data }
}
