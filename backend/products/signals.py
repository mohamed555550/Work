from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from favorites.models import Favorite
from orders.models import Order, OrderItem
from reviews.models import Review
from sellers.models import Follower
from .models import SearchHistory
from .recommendations import invalidate_recommendations


@receiver([post_save, post_delete], sender=Favorite, dispatch_uid='recommendations.favorite')
def favorite_changed(sender, instance, **kwargs):
    invalidate_recommendations(instance.user_id)


@receiver([post_save, post_delete], sender=Follower, dispatch_uid='recommendations.follower')
def follower_changed(sender, instance, **kwargs):
    invalidate_recommendations(instance.customer_id)


@receiver([post_save, post_delete], sender=Review, dispatch_uid='recommendations.review')
def review_changed(sender, instance, **kwargs):
    invalidate_recommendations(instance.user_id)


@receiver([post_save, post_delete], sender=SearchHistory, dispatch_uid='recommendations.search')
def search_changed(sender, instance, **kwargs):
    invalidate_recommendations(instance.user_id)


@receiver([post_save, post_delete], sender=Order, dispatch_uid='recommendations.order')
def order_changed(sender, instance, **kwargs):
    invalidate_recommendations(instance.user_id)


@receiver([post_save, post_delete], sender=OrderItem, dispatch_uid='recommendations.order_item')
def order_item_changed(sender, instance, **kwargs):
    user_id = Order.objects.filter(pk=instance.order_id).values_list('user_id', flat=True).first()
    if user_id:
        invalidate_recommendations(user_id)
