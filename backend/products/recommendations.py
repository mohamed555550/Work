import math
import re
import unicodedata
from collections import Counter
from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone

from favorites.models import Favorite
from orders.models import OrderItem
from reviews.models import Review
from sellers.models import Center, Follower, Governorate, SellerProfile
from .models import Product, SearchHistory


CATEGORY_TERMS = {
    'breakfast': {'breakfast', 'فطار', 'افطار', 'إفطار', 'صباحي'},
    'lunch': {'lunch', 'غداء', 'غدا'},
    'dinner': {'dinner', 'عشاء', 'عشا'},
    'healthy': {'healthy', 'health', 'صحي', 'صحية', 'دايت', 'diet', 'keto', 'كيتو'},
    'dessert': {'dessert', 'desserts', 'sweet', 'sweets', 'حلويات', 'حلو', 'كيك', 'cake'},
}

TERM_EXPANSIONS = {
    'mahshi': {'mahshi', 'محشي', 'محاشي'},
    'محشي': {'mahshi', 'محشي', 'محاشي'},
    'grilled': {'grilled', 'grill', 'مشوي', 'مشوية', 'شواية'},
    'مشوي': {'grilled', 'grill', 'مشوي', 'مشوية', 'شواية'},
    'chicken': {'chicken', 'فراخ', 'دجاج', 'فراخ مشوية'},
    'فراخ': {'chicken', 'فراخ', 'دجاج'},
    'homemade': {'homemade', 'home', 'منزلي', 'بيتي', 'بيتيه'},
}

STOP_WORDS = {
    'i', 'want', 'a', 'an', 'the', 'in', 'near', 'me', 'worker', 'service',
    'اريد', 'أريد', 'عايز', 'عايزة', 'في', 'من', 'عن', 'عامل', 'خدمة',
}

CHEAP_TERMS = {'cheap', 'budget', 'affordable', 'رخيص', 'رخيصة', 'اقتصادي', 'اقتصادية'}
BEST_TERMS = {'best', 'top', 'highest', 'افضل', 'أفضل', 'احسن', 'أحسن'}

CENTER_ALIASES = {
    'mansoura': 'المنصورة',
    'cairo': 'القاهرة',
    'alexandria': 'الإسكندرية',
    'giza': 'الجيزة',
    'minya': 'مركز المنيا',
    'tanta': 'طنطا',
    'zagazig': 'الزقازيق',
    'aswan': 'أسوان',
    'luxor': 'الأقصر',
}


def recommendation_version(user_id):
    from django.core.cache import cache

    return cache.get(f'recommendations:version:{user_id}', 1)


def invalidate_recommendations(user_id):
    from django.core.cache import cache

    key = f'recommendations:version:{user_id}'
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 2, timeout=None)


def normalize_text(value):
    value = unicodedata.normalize('NFKC', value or '').lower().strip()
    value = re.sub(r'[\u064b-\u065f\u0670]', '', value)
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    return re.sub(r'[^\w\u0600-\u06ff]+', ' ', value).strip()


def _tokens(value):
    return {token for token in normalize_text(value).split() if len(token) > 1 and token not in STOP_WORDS}


def _base_products():
    since = timezone.now() - timedelta(days=30)
    return list(
        Product.objects.filter(is_available=True, seller__approved='approved')
        .select_related('seller', 'seller__user')
        .annotate(
            rating_value=Avg('reviews__rating'),
            rating_count=Count('reviews', distinct=True),
            favorite_count=Count('favorite_items', distinct=True),
            recent_order_count=Count(
                'orderitem',
                filter=Q(
                    orderitem__order__status='completed',
                    orderitem__order__created_at__gte=since,
                ),
                distinct=True,
            ),
        )[:300]
    )


def _base_chefs():
    since = timezone.now() - timedelta(days=30)
    return list(
        SellerProfile.objects.filter(approved='approved')
        .select_related('user')
        .annotate(
            rating_value=Avg('products__reviews__rating'),
            reviews_count_value=Count('products__reviews', distinct=True),
            followers_count_value=Count('followers', distinct=True),
            product_count_value=Count(
                'products',
                filter=Q(products__is_available=True),
                distinct=True,
            ),
            recent_order_count=Count(
                'orders',
                filter=Q(orders__status='completed', orders__created_at__gte=since),
                distinct=True,
            ),
        )[:200]
    )


def _location_from_query(normalized):
    for alias, name in CENTER_ALIASES.items():
        if alias in normalized:
            return '', name
    centers = Center.objects.filter(is_active=True).select_related('governorate')
    for center in centers:
        if normalize_text(center.name_ar) in normalized or normalize_text(center.name_en) in normalized:
            return center.governorate.name_ar, center.name_ar
    for governorate in Governorate.objects.filter(is_active=True):
        if normalize_text(governorate.name_ar) in normalized or normalize_text(governorate.name_en) in normalized:
            return governorate.name_ar, ''
    return '', ''


def interpret_query(query):
    normalized = normalize_text(query)
    tokens = _tokens(normalized)
    matched_categories = [
        key for key, terms in CATEGORY_TERMS.items()
        if tokens.intersection({normalize_text(term) for term in terms})
    ]
    category = 'healthy' if 'healthy' in matched_categories else (
        matched_categories[0] if matched_categories else ''
    )
    governorate, center = _location_from_query(normalized)
    expanded = set(tokens)
    for token in list(tokens):
        expanded.update(normalize_text(term) for term in TERM_EXPANSIONS.get(token, set()))
    consumed_category_terms = {
        normalize_text(term)
        for key in matched_categories
        for term in CATEGORY_TERMS[key]
    }
    consumed_locations = {
        token for token in expanded
        if token in CENTER_ALIASES
        or (governorate and token in normalize_text(governorate))
        or (center and token in normalize_text(center))
    }
    intent = {
        'cheap': bool(tokens.intersection(CHEAP_TERMS)),
        'best': bool(tokens.intersection({normalize_text(term) for term in BEST_TERMS})),
        'category': category,
        'governorate': governorate,
        'center': center,
        'terms': expanded - CHEAP_TERMS - BEST_TERMS - consumed_category_terms - consumed_locations,
    }
    return normalized, intent


def semantic_search(query, governorate='', center=''):
    normalized, intent = interpret_query(query)
    governorate = intent['governorate'] or governorate
    center = intent['center'] or center
    category = intent['category']
    terms = intent['terms']
    products = _base_products()
    chefs = _base_chefs()

    def location_score(chef):
        if center and normalize_text(chef.center) != normalize_text(center):
            return -100
        if governorate and normalize_text(chef.governorate) != normalize_text(governorate):
            return -100
        return 5 if center else 3 if governorate else 0

    meal_results = []
    for product in products:
        if category and product.category != category:
            continue
        score = location_score(product.seller)
        if score < 0:
            continue
        haystack = normalize_text(f'{product.name} {product.description} {product.seller.name}')
        matched = sum(1 for term in terms if term and term in haystack)
        if terms and matched == 0:
            continue
        score += matched * 5
        score += float(product.rating_value or 0) * (1.4 if intent['best'] else 0.6)
        score += math.log1p(product.recent_order_count) * 1.2
        score += math.log1p(product.favorite_count) * 0.5
        if intent['cheap']:
            score += max(0, 4 - float(product.price) / 75)
        product.ai_score = round(score, 3)
        product.recommendation_reason = (
            'أفضل تطابق مع بحثك'
            if matched
            else 'يناسب الفئة والموقع المطلوبين'
        )
        meal_results.append(product)

    chef_results = []
    for chef in chefs:
        score = location_score(chef)
        if score < 0:
            continue
        haystack = normalize_text(f'{chef.name} {chef.food_description}')
        own_categories = {item.category for item in products if item.seller_id == chef.id}
        own_text = ' '.join(
            normalize_text(f'{item.name} {item.description}')
            for item in products if item.seller_id == chef.id
        )
        if category and category not in own_categories:
            continue
        matched = sum(1 for term in terms if term and (term in haystack or term in own_text))
        if terms and matched == 0:
            continue
        score += matched * 4
        score += float(chef.rating_value or 0) * (1.6 if intent['best'] else 0.7)
        score += math.log1p(chef.followers_count_value) * 0.7
        score += math.log1p(chef.recent_order_count)
        chef.ai_score = round(score, 3)
        chef.recommendation_reason = (
            'متخصص في طلبك'
            if matched or category
            else 'تقييمات قوية في موقعك'
        )
        chef_results.append(chef)

    meal_results.sort(key=lambda item: (-item.ai_score, float(item.price) if intent['cheap'] else -item.id))
    chef_results.sort(key=lambda item: (-item.ai_score, item.name))
    return {
        'normalized_query': normalized,
        'interpretation': {
            key: value for key, value in intent.items() if key != 'terms'
        } | {'governorate': governorate, 'center': center},
        'meals': meal_results[:24],
        'chefs': chef_results[:12],
    }


def recommendations_for(user, governorate='', center=''):
    products = _base_products()
    chefs = _base_chefs()
    favorite_rows = Favorite.objects.filter(user=user)
    favorite_products = set(favorite_rows.filter(product__isnull=False).values_list('product_id', flat=True))
    favorite_chefs = set(favorite_rows.filter(chef__isnull=False).values_list('chef_id', flat=True))
    followed_chefs = set(Follower.objects.filter(customer=user).values_list('chef_id', flat=True))
    order_rows = OrderItem.objects.filter(order__user=user).select_related('product')
    ordered_products = set(order_rows.values_list('product_id', flat=True))
    ordered_chefs = set(order_rows.values_list('product__seller_id', flat=True))
    preferred_categories = Counter(order_rows.values_list('product__category', flat=True))
    for category in Product.objects.filter(id__in=favorite_products).values_list('category', flat=True):
        preferred_categories[category] += 2
    positive_ratings = Review.objects.filter(user=user, rating__gte=4)
    for category in positive_ratings.values_list('product__category', flat=True):
        preferred_categories[category] += 2
    history_terms = set()
    for query in SearchHistory.objects.filter(user=user).values_list('normalized_query', flat=True)[:20]:
        history_terms.update(_tokens(query))

    interaction_ids = favorite_products | ordered_products
    similar_users = set()
    if interaction_ids:
        similar_users.update(
            Favorite.objects.filter(product_id__in=interaction_ids)
            .exclude(user=user).values_list('user_id', flat=True)[:100]
        )
        similar_users.update(
            OrderItem.objects.filter(product_id__in=interaction_ids)
            .exclude(order__user=user).values_list('order__user_id', flat=True)[:100]
        )
    collaborative = Counter(
        Favorite.objects.filter(user_id__in=similar_users, product__isnull=False)
        .values_list('product_id', flat=True)
    )
    collaborative.update(
        OrderItem.objects.filter(order__user_id__in=similar_users)
        .values_list('product_id', flat=True)
    )

    ranked_products = []
    for product in products:
        score = float(product.rating_value or 0) * 0.8
        reasons = []
        if product.id in favorite_products:
            score += 3
            reasons.append('من منتجاتك أو خدماتك المفضلة')
        if product.seller_id in favorite_chefs | followed_chefs:
            score += 6
            reasons.append('من عامل تفضله')
        if product.seller_id in ordered_chefs:
            score += 2.5
            reasons.append('عامل طلبت منه سابقًا')
        if preferred_categories[product.category]:
            score += min(preferred_categories[product.category], 5)
            reasons.append('يناسب اختياراتك السابقة')
        matches = sum(term in normalize_text(f'{product.name} {product.description}') for term in history_terms)
        if matches:
            score += min(matches * 1.5, 4.5)
            reasons.append('مرتبط بعمليات بحثك')
        if center and normalize_text(product.seller.center) == normalize_text(center):
            score += 5
            reasons.append('متاح في منطقتك')
        elif governorate and normalize_text(product.seller.governorate) == normalize_text(governorate):
            score += 3
            reasons.append('قريب منك')
        if collaborative[product.id]:
            score += min(math.log1p(collaborative[product.id]) * 2, 6)
            reasons.append('أعجب مستخدمين يشبهون ذوقك')
        trending = product.recent_order_count + product.favorite_count
        if trending:
            score += min(math.log1p(trending), 4)
            reasons.append('رائج حاليًا')
        product.ai_score = round(score, 3)
        product.recommendation_reason = reasons[0] if reasons else 'تقييمات قوية'
        ranked_products.append(product)

    ranked_products.sort(key=lambda item: (-item.ai_score, -float(item.rating_value or 0), item.id))
    product_scores_by_chef = Counter()
    for product in ranked_products[:50]:
        product_scores_by_chef[product.seller_id] += product.ai_score
    ranked_chefs = []
    for chef in chefs:
        score = float(chef.rating_value or 0) + product_scores_by_chef[chef.id] * 0.15
        reasons = []
        if chef.id in favorite_chefs | followed_chefs:
            score += 7
            reasons.append('من العمال المفضلين لديك')
        if chef.id in ordered_chefs:
            score += 3
            reasons.append('طلبت منه سابقًا')
        if center and normalize_text(chef.center) == normalize_text(center):
            score += 5
            reasons.append('في منطقتك')
        elif governorate and normalize_text(chef.governorate) == normalize_text(governorate):
            score += 3
            reasons.append('قريب منك')
        score += min(math.log1p(chef.followers_count_value), 4)
        chef.ai_score = round(score, 3)
        chef.recommendation_reason = reasons[0] if reasons else 'محبوب وذو تقييم مرتفع'
        ranked_chefs.append(chef)
    ranked_chefs.sort(key=lambda item: (-item.ai_score, item.name))
    return {'meals': ranked_products[:24], 'chefs': ranked_chefs[:12]}
