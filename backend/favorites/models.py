from django.db import models
from django.conf import settings


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(
        'products.Product', null=True, blank=True, on_delete=models.CASCADE, related_name='favorite_items'
    )
    chef = models.ForeignKey(
        'sellers.SellerProfile', null=True, blank=True, on_delete=models.CASCADE, related_name='favorite_items'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=models.Q(product__isnull=False),
                name='favorite_user_product_uniq',
            ),
            models.UniqueConstraint(
                fields=['user', 'chef'],
                condition=models.Q(chef__isnull=False),
                name='favorite_user_chef_uniq',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(product__isnull=False, chef__isnull=True)
                    | models.Q(product__isnull=True, chef__isnull=False)
                ),
                name='favorite_exactly_one_target',
            ),
        ]

    def __str__(self):
        target = self.product or self.chef
        return f'{self.user.username} favorite {target}'
