import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { notifications as notificationsApi } from '../api'
import { useAuthStore } from '../stores/authStore'
import type { AppNotification, ChatMessage } from '../types/marketplace'
import { mapChatMessage, queryKeys } from './useMarketplace'

function websocketUrl(path: string) {
  const configured = import.meta.env.VITE_WS_BASE_URL
  const base = configured || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
  return `${base}${path}`
}

function useManagedSocket(path: string | null, onMessage: (event: MessageEvent) => void) {
  const token = useAuthStore((state) => state.accessToken)
  const socketRef = useRef<WebSocket | null>(null)
  const messageHandler = useRef(onMessage)
  const [connected, setConnected] = useState(false)
  messageHandler.current = onMessage

  useEffect(() => {
    if (!path || !token) return
    let active = true
    let retryTimer: number | undefined
    let retryCount = 0

    const connect = () => {
      const socket = new WebSocket(websocketUrl(path), ['access_token', token])
      socketRef.current = socket
      socket.onopen = () => {
        retryCount = 0
        setConnected(true)
      }
      socket.onmessage = (event) => messageHandler.current(event)
      socket.onclose = () => {
        setConnected(false)
        if (active) {
          retryTimer = window.setTimeout(connect, Math.min(1000 * 2 ** retryCount++, 15_000))
        }
      }
    }

    connect()
    return () => {
      active = false
      if (retryTimer) window.clearTimeout(retryTimer)
      socketRef.current?.close()
    }
  }, [path, token])

  return {
    connected,
    send: (payload: unknown) => {
      if (socketRef.current?.readyState !== WebSocket.OPEN) return false
      socketRef.current.send(JSON.stringify(payload))
      return true
    },
  }
}

function urlBase64ToUint8Array(value: string) {
  const padding = '='.repeat((4 - value.length % 4) % 4)
  const base64 = (value + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = window.atob(base64)
  return Uint8Array.from([...raw].map((char) => char.charCodeAt(0)))
}

export function usePushNotifications() {
  const token = useAuthStore((state) => state.accessToken)

  useEffect(() => {
    if (!token || !('serviceWorker' in navigator) || !('Notification' in window) || !('PushManager' in window)) return
    let active = true

    async function setupPush() {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js')
        if (!active) return

        if (Notification.permission === 'default') {
          await Notification.requestPermission()
        }
        if (Notification.permission !== 'granted') return

        const keyResponse = await notificationsApi.pushPublicKey()
        const publicKey = keyResponse.data?.data?.public_key
        if (!publicKey) return

        const existing = await registration.pushManager.getSubscription()
        const subscription = existing || await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(publicKey),
        })
        await notificationsApi.pushSubscribe(subscription.toJSON())
      } catch {
        // Push is best-effort; websocket notifications still work inside the app.
      }
    }

    setupPush()
    return () => {
      active = false
    }
  }, [token])
}

export function useRealtimeNotifications() {
  const queryClient = useQueryClient()
  return useManagedSocket('/ws/notifications/', (event) => {
    const payload = JSON.parse(event.data)
    if (payload.type !== 'notification.message') return
    const item = payload.data
    const notification: AppNotification = {
      id: Number(item.id),
      title: item.title,
      content: item.content,
      type: item.notification_type,
      read: Boolean(item.read),
      createdAt: item.created_at,
      orderId: item.order ? String(item.order) : undefined,
    }
    queryClient.setQueryData<AppNotification[]>(queryKeys.notifications, (current = []) => (
      current.some((entry) => entry.id === notification.id) ? current : [notification, ...current]
    ))
    if ('Notification' in window && Notification.permission === 'granted' && document.visibilityState !== 'visible') {
      new Notification(notification.title, {
        body: notification.content,
        icon: '/brand/sanati-mark.png',
      })
    }
  })
}

export function useOrderChatSocket(orderId: string) {
  const queryClient = useQueryClient()
  const [typing, setTyping] = useState(false)
  const [otherOnline, setOtherOnline] = useState<boolean | null>(null)
  const [lastSeenAt, setLastSeenAt] = useState<string | null>(null)
  const socket = useManagedSocket(orderId ? `/ws/orders/${orderId}/chat/` : null, (event) => {
    const payload = JSON.parse(event.data)
    if (payload.type === 'chat.message') {
      const message = mapChatMessage(payload.data)
      queryClient.setQueryData<ChatMessage[]>(queryKeys.chat(orderId), (current = []) => (
        current.some((entry) => entry.id === message.id) ? current : [...current, message]
      ))
      socket.send({ action: 'read' })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      return
    }
    if (payload.type === 'chat.status') {
      const ids = new Set<number>((payload.message_ids || []).map(Number))
      queryClient.setQueryData<ChatMessage[]>(queryKeys.chat(orderId), (current = []) => (
        current.map((message) => ids.has(message.id) ? {
          ...message,
          status: payload.status,
          deliveredAt: payload.status === 'delivered' ? payload.timestamp : message.deliveredAt,
          readAt: payload.status === 'seen' ? payload.timestamp : message.readAt,
        } : message)
      ))
      return
    }
    if (payload.type === 'chat.typing') {
      setTyping(Boolean(payload.typing))
      return
    }
    if (payload.type === 'chat.presence') {
      setOtherOnline(Boolean(payload.online))
      setLastSeenAt(payload.last_seen_at || null)
      return
    }
    if (payload.type === 'chat.deleted') {
      queryClient.setQueryData<ChatMessage[]>(queryKeys.chat(orderId), (current = []) => (
        current.map((message) => message.id === Number(payload.message_id)
          ? { ...message, message: '', image: null, video: null, isDeleted: true }
          : message)
      ))
    }
  })
  return {
    connected: socket.connected,
    typing,
    otherOnline,
    lastSeenAt,
    sendMessage: (message: string, replyTo?: number) => socket.send({
      action: 'send',
      message,
      reply_to: replyTo,
    }),
    sendTyping: (value: boolean) => socket.send({ action: 'typing', typing: value }),
    markRead: () => socket.send({ action: 'read' }),
  }
}
