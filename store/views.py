from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, Order, ProductVariant, Star, OrderItem, Category, Review, Image, Brand
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.http import JsonResponse
from .utils import normalize_and_validate_phone

def custom_404_view(request, exception):
    return render(request, "store/404.html", status=404)

def home_view(request):
    featured_products = Product.objects.order_by('-view_count')[:10]  # Xem nhiều nhất
    new_products = Product.objects.order_by('-created_at')
    return render(request, 'store/home.html', {
        'featured_products': featured_products,
        'new_products': new_products,
    })

def product_detail_view(request, category_slug, product_slug):
    product = Product.objects.filter(
        slug=product_slug,
        category__slug=category_slug,
        is_active=True
    ).first()

    if not product:
        return render(request, 'store/404.html', status=404)

    product.view_count += 1
    product.save(update_fields=['view_count'])
    variant = product.get_variant(request.GET.get("variant"))

    images = []
    seen_urls = set()
    if variant:
        for img in variant.images.all():
            if img.image.url not in seen_urls:
                images.append({'url': img.image.url, 'alt_text': img.alt_text})
                seen_urls.add(img.image.url)

    for img in product.images.all():
        if img.image.url not in seen_urls:
            images.append({'url': img.image.url, 'alt_text': img.alt_text})
            seen_urls.add(img.image.url)

    if product.thumbnail:
        og_image = product.thumbnail.image.url
    elif variant and variant.images.exists():
        og_image = variant.images.first().image.url
    elif images:
        og_image = images[0]['url']
    else:
        og_image = None

    reviews = product.reviews.filter(is_active=True).order_by('-created_at')[:3]

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:8]

    return render(request, 'store/product.html', {
        'product': product,
        'variant': variant,
        'images': images,
        'og_image': og_image,
        'reviews': reviews,
        'stars': Star.objects.all().order_by('star'),
        "related_products": related_products,
    })

def category_products_view(request, category_slug=None):
    category = None
    brand = None

    products = Product.objects.filter(is_active=True)

    if category_slug:
        category = Category.objects.filter(slug=category_slug).first()
        if not category:
            return render(request, 'store/404.html', status=404)
        products = products.filter(category=category)

    # Filter theo hãng
    brand_id = request.GET.get('brand')
    if brand_id:
        brand = Brand.objects.filter(id=brand_id).first()
        if brand:
            products = products.filter(brand=brand)

    # Sắp xếp
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('default_price')
    elif sort == 'price_desc':
        products = products.order_by('-default_price')
    elif sort == 'best_seller':
        products = products.order_by('-sold')
    elif sort == 'new':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-view_count')

    if category:
        all_brands = Brand.objects.filter(products__category=category, products__is_active=True).distinct()
    else:
        all_brands = Brand.objects.filter(products__is_active=True).distinct()

    return render(request, 'store/products.html', {
        'products': products,
        'category': category,
        'brand': brand,
        'all_brands': all_brands,
    })

def cart_view(request):
    return render(request, 'store/cart.html', )

def get_variant(request, variant_id):

    try:
        variant = ProductVariant.objects.select_related('product').get(id=variant_id)
        return JsonResponse({
            'variant_id': variant.id,
            'product_name': variant.product.name,
            'product_slug': variant.product.get_full_slug(),
            'variant_name': variant.name,
            'price': float(variant.price),
            'thumbnail': variant.product.thumbnail.image.url,
        })
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy biến thể.'}, status=404)

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_full_slug()

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/{obj.slug}/"


def robots_txt(request):
    lines = [
        "User-agent: *",

        # Ngăn bot crawl các phần không nên index
        "Disallow: /admin/",
        "Disallow: /cart/",
        "Disallow: /order/",

        # Sitemap (cực kỳ quan trọng)
        f"Sitemap: {settings.SITE_DOMAIN}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

@csrf_exempt
def submit_cart_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Lấy và kiểm tra dữ liệu
            full_name = data.get('full_name', '').strip()
            phone_number = normalize_and_validate_phone(data.get('phone_number', '').strip())
            email = data.get('email', '').strip()
            address = data.get('address', '').strip()
            note = data.get('note', '').strip()
            items = data.get('items', [])

            if not all([full_name, phone_number, address]) or not items:
                return JsonResponse({'error': 'Thiếu thông tin hoặc giỏ hàng trống.'}, status=400)

            # Tạo đơn hàng
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                phone_number=phone_number,
                email=email,
                address=address,
                note=note
            )

            # Lưu các item trong đơn
            for item in items:
                variant_id = item.get('variant_id')
                quantity = item.get('quantity', 1)
                variant = ProductVariant.objects.filter(id=variant_id).first()
                if variant:
                    OrderItem.objects.create(
                        order=order,
                        variant=variant,
                        quantity=max(1, quantity)
                    )

            return JsonResponse({'message': 'Đặt hàng thành công!'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Yêu cầu không hợp lệ.'}, status=405)

@csrf_exempt
def submit_review(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            product_id = data.get("product_id")
            rating = data.get("rating")
            name = data.get("name", "").strip()
            phone = normalize_and_validate_phone(data.get("phone", "").strip())
            content = data.get("content", "").strip()

            # Kiểm tra dữ liệu đầu vào
            if not all([product_id, rating, name, phone, content]):
                return JsonResponse({"error": "Vui lòng điền đầy đủ thông tin."}, status=400)

            product = Product.objects.filter(id=product_id).first()
            if product:
                star = Star.objects.filter(star=int(rating)).first()
                if star:
                    Review.objects.create(
                        product=product,
                        star=star,
                        name=name,
                        phone=phone,
                        comment=content,
                    )

                    return JsonResponse({"message": "Đánh giá của bạn đã được gửi thành công!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def search_view(request):
    keyword = request.GET.get('keyword', '').strip()

    if keyword:
        category = Category.objects.filter(name__icontains=keyword).first()

        if category:
            return redirect(f'/{category.slug}/')
        else:
            product = Product.objects.filter(name__icontains=keyword, is_active=True).select_related('category').first()
            if product and product.category:
                return redirect(f'/{product.category.slug}/?key={keyword}')

    return redirect('home')