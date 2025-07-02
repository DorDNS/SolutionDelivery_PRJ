import { ref } from 'vue'

export const useWebSocket = (url = "ws://localhost:8000/ws/dashboard") => {
  const data = ref(null)

  // Vérifiez si l'environnement est côté client
  if (typeof window !== "undefined") {
    const socket = new WebSocket(url)

    socket.onmessage = (event) => {
      data.value = JSON.parse(event.data)
    }

    socket.onerror = (e) => {
      console.error("WebSocket error:", e)
    }

    socket.onclose = () => {
      console.warn("WebSocket connection closed")
    }
  } else {
    console.warn("WebSocket is not available in SSR")
  }

  return { data }
}
