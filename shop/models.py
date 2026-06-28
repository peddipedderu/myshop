from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.CharField(max_length=100, default='Pink Cycle Team')
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/%Y/%m/%d', blank=True)
    image_description = models.TextField(blank=True)
    event_description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class SocialMedia(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField()
    icon_name = models.CharField(max_length=50)
    followers_count = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.name

class ProgramCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        verbose_name_plural = 'Program Categories'
    def __str__(self):
        return self.name

class Program(models.Model):
    category = models.ForeignKey(ProgramCategory, related_name='programs', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='programs/%Y/%m/%d', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Session(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    mentor_name = models.CharField(max_length=100)
    mentor_bio = models.TextField(blank=True, null=True)
    time = models.DateTimeField()
    duration = models.CharField(max_length=50, default='1 hour')
    capacity = models.PositiveIntegerField()
    syllabus = models.TextField(blank=True, null=True)
    prerequisites = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sessions/%Y/%m/%d', blank=True, null=True)
    meeting_type = models.CharField(max_length=20, choices=[('Live', 'Live Meeting'), ('Virtual', 'Virtual (Skype)')], default='Virtual')
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)
    session_name = models.CharField(max_length=200)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    meeting_format = models.CharField(max_length=20, choices=[('Live', 'Live Meeting'), ('Virtual', 'Virtual (Skype)')], default='Virtual')
    status = models.CharField(max_length=20, default='Pending')
    booked_at = models.DateTimeField(auto_now_add=True)

class ProgramEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'program')

class Donation(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

class UserFollow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_follows')
    social_media = models.ForeignKey(SocialMedia, on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'social_media')

    def __str__(self):
        return f"{self.user.username} follows {self.social_media.name}"

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages', null=True, blank=True)
    username = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.username}: {self.message[:50]}'
