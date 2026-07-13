export type UserRole = 'user' | 'seller' | 'admin'
export type Category = string
export type OrderStatus =
  | 'pending'
  | 'confirmed_by_seller'
  | 'preparing'
  | 'ready_for_pickup'
  | 'completed'
  | 'canceled'

export interface UserProfile {
  id: number
  username: string
  email: string
  role: UserRole
  first_name: string
  last_name: string
  is_staff?: boolean
  email_verified: boolean
  profile_image?: string | null
}

export interface Session {
  access: string
  refresh: string
  user: UserProfile
}

export interface Seller {
  id: number
  name: string
  governorate: string
  center: string
  pickupAddress?: string
  bio: string
  rating: number
  orderCount: number
  productCount: number
  approved: boolean
  coverImage: string | null
  profileImage: string | null
  reviewCount: number
  followersCount: number
  experienceYears: number
  professions: Array<{ trade: string; category: string; title?: string; description?: string }>
  isOpen: boolean
  workStartTime: string
  workEndTime: string
  isOnline: boolean
  isFollowing: boolean
  isFavorite: boolean
}

export interface Center {
  id: number
  name: string
  name_ar: string
  name_en: string
  slug: string
}

export interface Governorate {
  id: number
  icon: string
  name: string
  name_ar: string
  name_en: string
  slug: string
  centers: Center[]
}

export interface Product {
  id: number
  name: string
  description: string
  ingredients: string
  price: number
  image: string
  images: string[]
  category: Category
  preparationTime: number
  rating: number
  reviewCount: number
  sellerId: number
  sellerName: string
  isAvailable: boolean
  availableAt: string | null
  listingType?: 'service' | 'sale'
  trade?: string
  tradeCategory?: string
}

export interface CartItem {
  id: number
  productId: number
  quantity: number
  productName: string
  productPrice: number
  productImage: string
  preparationTime: number
  pickupAddress: string
}

export interface OrderItem {
  id: number
  productId: number
  productName: string
  productImage: string
  quantity: number
  unitPrice: number
}

export interface Order {
  id: string
  status: OrderStatus
  total: number
  createdAt: string
  items: OrderItem[]
  sellerName: string
  userName?: string
  pickupTime: string
  pickupAddress: string
}

export interface AppNotification {
  id: number
  title: string
  content: string
  type: 'order_update' | 'message' | 'seller_approval'
  read: boolean
  createdAt: string
  orderId?: string
}

export interface ChatMessage {
  id: number
  orderId: string
  senderId: number
  senderName: string
  message: string
  createdAt: string
  messageType: 'text' | 'image' | 'video'
  image: string | null
  video: string | null
  status: 'sent' | 'delivered' | 'seen'
  deliveredAt: string | null
  readAt: string | null
  isDeleted: boolean
  canDeleteForEveryone: boolean
  reply: {
    id: number
    senderName: string
    message: string
    messageType: 'text' | 'image' | 'video'
  } | null
}

export interface Conversation {
  id: number
  orderId: string
  otherUser: {
    id: number
    name: string
    profileImage: string | null
    isOnline: boolean
    lastSeenAt: string | null
  }
  lastMessage: {
    id: number
    message: string
    messageType: 'text' | 'image' | 'video'
    createdAt: string
  } | null
  unreadCount: number
  updatedAt: string
}

export interface SupportMessage {
  id: number
  sender: number
  senderName: string
  isSupport: boolean
  message: string
  readAt: string | null
  createdAt: string
}

export interface SupportConversation {
  id: number
  user: number
  userName: string
  userEmail: string
  userRole: UserRole
  status: 'open' | 'closed'
  unreadCount: number
  lastMessage: SupportMessage | null
  messages: SupportMessage[]
  createdAt: string
  updatedAt: string
}
