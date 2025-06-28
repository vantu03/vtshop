from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Product, Order, ProductVariant
import re
from django.contrib.sitemaps import Sitemap
from django.http import JsonResponse

def home_view(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:12]
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

        if request.method == 'POST':
            last_name = request.POST.get('last_name', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            note = request.POST.get('note', '').strip()
            variant_id = request.POST.get('variant_id')

            errors = []

            if not last_name or not first_name:
                errors.append("Vui lòng nhập đầy đủ họ tên.")
            if not phone:
                errors.append("Vui lòng nhập số điện thoại.")
            elif not re.match(r'^0\d{9}$', phone):
                errors.append("Số điện thoại không hợp lệ. Phải gồm 10 chữ số và bắt đầu bằng 0.")
            if not address:
                errors.append("Vui lòng nhập địa chỉ.")

            variant = product.variants.filter(id=variant_id).first()
            if not variant:
                errors.append("Biến thể sản phẩm không hợp lệ.")

            if errors:
                for error in errors:
                    messages.error(request, error)
            else:

                user, created = User.objects.get_or_create(username=phone)
                if created:
                    user.first_name = first_name
                    user.last_name = last_name

                    user.set_password(User.make_random_password())
                    user.save()

                Order.objects.create(
                    user=user,
                    address=address,
                    note=note,
                    variant=variant
                )

                messages.success(request, "Đặt hàng thành công! Chúng tôi sẽ liên hệ với bạn.")

        return render(request, 'store/product.html', {
            'product': product,
            'variant': variant,
            'images': images,
            "og_image": og_image,
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
