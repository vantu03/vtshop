from django.contrib import admin
from .models import Category, Image, Product, ProductVariant, ProductContent, Order, Promotion, Review, Star, OrderItem, Brand
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', '__str__', 'uploaded_at',)
    search_fields = ('alt_text',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:  # thay 'image' bằng đúng tên field trong model
            return format_html('<img src="{}" width="100" height="auto" style="object-fit: contain;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"
    image_preview.allow_tags = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    class ProductVariantInline(admin.TabularInline):
        model = ProductVariant
        extra = 1

    class ProductContentInline(admin.StackedInline):
        model = ProductContent
        extra = 0
        fields = ('content_type', 'content', 'is_active')
        show_change_link = True

    list_display = ('name', 'category', 'is_active', 'view_count', 'sold', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    #filter_horizontal = ('images',)

    inlines = [ProductVariantInline, ProductContentInline]


@admin.register(ProductContent)
class ProductContentAdmin(admin.ModelAdmin):
    list_display = ('product', 'content_type', 'is_active', 'created_at')
    list_filter = ('content_type', 'is_active', 'created_at')
    search_fields = ('product__name', 'content')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone_number', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone_number', 'email', 'address', 'note')
    list_editable = ('status',)
    readonly_fields = ('created_at',)

    class OrderItemInline(admin.TabularInline):
        model = OrderItem
        extra = 0
        readonly_fields = ('variant', 'quantity')

    inlines = [OrderItemInline]

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'discount_type', 'discount_value', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'discount_type', 'start_date', 'end_date')
    search_fields = ('name', 'code')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'phone', 'star', 'is_active', 'created_at')
    list_filter = ('star', 'is_active', 'created_at')
    search_fields = ('product__name', 'name', 'phone', 'comment')
    readonly_fields = ('created_at',)


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('label', 'star', )
    list_filter = ('star',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
