from django.db import models
from django.contrib.auth.models import User # Import Django's built-in User model

# Model for storing testimonials submitted via the website
class Testimonial(models.Model):
    author_name = models.CharField(max_length=100)
    author_title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(default=5) # e.g., out of 5 stars
    is_approved = models.BooleanField(default=False) # Admin can approve before display
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.author_name}"

# Model for uploaded files (e.g., for internal use or authorized users)
class UploadedFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/') # Files will be saved in MEDIA_ROOT/uploads/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Model for contact messages submitted through the form
class ContactMessage(models.Model):
    # Link to a User if they are logged in when submitting the form
    # The 'user' field is nullable (blank=True, null=True) to allow guest submissions
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True, null=True) # Added subject field
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # To track if admin has read it
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - Subject: {self.subject or 'No Subject'}"
  



# Blog Post Model
class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True) # For clean URLs
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True) # Optional image for the post
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    # You might add categories, tags, status (draft/published) later
    
    class Meta:
        ordering = ['-created_on'] # Order posts by creation date, newest first

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})


# Comment Model for Blog Posts
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True) # Admins can moderate comments

    class Meta:
        ordering = ['created_on'] # Order comments by creation date, oldest first

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
