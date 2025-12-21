from django.contrib import admin
from django.utils.timezone import now
from .models import Testimonial, UploadedFile, ContactMessage, Post, Comment
from .services.email_service import send_admin_reply
from django.http import HttpResponse
import csv




from .models import (
    Testimonial,
    UploadedFile,
    ContactMessage,
    Post,
    Comment,
)

from .services.email_service import send_admin_reply


# ===============================
# TESTIMONIAL ADMIN
# ===============================
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_title", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("author_name", "content")
    list_editable = ("is_approved",)
    ordering = ("-created_at",)


# ===============================
# UPLOADED FILE ADMIN
# ===============================
@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "uploaded_at")
    search_fields = ("name",)
    ordering = ("-uploaded_at",)


# ===============================
# CONTACT MESSAGE ADMIN (CRM)
# ===============================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "subject",
        "country",
        "ip_address",
        "created_at",
        "is_read",
        "user",
    )

    list_filter = ("country", "is_read", "created_at")
    search_fields = (
        "name",
        "email",
        "subject",
        "message",
        "ip_address",
    )

    list_editable = ("is_read",)
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "ip_address", "country")

    fieldsets = (
        ("User Message", {
            "fields": ("name", "email", "message")
        }),
        ("Admin Reply", {
            "fields": ("admin_reply",)
        }),
        ("System Metadata", {
            "fields": ("ip_address", "country", "created_at")
        }),
    )

    actions = ["send_reply", "export_contacts_csv"]

    def send_reply(self, request, queryset):
        sent = 0
        for msg in queryset:
            if msg.admin_reply and msg.email:
                send_admin_reply(
                    to_email=msg.email,
                    name=msg.name,
                    reply_message=msg.admin_reply,
                )
                msg.replied_at = now()
                msg.is_read = True
                msg.save()
                sent += 1

        self.message_user(
            request,
            f"{sent} reply email(s) successfully sent."
        )

    send_reply.short_description = "Send admin reply email"

    def export_contacts_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="contacts.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Name",
            "Email",
            "Country",
            "IP Address",
            "Message",
            "Created At",
            "Replied",
        ])

        for obj in queryset:
            writer.writerow([
                obj.name,
                obj.email,
                obj.country,
                obj.ip_address,
                obj.message,
                obj.created_at,
                bool(obj.replied_at),
            ])

        return response

    export_contacts_csv.short_description = "Export selected contacts to CSV"


# ===============================
# BLOG POST ADMIN
# ===============================
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "created_on", "updated_on")
    list_filter = ("author", "created_on")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    ordering = ("-created_on",)


# ===============================
# COMMENT ADMIN
# ===============================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_on", "is_approved")
    list_filter = ("is_approved", "created_on")
    search_fields = ("content", "author__username")
    list_editable = ("is_approved",)
    raw_id_fields = ("post", "author")
    ordering = ("-created_on",)
