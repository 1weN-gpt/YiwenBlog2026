from django.contrib import admin
from .models import Category, Tag, Post, Comment, SiteConfig


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'views', 'created_at']
    list_filter = ['status', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'content', 'summary']
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'created_at'
    filter_horizontal = ['tags']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content_short', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    actions = ['approve_comments']

    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = '评论内容'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = '审核通过所选评论'


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'github_url', 'email', 'updated_at']
    fieldsets = [
        ('站点信息', {
            'fields': ['avatar']
        }),
        ('联系方式', {
            'fields': ['github_url', 'wechat_id', 'email']
        }),
        ('友情链接', {
            'fields': [
                ('friend_link_1_name', 'friend_link_1_url'),
                ('friend_link_2_name', 'friend_link_2_url'),
                ('friend_link_3_name', 'friend_link_3_url'),
            ]
        }),
        ('技术栈配置', {
            'fields': [
                ('tech_1', 'tech_2', 'tech_3', 'tech_4'),
                ('tech_5', 'tech_6', 'tech_7', 'tech_8'),
            ],
            'description': '选择要展示的技术栈（最多8个）'
        }),
    ]
