from django.db import models
from slugify import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from ckeditor_uploader.fields import RichTextUploadingField
from .fields import MediaGridManyToManyField

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alt_text or self.image.name

class Category(models.Model):
    icon = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    thumbnail = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
    )
    images = MediaGridManyToManyField(Image, related_name='images', blank=True)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_variant(self, variant_id=None):
        if variant_id:
            return self.variants.filter(id=variant_id).first()
        return self.variants.first()

    @property
    def average_star(self):
        return self.reviews.filter(is_active=True).aggregate(avg=Avg('star__star'))['avg'] or 0

    @property
    def star_details(self):
        total = self.reviews.filter(is_active=True).count()
        stars = []

        for star in Star.objects.all():
            count = self.reviews.filter(is_active=True, star__star=star.star).count()
            percent = (count / total) * 100 if total > 0 else 0
            stars.append({
                'star': star.star,
                'count': count,
                'percent': percent
            })

        return {
            'total': total,
            'stars': stars,
        }

    def get_full_slug(self):
        return f"/{self.category.slug}/{self.slug}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ManyToManyField(Image, related_name='products', blank=True)

    def __str__(self):
        return f"{self.name} - {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('confirmed', 'Đã xác nhận'),
        ('shipped', 'Đã giao hàng'),
        ('delivered', 'Đã nhận hàng'),
        ('cancelled', 'Đã hủy'),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()

    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.pk} - {self.full_name} ({self.get_status_display()})"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.variant} x{self.quantity}"



class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percent', 'Phần trăm'),
        ('fixed', 'Số tiền cố định'),
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)

    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    users = models.ManyToManyField(User, blank=True)
    products = models.ManyToManyField('Product', blank=True)
    categories = models.ManyToManyField('Category', blank=True)

    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_valid(self, user=None, order_total=0):
        now = timezone.now()

        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        if order_total < self.min_order_value:
            return False
        if self.usage_limit is not None and self.promotionusage_set.count() >= self.usage_limit:
            return False
        if user:
            if self.users.exists() and user not in self.users.all():
                return False
            if self.usage_limit_per_user is not None:
                count = self.promotionusage_set.filter(user=user).count()
                if count >= self.usage_limit_per_user:
                    return False
        return True

    def apply_discount(self, price):
        if self.discount_type == 'percent':
            discount = price * (self.discount_value / 100)
        else:
            discount = self.discount_value

        if self.max_discount:
            discount = min(discount, self.max_discount)

        return max(price - discount, 0)

class ProductContent(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('intro', 'Giới thiệu sản phẩm'),
        ('info', 'Thông tin chi tiết'),
        ('guide', 'Hướng dẫn sử dụng'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='contents')
    content = RichTextUploadingField()
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='info',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.content_type} ({self.get_content_type_display()})"

class Star(models.Model):
    star = models.PositiveSmallIntegerField(unique=True)
    label = models.CharField(max_length=50)

    class Meta:
        ordering = ['-star']

    def __str__(self):
        return f"{self.star} - {self.label}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    star = models.ForeignKey(Star, on_delete=models.CASCADE)
    comment = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.star.label} - {self.product.name}"