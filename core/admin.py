import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.timezone import now
from django.utils.html import format_html
from .models import (
    Testimonial, UploadedFile, ContactMessage, 
    Post, Comment, ProgramRegistration
)
from .services.email_service import send_admin_reply

# ===============================
# PROGRAM REGISTRATION ADMIN
# ===============================


@admin.register(ProgramRegistration)
class ProgramRegistrationAdmin(admin.ModelAdmin):
    # 1. Columns shown in the main list view
    list_display = (
        "name", "program", "mode", "payment_method", 
        "amount_paid", "is_confirmed", "whatsapp", "created_at"
    )
    
    # 2. Sidebar filters
    list_filter = ("program", "mode", "payment_method", "is_confirmed", "created_at")
    
    # 3. Search functionality
    search_fields = ("name", "email", "phone", "whatsapp", "location")
    
    # 4. Quick edit checkmark in the list
    list_editable = ("is_confirmed",)

    # 5. Organization of the detail page (when you click a name)
    fieldsets = (
        ("Personal Information", {
            "fields": ("name", "email", "phone", "whatsapp", "occupation")
        }),
        ("Address & Goals", {
            "fields": ("location", "address", "aim")
        }),
        ("Program Details", {
            "fields": ("program", "mode", "depth")
        }),
        ("Payment Info", {
            "fields": ("payment_method", "amount_paid", "transaction_ref", "payment_screenshot", "is_confirmed")
        }),
    )

    # 6. Action to export to CSV (Excel)
    actions = ["export_to_csv"]

    @admin.action(description="Export selected to CSV")
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="registrations.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Program', 'Mode', 'Location', 'Paid'])
        for obj in queryset:
            writer.writerow([obj.name, obj.email, obj.phone, obj.program, obj.mode, obj.location, obj.amount_paid])
        return response

    

    # Color-coded Program labels
    def program_tag(self, obj):
        colors = {
            'launch': '#fbbf24',    # Gold
            'pro': '#60a5fa',       # Blue
            'fullstack': '#a78bfa', # Purple
            'extra': '#f472b6',     # Pink
        }
        color = colors.get(obj.program, '#94a3b8')
        return format_html(
            '<span style="background: {}; color: black; padding: 3px 10px; border-radius: 10px; font-weight: bold; font-size: 10px; text-transform: uppercase;">{}</span>',
            color, obj.program
        )
    program_tag.short_description = "Track"

    # Visual Payment Status
    def payment_status(self, obj):
        if obj.is_confirmed:
            return format_html('<b style="color: #059669;">Verified ✅</b>')
        return format_html('<b style="color: #dc2626;">Pending ⏳</b>')
    payment_status.short_description = "Status"

    def mark_as_confirmed(self, request, queryset):
        queryset.update(is_confirmed=True)
    mark_as_confirmed.short_description = "Confirm selected payments"

    def export_students_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="uase_students_{now().date()}.csv"'
        writer = csv.writer(response)
        writer.writerow(["Name", "Email", "Phone", "WhatsApp", "Mode", "Program", "Depth", "Amount", "Confirmed"])
        for student in queryset:
            writer.writerow([
                student.name, student.email, student.phone, student.whatsapp,
                student.mode, student.program, student.depth, student.amount_paid, student.is_confirmed
            ])
        return response
    export_students_csv.short_description = "Export Student List (CSV)"

# ===============================
# CONTACT MESSAGE ADMIN
# ===============================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "country", "created_at", "is_read")
    list_filter = ("country", "is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("is_read",)
    readonly_fields = ("created_at", "ip_address", "country")
    actions = ["send_reply", "export_contacts_csv"]

    def send_reply(self, request, queryset):
        sent = 0
        for msg in queryset:
            if msg.admin_reply and msg.email:
                send_admin_reply(to_email=msg.email, name=msg.name, reply_message=msg.admin_reply)
                msg.replied_at = now()
                msg.is_read = True
                msg.save()
                sent += 1
        self.message_user(request, f"{sent} reply email(s) successfully sent.")

    def export_contacts_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="contacts.csv"'
        writer = csv.writer(response)
        writer.writerow(["Name", "Email", "Country", "Message", "Created At"])
        for obj in queryset:
            writer.writerow([obj.name, obj.email, obj.country, obj.message, obj.created_at])
        return response

# ===============================
# REMAINING ADMINS
# ===============================
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_title", "is_approved", "created_at")
    list_editable = ("is_approved",)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "uploaded_at")

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "created_on")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_on", "is_approved")
    list_editable = ("is_approved",)