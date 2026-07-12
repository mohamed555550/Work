import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  cart as cartApi,
  chat as chatApi,
  favorites as favoritesApi,
  notifications as notificationsApi,
  orders as ordersApi,
  products as productsApi,
  sellers as sellersApi,
} from '../api'
import { dataOf, listOf } from '../services/response'
import { useAuthStore } from '../stores/authStore'
import { findTrade } from '../data/trades'
import { mediaUrl, publicAsset } from '../utils/assets'
import type {
  AppNotification,
  Category,
  CartItem,
  ChatMessage,
  Conversation,
  Governorate,
  Order,
  Product,
  Seller,
} from '../types/marketplace'

export const queryKeys = {
  products: ['products'] as const,
  chefs: (params?: Record<string, string>) => ['chefs', params || {}] as const,
  cart: ['cart'] as const,
  favorites: ['favorites'] as const,
  orders: ['orders'] as const,
  notifications: ['notifications'] as const,
  chat: (orderId: string) => ['chat', orderId] as const,
  conversations: (search = '') => ['conversations', search] as const,
  locations: ['locations', 'population-order-v3'] as const,
  recommendations: (governorate: string, center: string) => ['recommendations', governorate, center] as const,
  aiSearch: (query: string, governorate: string, center: string) => ['ai-search', query, governorate, center] as const,
}

const fallbackImages = [
  '/backgrounds/trades/01-carpenter.jpg',
  '/backgrounds/trades/02-electrician.jpg',
  '/backgrounds/trades/03-plumber.jpg',
  '/backgrounds/trades/04-painter.jpg',
  '/backgrounds/trades/05-blacksmith.jpg',
  '/backgrounds/trades/06-tiler.jpg',
  '/backgrounds/trades/07-mason.jpg',
  '/backgrounds/trades/08-ac-technician.jpg',
  '/backgrounds/trades/09-appliance-repair.jpg',
  '/backgrounds/trades/10-upholsterer.jpg',
  '/backgrounds/trades/11-aluminum.jpg',
  '/backgrounds/trades/12-glass.jpg',
  '/backgrounds/trades/13-gypsum.jpg',
  '/backgrounds/trades/14-locksmith.jpg',
  '/backgrounds/trades/15-network.jpg',
  '/backgrounds/trades/16-cleaning.jpg',
  '/backgrounds/trades/17-roofing.jpg',
  '/backgrounds/trades/18-mechanic.jpg',
  '/backgrounds/trades/19-mobile-repair.jpg',
  '/backgrounds/trades/20-tailor.jpg',
]

export function fallbackTradeImage(trade?: string, id = 0) {
  if (trade) return publicAsset(findTrade(trade).image)
  return publicAsset(fallbackImages[Math.abs(id) % fallbackImages.length])
}

export function fallbackMealImage(_name: string, _category?: Category, id = 0) {
  return fallbackTradeImage(undefined, id)
}
function mapSeller(raw: any): Seller {
  return {
    id: Number(raw.id),
    name: raw.name,
    governorate: raw.governorate,
    center: raw.center,
    pickupAddress: raw.pickup_address || '',
    bio: raw.food_description || '',
    rating: Number(raw.rating || 0),
    orderCount: Number(raw.order_count || 0),
    productCount: Number(raw.product_count || 0),
    approved: raw.approved === true || raw.approved === 'approved',
    coverImage: raw.cover_image ? mediaUrl(raw.cover_image, fallbackTradeImage(undefined, Number(raw.id))) : fallbackTradeImage(undefined, Number(raw.id)),
    profileImage: raw.profile_image ? mediaUrl(raw.profile_image, fallbackTradeImage(undefined, Number(raw.id))) : null,
    reviewCount: Number(raw.reviews_count || 0),
    followersCount: Number(raw.followers_count || 0),
    experienceYears: Number(raw.experience_years || 0),
    professions: Array.isArray(raw.professions) ? raw.professions : [],
    isOpen: Boolean(raw.is_open),
    workStartTime: raw.work_start_time || '09:00',
    workEndTime: raw.work_end_time || '17:00',
    isOnline: Boolean(raw.is_online),
    isFollowing: Boolean(raw.is_following),
    isFavorite: Boolean(raw.is_favorite),
  }
}

function mapProduct(raw: any): Product {
  const id = Number(raw.id)
  return {
    id,
    name: raw.name,
    description: raw.description || '',
    ingredients: raw.ingredients || '',
    price: Number(raw.price),
    image: mediaUrl(raw.image, fallbackTradeImage(raw.trade, id)),
    category: raw.category,
    preparationTime: Number(raw.preparation_time),
    rating: Number(raw.average_rating || 0),
    reviewCount: Number(raw.review_count || 0),
    sellerId: Number(raw.seller?.id),
    sellerName: raw.seller?.name || '',
    isAvailable: raw.can_order ?? raw.is_available !== false,
    availableAt: raw.available_at || null,
    listingType: raw.listing_type || 'sale',
    trade: raw.trade || '',
    tradeCategory: raw.trade_category || raw.category || '',
  }
}

function mapOrder(raw: any): Order {
  return {
    id: String(raw.id),
    status: raw.status,
    total: Number(raw.total_price),
    createdAt: raw.created_at,
    sellerName: raw.seller_name || '',
    userName: raw.user_name,
    pickupTime: raw.pickup_time,
    pickupAddress: raw.pickup_address || '',
    items: (raw.items || []).map((item: any) => ({
      id: Number(item.id),
      productId: Number(item.product),
      productName: item.product_name,
      productImage: mediaUrl(item.product_image, fallbackMealImage(
        item.product_name,
        undefined,
        Number(item.product),
      )),
      quantity: Number(item.quantity),
      unitPrice: Number(item.unit_price),
    })),
  }
}

function mapNotification(raw: any): AppNotification {
  return {
    id: Number(raw.id),
    title: raw.title,
    content: raw.content,
    type: raw.notification_type,
    read: Boolean(raw.read),
    createdAt: raw.created_at,
    orderId: raw.order ? String(raw.order) : undefined,
  }
}

export function mapChatMessage(item: any): ChatMessage {
  return {
    id: Number(item.id),
    orderId: String(item.order),
    senderId: Number(item.sender),
    senderName: item.sender_name,
    message: item.message || '',
    messageType: item.message_type || 'text',
    image: item.image ? mediaUrl(item.image, '') : null,
    video: item.video ? mediaUrl(item.video, '') : null,
    status: item.status || (item.read_at ? 'seen' : item.delivered_at ? 'delivered' : 'sent'),
    deliveredAt: item.delivered_at || null,
    readAt: item.read_at || null,
    isDeleted: Boolean(item.is_deleted),
    canDeleteForEveryone: Boolean(item.can_delete_for_everyone),
    reply: item.reply ? {
      id: Number(item.reply.id),
      senderName: item.reply.sender_name,
      message: item.reply.message || '',
      messageType: item.reply.message_type || 'text',
    } : null,
    createdAt: item.created_at,
  }
}

export function useProducts(params: Record<string, string | number> = {}) {
  return useQuery({
    queryKey: [...queryKeys.products, params],
    queryFn: async () => {
      const response = await productsApi.list(params)
      const rawProducts = listOf<any>(response)
      return {
        products: rawProducts.map(mapProduct),
        sellers: Array.from(
          new Map(rawProducts.filter((item) => item.seller).map((item) => [item.seller.id, mapSeller(item.seller)])).values(),
        ),
      }
    },
  })
}

export function useProduct(id: number) {
  return useQuery({
    queryKey: ['products', id],
    enabled: Number.isFinite(id),
    queryFn: async () => mapProduct(dataOf<any>(await productsApi.detail(id))),
  })
}

export function useRecommendations(governorate: string, center: string) {
  const authenticated = Boolean(useAuthStore((state) => state.accessToken))
  return useQuery({
    queryKey: queryKeys.recommendations(governorate, center),
    enabled: authenticated,
    staleTime: 5 * 60 * 1000,
    queryFn: async () => {
      const value = dataOf<any>(await productsApi.recommendations({ governorate, center }))
      const rawMeals: any[] = Array.isArray(value.meals) ? value.meals : []
      const rawChefs: any[] = Array.isArray(value.chefs) ? value.chefs : []
      return {
        products: rawMeals.map(mapProduct),
        chefs: rawChefs.map(mapSeller),
        productReasons: Object.fromEntries(
          rawMeals.map((item) => [Number(item.id), item.recommendation_reason]),
        ) as Record<number, string>,
        chefReasons: Object.fromEntries(
          rawChefs.map((item) => [Number(item.id), item.recommendation_reason]),
        ) as Record<number, string>,
      }
    },
  })
}

export function useAISearch(query: string, governorate: string, center: string) {
  return useQuery({
    queryKey: queryKeys.aiSearch(query, governorate, center),
    enabled: query.trim().length >= 2,
    staleTime: 2 * 60 * 1000,
    queryFn: async () => {
      const value = dataOf<any>(await productsApi.aiSearch({ q: query, governorate, center }))
      const rawMeals: any[] = Array.isArray(value.meals) ? value.meals : []
      const rawChefs: any[] = Array.isArray(value.chefs) ? value.chefs : []
      return {
        products: rawMeals.map(mapProduct),
        chefs: rawChefs.map(mapSeller),
        interpretation: value.interpretation as {
          cheap: boolean
          best: boolean
          category: string
          governorate: string
          center: string
        },
      }
    },
  })
}

export function useChefs(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: queryKeys.chefs(params),
    queryFn: async () => listOf<any>(await sellersApi.list(params)).map(mapSeller),
  })
}

export function useChef(id: number) {
  return useQuery({
    queryKey: ['chefs', id],
    enabled: Number.isFinite(id),
    queryFn: async () => mapSeller(dataOf<any>(await sellersApi.detail(id))),
  })
}

export function useLocations() {
  return useQuery({
    queryKey: queryKeys.locations,
    staleTime: 60 * 60 * 1000,
    queryFn: async () => listOf<Governorate>(await sellersApi.locations()),
  })
}

export function useToggleChefFollow() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, following }: { id: number; following: boolean }) => (
      following ? sellersApi.unfollow(id) : sellersApi.follow(id)
    ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['chefs'] }),
  })
}

export function useToggleChefFavorite() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, favorite }: { id: number; favorite: boolean }) => (
      favorite ? sellersApi.unfavorite(id) : sellersApi.favorite(id)
    ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['chefs'] }),
  })
}

export function useCart() {
  const authenticated = Boolean(useAuthStore((state) => state.accessToken))
  return useQuery({
    queryKey: queryKeys.cart,
    enabled: authenticated,
    queryFn: async () => listOf<any>(await cartApi.list()).map((item) => ({
      id: Number(item.id),
      productId: Number(item.product),
      quantity: Number(item.quantity),
      productName: item.product_name || '',
      productPrice: Number(item.product_price || 0),
      preparationTime: Number(item.preparation_time || 0),
      pickupAddress: item.pickup_address || '',
      productImage: mediaUrl(item.product_image, fallbackMealImage(
        item.product_name,
        undefined,
        Number(item.product),
      )),
    })) as CartItem[],
  })
}

export function useFavorites() {
  const authenticated = Boolean(useAuthStore((state) => state.accessToken))
  return useQuery({
    queryKey: queryKeys.favorites,
    enabled: authenticated,
    queryFn: async () => listOf<any>(await favoritesApi.list()).map((item) => ({
      id: Number(item.id),
      productId: Number(item.product),
    })),
  })
}

export function useOrders() {
  const authenticated = Boolean(useAuthStore((state) => state.accessToken))
  return useQuery({
    queryKey: queryKeys.orders,
    enabled: authenticated,
    queryFn: async () => listOf<any>(await ordersApi.list()).map(mapOrder),
  })
}

export function useNotifications() {
  const authenticated = Boolean(useAuthStore((state) => state.accessToken))
  return useQuery({
    queryKey: queryKeys.notifications,
    enabled: authenticated,
    queryFn: async () => {
      const value = dataOf<{ items: any[] }>(await notificationsApi.list())
      return (value.items || []).map(mapNotification)
    },
  })
}

export function useChat(orderId: string) {
  const authenticated = Boolean(useAuthStore((state) => state.accessToken))
  return useQuery({
    queryKey: queryKeys.chat(orderId),
    enabled: authenticated && Boolean(orderId),
    queryFn: async () => {
      const messages = listOf<any>(await chatApi.list(Number(orderId))).map(mapChatMessage)
      await chatApi.markRead(Number(orderId))
      return messages.map((message) => (
        message.senderId === useAuthStore.getState().profile?.id
          ? message
          : { ...message, status: 'seen' as const, readAt: new Date().toISOString() }
      ))
    },
  })
}

export function useConversations(search = '') {
  const authenticated = Boolean(useAuthStore((state) => state.accessToken))
  return useQuery({
    queryKey: queryKeys.conversations(search),
    enabled: authenticated,
    queryFn: async () => listOf<any>(await chatApi.conversations(search)).map((item) => ({
      id: Number(item.id),
      orderId: String(item.order_id),
      otherUser: {
        id: Number(item.other_user.id),
        name: item.other_user.name,
        profileImage: item.other_user.profile_image ? mediaUrl(item.other_user.profile_image, '') : null,
        isOnline: Boolean(item.other_user.is_online),
        lastSeenAt: item.other_user.last_seen_at || null,
      },
      lastMessage: item.last_message ? {
        id: Number(item.last_message.id),
        message: item.last_message.message || '',
        messageType: item.last_message.message_type,
        createdAt: item.last_message.created_at,
      } : null,
      unreadCount: Number(item.unread_count || 0),
      updatedAt: item.updated_at,
    })) as Conversation[],
  })
}

export function useAddToCart() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (productId: number) => {
      const cart = queryClient.getQueryData<CartItem[]>(queryKeys.cart) || []
      const existing = cart.find((item) => item.productId === productId)
      return existing
        ? cartApi.update(existing.id, { product: productId, quantity: existing.quantity + 1 })
        : cartApi.add({ product: productId, quantity: 1 })
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.cart }),
  })
}

export function useUpdateCart() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ item, quantity }: { item: CartItem; quantity: number }) => (
      quantity <= 0
        ? cartApi.remove(item.id)
        : cartApi.update(item.id, { product: item.productId, quantity })
    ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.cart }),
  })
}

export function useToggleFavorite() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (productId: number) => {
      const favorites = queryClient.getQueryData<Array<{ id: number; productId: number }>>(queryKeys.favorites) || []
      const existing = favorites.find((item) => item.productId === productId)
      return existing ? favoritesApi.remove(existing.id) : favoritesApi.add({ product: productId })
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.favorites }),
  })
}

export function useCreateOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ cart, pickupTime }: { cart: CartItem[]; pickupTime: string }) => ordersApi.create({
      idempotency_key: crypto.randomUUID(),
      pickup_time: new Date(pickupTime).toISOString(),
      items: cart.map((item) => ({ product: item.productId, quantity: item.quantity })),
    }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.cart }),
        queryClient.invalidateQueries({ queryKey: queryKeys.orders }),
      ])
    },
  })
}

export function useCancelOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => ordersApi.cancel(Number(id)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.orders }),
  })
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.notifications }),
  })
}

export function useSendMessage(orderId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: { message?: string; image?: File; video?: File; replyTo?: number }) => {
      const hasFile = payload.image || payload.video
      if (hasFile) {
        const form = new FormData()
        form.append('order', orderId)
        if (payload.message) form.append('message', payload.message)
        if (payload.image) form.append('image', payload.image)
        if (payload.video) form.append('video', payload.video)
        if (payload.replyTo) form.append('reply_to', String(payload.replyTo))
        return chatApi.send(form)
      }
      return chatApi.send({
        order: Number(orderId),
        message: payload.message,
        reply_to: payload.replyTo,
      })
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.chat(orderId) }),
        queryClient.invalidateQueries({ queryKey: ['conversations'] }),
      ])
    },
  })
}

export function useDeleteMessage(orderId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, scope }: { id: number; scope: 'me' | 'everyone' }) => (
      chatApi.deleteMessage(id, scope)
    ),
    onSuccess: (_response, variables) => {
      queryClient.setQueryData<ChatMessage[]>(queryKeys.chat(orderId), (current = []) => (
        variables.scope === 'me'
          ? current.filter((item) => item.id !== variables.id)
          : current.map((item) => item.id === variables.id
            ? { ...item, message: '', image: null, video: null, isDeleted: true }
            : item)
      ))
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}

export function useStartChefChat() {
  return useMutation({
    mutationFn: async (chefId: number) => {
      const response = await chatApi.withChef(chefId)
      return dataOf<{ chat_id: number; order_id: number }>(response)
    },
  })
}

export function useSellerApplication() {
  return useMutation({
    mutationFn: (payload: {
      name: string
      governorate: string
      center: string
      food_description: string
      pickup_address: string
      age: number
      national_id: string
      professions: Array<{ trade: string; category: string }>
      work_start_time: string
      work_end_time: string
    }) => sellersApi.apply(payload),
  })
}
