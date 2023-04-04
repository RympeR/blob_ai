from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count


class User(AbstractUser):
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    background_photo = models.ImageField(upload_to='background_photos/', blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)
    amount_of_lookups = models.IntegerField(default=0)
    joined_date = models.DateTimeField(auto_now_add=True)
    custom_prompt_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    register_provider = models.CharField(
        max_length=50, choices=[('email', 'Email'), ('google', 'Google')], default='email'
    )
    sale_notification_emails = models.BooleanField(default=True)
    new_favorites_emails = models.BooleanField(default=True)
    new_followers_emails = models.BooleanField(default=True)
    new_messages_emails = models.BooleanField(default=True)
    new_job_emails = models.BooleanField(default=True)
    new_review_emails = models.BooleanField(default=True)
    new_credits_emails = models.BooleanField(default=True)
    review_reminder_emails = models.BooleanField(default=True)
    following_users_new_prompts = models.BooleanField(default=True)
    google_id = models.CharField(max_length=50, blank=True, null=True)
    hide_categories = models.BooleanField(default=False)
    hide_tone_style = models.BooleanField(default=False)
    hide_fast_prompt = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    @staticmethod
    def _create_user(password, email, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        user = User.objects.create(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(password, email, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(password, email, **extra_fields)

    @property
    def get_main_category(self):
        try:
            return self.user_post.all().values('category__name').annotate(
                count=Count('category__name')).order_by('-count')[0]['category__name']
        except IndexError:
            return None

    @property
    def subscriptions(self):
        return self.subscribed_to.all().values_list('receiver', flat=True)

    @property
    def subscribers(self):
        return self.subscribed_by.all().values_list('sender', flat=True)

    @property
    def amount_of_sells(self):
        return self.orders_created.count()

    @property
    def amount_of_likes(self):
        return len(self.liked_by.all())

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Like(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_by')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} likes {self.receiver.username}'

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'


class Subscription(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} subscribed to {self.receiver.username}'

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
