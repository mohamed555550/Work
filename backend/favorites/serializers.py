from rest_framework import serializers
from .models import Favorite
from products.models import Product


class FavoriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True,
    )
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'created_at']
        read_only_fields = ['product_name', 'product_price', 'product_image', 'created_at']

    def validate_product(self, value):
        if not value.is_available or not value.seller.is_active_seller:
            raise serializers.ValidationError('هذا المنتج غير متاح حالياً')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        favorite, _ = Favorite.objects.get_or_create(user=user, product=validated_data['product'])
        return favorite
