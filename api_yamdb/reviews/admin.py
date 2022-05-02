from django.contrib import admin

from reviews.models import User, Title, Review, Comment, Genre, Category


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_editable = ('name', 'slug')
    search_fields = ('name', 'slug')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_editable = ('name', 'slug')
    search_fields = ('name', 'slug')


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'category',
    )
    list_editable = ('name', 'description', 'category', 'year')
    search_fields = ('name', 'year', 'genre', 'category')


admin.site.register(User)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
