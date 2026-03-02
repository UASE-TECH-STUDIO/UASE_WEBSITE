from django.db import models
from django.contrib.auth.models import User

# ===============================
# WEBSITE CONTENT MODELS
# ===============================

class Testimonial(models.Model):
    author_name = models.CharField(max_length=100)
    author_title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(default=5)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.author_name}"

class UploadedFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    admin_reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} | {self.email}"

# ===============================
# BLOG MODELS
# ===============================

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f'Comment by {self.author.username}'

# ===============================
# ADMISSION & REGISTRATION MODEL (MERGED & FIXED)
# ===============================

class ProgramRegistration(models.Model):
    PROGRAM_CHOICES = [
        ('launch', 'Office Launch'),
        ('pro', 'Professional Program'),
        ('fullstack', 'Full Stack'),
        ('extra', 'Full Stack Extra'),
    ]
    MODE_CHOICES = [('Physical', 'Physical'), ('Online', 'Online')]
    PAYMENT_METHODS = [('card', 'Card'), ('transfer', 'Transfer')]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20)
    
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    program = models.CharField(max_length=50, choices=PROGRAM_CHOICES)
    depth = models.CharField(max_length=100, blank=True, null=True)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_ref = models.CharField(max_length=200, blank=True, null=True)
    paystack_ref = models.CharField(max_length=100, blank=True, null=True)
    
    # Screenshot field fixed here:
    payment_screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_confirmed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_program_display()}"