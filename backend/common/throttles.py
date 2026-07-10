from rest_framework.throttling import UserRateThrottle


class AuthRateThrottle(UserRateThrottle):
    scope = 'auth'


class OrderCreationThrottle(UserRateThrottle):
    scope = 'order_create'


class ReviewCreationThrottle(UserRateThrottle):
    scope = 'review_create'
