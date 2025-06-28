from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from .models import Product, Order, ProductVariant, Star, OrderItem
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.http import JsonResponse
from .utils import normalize_and_validate_phone


def home_view(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
    return render(request, 'store/home.html', {'products': products})

def product_view(request, slug):

    product = Product.objects.filter(slug=slug).first()

    if product:

        product.view_count += 1
        product.save(update_fields=['view_count'])
        variant = product.get_variant(request.GET.get("variant"))

        images = []

        seen_urls = set()
        if variant:
            for img in variant.images.all():
                if img.image.url not in seen_urls:
                    images.append({
                        'url': img.image.url,
                        'alt_text': img.alt_text,
                    })
                    seen_urls.add(img.image.url)

        for img in product.images.all():
            if img.image.url not in seen_urls:
                images.append({
                    'url': img.image.url,
                    'alt_text': img.alt_text,
                })
                seen_urls.add(img.image.url)

        if product.thumbnail:
            og_image = product.thumbnail.image.url
        elif variant and variant.images.exists():
            og_image = variant.images.first().image.url
        elif images:
            og_image = images[0]['url']
        else:
            og_image = None


        return render(request, 'store/product.html', {
            'product': product,
            'variant': variant,
            'images': images,
            "og_image": og_image,
            "stars": Star.objects.all().order_by('star')
        })

    return render(request, '404.html', status=404)

def products_view(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'store/products.html', {'products': products})

def cart_view(request):
    return render(request, 'store/cart.html', )

def get_variant(request, variant_id):

    try:
        variant = ProductVariant.objects.select_related('product').get(id=variant_id)
        return JsonResponse({
            'variant_id': variant.id,
            'product_name': variant.product.name,
            'product_slug': variant.product.slug,
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
        return f"/product/{obj.slug}/"

def robots_txt(request):
    lines = [
        "User-agent: *",

        # Ngăn bot crawl các phần không nên index
        "Disallow: /admin/",
        "Disallow: /cart/",
        "Disallow: /order/",
        "Disallow: /*?*",

        # Sitemap (cực kỳ quan trọng)
        f"Sitemap: {settings.SITE_DOMAIN}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

@csrf_exempt
def submit_cart_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Validate thông tin cá nhân
            last_name = data.get('last_name', '').strip()
            first_name = data.get('first_name', '').strip()
            phone = normalize_and_validate_phone(data.get('phone', '').strip())
            address = data.get('address', '').strip()
            note = data.get('note', '').strip()

            if not all([last_name, first_name, phone, address]):
                return JsonResponse({'error': 'Thiếu thông tin bắt buộc.'}, status=400)

            items = data.get('items', [])
            if not items:
                return JsonResponse({'error': 'Giỏ hàng trống.'}, status=400)

            # Tạo user ẩn danh theo số điện thoại
            user, created = User.objects.get_or_create(username=phone)
            if created:
                user.first_name = first_name
                user.last_name = last_name
                user.set_unusable_password()
                user.save()

            # Tạo đơn hàng
            order = Order.objects.create(
                user=user,
                address=address,
                note=note
            )

            # Tạo các item trong đơn hàng
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