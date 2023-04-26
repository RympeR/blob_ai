from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.shop.models import Prompt, ModelCategory
from blob.utils.customFields import TimestampField
from blob.utils.func import get_online
from .models import User, Like, Subscription


class CustomModelCategorySerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(use_url=True, read_only=True)

    class Meta:
        model = ModelCategory
        fields = ('id', 'name', 'icon')


class CustomPromptSerializer(serializers.ModelSerializer):
    model_category = CustomModelCategorySerializer()
    image = serializers.ImageField(use_url=True, read_only=True)

    class Meta:
        model = Prompt
        fields = ('id', 'name', 'model_category', 'image')


class UserFavouritesSerializer(serializers.Serializer):
    favourite = serializers.BooleanField()
    prompt_id = serializers.PrimaryKeyRelatedField(queryset=Prompt.objects.all())


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'].lower(),
            password=validated_data['password']
        )
        return user

    def get_serializer_context(self):
        return {'request': self.request}


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data.get("email").lower(), password=data.get("password"))
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'social_links', 'custom_prompt_price',
            'sale_notification_emails', 'new_favorites_emails', 'new_followers_emails', 'new_messages_emails',
            'new_job_emails', 'new_review_emails', 'new_credits_emails', 'review_reminder_emails',
            'following_users_new_prompts', 'hide_categories', 'hide_tone_style', 'hide_fast_prompt'
        )


class CustomUserSerializer(serializers.ModelSerializer):
    favorite_prompts = serializers.SerializerMethodField()
    joined_date = TimestampField()
    avatar = serializers.ImageField(use_url=True)
    background_photo = serializers.ImageField(use_url=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'background_photo', 'social_links',
            'amount_of_lookups', 'amount_of_likes', 'joined_date', 'custom_prompt_price', 'register_provider',
            'sale_notification_emails', 'new_favorites_emails', 'new_followers_emails', 'new_messages_emails',
            'new_job_emails', 'new_review_emails', 'new_credits_emails', 'review_reminder_emails',
            'following_users_new_prompts', 'favorite_prompts', 'hide_categories', 'hide_tone_style', 'hide_fast_prompt'
        )

    def get_favorite_prompts(self, obj):
        return CustomPromptSerializer(
            obj.favorited_by.all(), many=True, context={'request': self.context.get('request')}
        ).data


class UserProfileSerializer(serializers.ModelSerializer):
    most_popular_prompts = serializers.SerializerMethodField()
    newest_prompts = serializers.SerializerMethodField()
    avatar = serializers.ImageField(use_url=True)
    background_photo = serializers.ImageField(use_url=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'background_photo',
            'amount_of_lookups',
            'amount_of_likes',
            'amount_of_sells',
            'most_popular_prompts',
            'newest_prompts'
        )

    def get_most_popular_prompts(self, obj):
        return CustomPromptSerializer(
            obj.prompt_creator.order_by('-amount_of_lookups'), many=True,
            context={'request': self.context.get('request')}
        ).data

    def get_newest_prompts(self, obj):
        return CustomPromptSerializer(
            obj.prompt_creator.order_by('-creation_date'), many=True, context={'request': self.context.get('request')}
        ).data


class UserGetProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(use_url=True)
    background_photo = serializers.ImageField(use_url=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'background_photo',
            'amount_of_lookups',
            'amount_of_likes',
            'amount_of_sells',
        )


class GoogleUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    register_provider = serializers.CharField()


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)


class UserPartialSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    avatar = serializers.ImageField(required=False)
    background_photo = serializers.ImageField(required=False)
    social_links = serializers.JSONField(required=False)
    custom_prompt_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    register_provider = serializers.CharField(required=False)
    sale_notification_emails = serializers.BooleanField(required=False)
    new_favorites_emails = serializers.BooleanField(required=False)
    new_followers_emails = serializers.BooleanField(required=False)
    new_messages_emails = serializers.BooleanField(required=False)
    new_job_emails = serializers.BooleanField(required=False)
    new_review_emails = serializers.BooleanField(required=False)
    new_credits_emails = serializers.BooleanField(required=False)
    review_reminder_emails = serializers.BooleanField(required=False)
    following_users_new_prompts = serializers.BooleanField(required=False)
    hide_categories = serializers.BooleanField(required=False)
    hide_tone_style = serializers.BooleanField(required=False)
    hide_fast_prompt = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if attrs.get('email'):
            attrs['email'] = attrs['email'].lower()
        return attrs

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'background_photo',
            'social_links',
            'custom_prompt_price',
            'register_provider',
            'sale_notification_emails',
            'new_favorites_emails',
            'new_followers_emails',
            'new_messages_emails',
            'new_job_emails',
            'new_review_emails',
            'new_credits_emails',
            'review_reminder_emails',
            'following_users_new_prompts',
            'hide_categories',
            'hide_tone_style',
            'hide_fast_prompt',
        )


class LikeCreateSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    creation_date = TimestampField(required=False)

    class Meta:
        model = Like
        fields = '__all__'


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    creation_date = TimestampField(required=False)

    class Meta:
        model = Subscription
        fields = '__all__'


class SubscriptionsGetSerializer(serializers.ModelSerializer):
    sender = UserGetProfileSerializer()
    receiver = UserGetProfileSerializer()

    class Meta:
        model = Subscription
        fields = '__all__'


class UserShortChatRetrieveSerializer:
    avatar = serializers.ImageField(use_url=True)
    background_photo = serializers.ImageField(use_url=True)
    is_online = serializers.SerializerMethodField()

    def get_is_online(self, user: User):
        return get_online(self, user)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'background_photo',
            'is_online',
        )


class UserShortSocketRetrieveSerializer:
    avatar = serializers.ImageField(use_url=True)
    is_online = serializers.SerializerMethodField()

    def get_is_online(self, user: User):
        return get_online(self, user)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'is_online',
        )
