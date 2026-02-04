from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    empty_value_display = '-'

    list_display = (
        'title',
        'short_description',
        'slug',
        'is_published',
        'created_at',
    )
    search_fields = (
        'title',
        'slug',
        'description',
    )
    list_filter = (
        'is_published',
        'created_at',
    )

    def short_description(self, obj):
        return obj.description[:100] + '...' if obj.description else '-'
    short_description.short_description = 'Краткое описание'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    empty_value_display = '-'
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'is_published',
        'created_at',
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    empty_value_display = '-'

    list_display = (
        'title',
        'short_text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
        'image_preview',
    )

    search_fields = ('title', 'text')
    
    list_filter = (
        'is_published',
        'pub_date',
        'created_at',
        'location',
        'author',
        'category',
    )

    def short_text(self, obj):
        return obj.text[:100] + '...' if obj.text else '-'
    short_text.short_description = 'Краткий текст'

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="80" height="60" style="object-fit: cover;">'
            )
        return "-"
    
    image_preview.short_description = "Превью"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'author', 'post', 'created_at')
    list_filter = ('created_at', 'author', 'post')
    search_fields = ('text', 'author__username', 'post__title')
    ordering = ('-created_at',)

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
