from rest_framework import serializers
from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    product_image = serializers.ImageField(source='product.image', read_only=True)
    preparation_time = serializers.ReadOnlyField(source='product.preparation_time')
    pickup_address = serializers.ReadOnlyField(source='product.seller.pickup_address')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_price', 'product_image',
            'preparation_time', 'pickup_address', 'quantity', 'total_price',
        ]

    def validate_product(self, value):
        if not value.can_order or not value.seller.is_active_seller:
            raise serializers.ValidationError('هذا المنتج غير متاح حالياً')
        if self.instance and value.pk != self.instance.product_id:
            raise serializers.ValidationError('لا يمكن تغيير منتج عنصر موجود في السلة')
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('يجب أن تكون الكمية 1 على الأقل')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs.get('product') or getattr(self.instance, 'product', None)
        existing_items = CartItem.objects.filter(user=user)
        if self.instance:
            existing_items = existing_items.exclude(pk=self.instance.pk)
        if product and existing_items.exclude(product__seller_id=product.seller_id).exists():
            raise serializers.ValidationError('يجب أن تحتوي السلة على منتجات من عامل واحد')
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        item, _ = CartItem.objects.update_or_create(
            user=user,
            product=validated_data['product'],
            defaults={'quantity': validated_data['quantity']},
        )
        return item
