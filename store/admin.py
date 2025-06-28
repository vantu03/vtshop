from django.contrib import admin
from .models import Category, Image, Product, ProductVariant, ProductContent, Order, Promotion, Review, Star, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'uploaded_at')
    search_fields = ('alt_text',)


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

    list_display = ('name', 'category', 'is_active', 'view_count', 'average_rating', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    inlines = [ProductVariantInline, ProductContentInline]


@admin.register(ProductContent)
class ProductContentAdmin(admin.ModelAdmin):
    list_display = ('product', 'content_type', 'is_active', 'created_at')
    list_filter = ('content_type', 'is_active', 'created_at')
    search_fields = ('product__name', 'content')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('user__username', 'address', 'note')

    inlines = []

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
    list_display = ('product', 'user', 'star', 'is_active', 'created_at')
    list_filter = ('star', 'is_active', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    autocomplete_fields = ('product', 'user')
    readonly_fields = ('created_at',)

@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('label', 'star', )
    list_filter = ('star',)