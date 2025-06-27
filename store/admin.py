from django.contrib import admin
from .models import Category, Image, Product, ProductVariant, Review, Order, Promotion

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

    class ReviewInline(admin.StackedInline):
        model = Review
        extra = 0
        fields = ('review_type', 'content', 'is_active')
        show_change_link = True

    list_display = ('name', 'category', 'is_active', 'view_count', 'average_rating', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    inlines = [ProductVariantInline, ReviewInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'review_type', 'is_active', 'created_at')
    list_filter = ('review_type', 'is_active', 'created_at')
    search_fields = ('product__name', 'content')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'variant', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('user__username', 'address', 'note')


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'discount_type', 'discount_value', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'discount_type', 'start_date', 'end_date')
    search_fields = ('name', 'code')