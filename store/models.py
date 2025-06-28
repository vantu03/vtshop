from django.db import models
from slugify import slugify
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alt_text or self.image.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    thumbnail = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
    )
    images = models.ManyToManyField(Image, related_name='images', blank=True)

    is_active = models.BooleanField(default=True)

    view_count = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

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

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ManyToManyField(Image, related_name='products', blank=True)

    def __str__(self):
        return f"{self.name} - {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.TextField()
    note = models.TextField(blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.variant.product.name


class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percent', 'Phần trăm'),
        ('fixed', 'Số tiền cố định'),
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Mã giảm giá (nếu cần nhập)")

    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    users = models.ManyToManyField(User, blank=True, help_text="Để trống nếu áp dụng cho tất cả người dùng")
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

class Review(models.Model):
    REVIEW_TYPE_CHOICES = (
        ('intro', 'Giới thiệu sản phẩm'),
        ('info', 'Thông tin chi tiết'),
        ('guide', 'Hướng dẫn sử dụng'),
        ('review', 'Đánh giá từ người dùng'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    review_type = models.CharField(
        max_length=20,
        choices=REVIEW_TYPE_CHOICES,
        default='review',
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.review_type} ({self.get_review_type_display()})"
