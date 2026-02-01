from django.contrib import admin

from .models import Category, Location, Post


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
    )
    search_fields = (
        'title',
        'text',
    )
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'author', 'location', 'category'
        )
    short_text.short_description = 'Краткий текст'
