from django.contrib import admin
from .models import ModelCategory, Tag, Attachment, Rating, Prompt, Category


@admin.register(ModelCategory)
class ModelCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


@admin.register(Category)
class ModelCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_system', 'icon')
    list_filter = ('is_system',)
    search_fields = ('name',)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_type', '_file')
    search_fields = ('file_type',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('amount_of_stars', 'prompt')
    list_filter = ('amount_of_stars',)
    search_fields = ('prompt__name',)

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'model_category', 'sell_amount', 'token_size', 'creation_date', 'review_amount', 'amount_of_lookups')
    list_filter = ('user', 'model_category', 'tags', 'creation_date')
    search_fields = ('name',)
    autocomplete_fields = ('user', 'model_category', 'tags', 'attachments',)
