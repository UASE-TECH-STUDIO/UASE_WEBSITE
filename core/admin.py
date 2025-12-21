from django.contrib import admin
from .models import Testimonial, UploadedFile, ContactMessage, Post, Comment

# Register your models here.

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'author_title', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author_name', 'content')
    list_editable = ('is_approved',)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'uploaded_at')
    search_fields = ('name',)

    
    
from django.contrib import admin
from django.utils.timezone import now
from .models import ContactMessage
from .services.email_service import send_admin_reply



  


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'subject',
        'country',
        'ip_address',
        'submitted_at',
        'is_read',
        'user'
    )
      readonly_fields = ("created_at", "ip_address", "country")

    fieldsets = (
        ("User Message", {
            "fields": ("name", "email", "message")
        }),
        ("Admin Reply", {
            "fields": ("admin_reply",)
        }),
        ("Meta", {
            "fields": ("ip_address", "country", "created_at")
        }),
    )

    actions = ["send_reply"]

    def send_reply(self, request, queryset):
        for msg in queryset:
            if msg.admin_reply:
                send_admin_reply(msg.email, msg.name, msg.admin_reply)
                msg.replied_at = now()
                msg.save()
    list_filter = ('country', 'is_read', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message', 'ip_address')
    list_editable = ('is_read',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'created_on', 'updated_on')
    list_filter = ('author', 'created_on')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)} # Auto-generates slug from title
    raw_id_fields = ('author',) # For better user selection if many users

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_on', 'is_approved')
    list_filter = ('is_approved', 'created_on')
    search_fields = ('content', 'author__username')
    list_editable = ('is_approved',)
    raw_id_fields = ('post', 'author',) # For better post/user selection