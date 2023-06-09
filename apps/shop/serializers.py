from rest_framework import serializers
from .models import ModelCategory, Tag, Attachment, Rating, Prompt, Category, Order, PromptLike
from ..users.models import User
from blob.utils.customFields import TimestampField
from apps.users.serializers import UserGetProfileSerializer


class ModelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCategory
        fields = ('id', 'name', 'icon')


class ModelCategoryCreatePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCategory
        fields = ('id', 'name', 'icon', 'custom_parameters')


class ModelCategoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCategory
        fields = ('id', 'name')


class CategoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class TagGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'is_system', 'icon')


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = 'id', 'file_type', '_file'


class AttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = 'id', 'file_type', '_file'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'amount_of_stars', 'prompt')


class PromptSerializer(serializers.ModelSerializer):
    model_category = ModelCategorySerializer()
    tags = TagSerializer(many=True)
    ratings = RatingSerializer(many=True)
    attachments = AttachmentSerializer(many=True)
    purchased = serializers.SerializerMethodField()
    categories = CategoryGetSerializer(many=True)

    class Meta:
        model = Prompt
        fields = (
            'id', 'image', 'model_category', 'price', 'name',
            'description', 'token_size', 'example_input',
            'example_output', 'user', 'review_amount',
            'creation_date', 'tags', 'amount_of_lookups', 'ratings',
            'attachments', 'prompt_template', 'instructions', 'purchased', 'categories'
        )

    def get_purchased(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Order.objects.filter(
                buyer=user, prompt=obj
            ).exists() or Order.objects.filter(creator=user, prompt=obj).exists()
        return False


class MainPageSerializer(serializers.Serializer):
    featured_prompts = PromptSerializer(many=True)
    new_prompts = PromptSerializer(many=True)
    top_prompts = PromptSerializer(many=True)



class PromptCreateSerializer(serializers.ModelSerializer):
    model_category = serializers.PrimaryKeyRelatedField(queryset=ModelCategory.objects.all())
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    attachments = serializers.PrimaryKeyRelatedField(many=True, queryset=Attachment.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    image = serializers.ImageField()
    custom_parameters = serializers.JSONField(required=False)

    class Meta:
        model = Prompt
        fields = (
            'id', 'image', 'model_category', 'price', 'name',
            'description', 'token_size', 'example_input',
            'example_output', 'user', 'categories', 'sell_amount',
            'tags', 'attachments', 'prompt_template', 'instructions', 'custom_parameters'
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ModelCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCategory
        fields = ('id', 'name')


class MarketplacePromptSerializer(serializers.ModelSerializer):
    model_category = ModelCategoryListSerializer()
    category = CategorySerializer(many=True)

    class Meta:
        model = Prompt
        fields = ('id', 'name', 'model_category', 'category', 'image')


class OrderSerializer(serializers.ModelSerializer):
    prompt = serializers.PrimaryKeyRelatedField(queryset=Prompt.objects.all())
    buyer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    created_at = TimestampField(required=False)

    class Meta:
        model = Order
        fields = ('id', 'buyer', 'prompt', 'creator', 'price', 'created_at')


class UserOrderSerializer(serializers.ModelSerializer):
    prompt = PromptSerializer()
    creator = UserGetProfileSerializer()
    created_at = TimestampField(required=False)
    buyer = UserGetProfileSerializer()

    class Meta:
        model = Order
        fields = ('id', 'buyer', 'prompt', 'creator', 'price', 'created_at')


class PromptLikeCreateSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=Prompt.objects.all())
    creation_date = TimestampField(required=False)

    class Meta:
        model = PromptLike
        fields = '__all__'
