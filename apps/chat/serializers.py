from xml.dom import ValidationErr
from blob.utils.customFields import TimestampField
from blob.utils.func import return_file_url
from rest_framework import serializers

from apps.shop.models import Attachment
from apps.shop.serializers import AttachmentSerializer
from apps.users.models import User
from apps.users.serializers import (UserShortChatRetrieveSerializer,
                                    UserProfileSerializer,
                                    UserShortSocketRetrieveSerializer)

from .models import Chat, Room, UserMessage, Bookmark, Favourite


class RoomGetSerializer(serializers.ModelSerializer):

    creator = UserProfileSerializer()
    invited = UserProfileSerializer(many=True)
    date = TimestampField(required=False)
    logo = serializers.SerializerMethodField()

    def get_logo(self, room: Room):
        if room.logo and hasattr(room.logo, 'url'):
            return return_file_url(self, room.logo.url)
        return ''

    class Meta:
        model = Room
        fields = '__all__'


class RoomSocketSerializer(serializers.ModelSerializer):

    creator = UserShortSocketRetrieveSerializer()
    invited = serializers.SerializerMethodField()
    date = TimestampField(required=False)
    logo = serializers.SerializerMethodField()

    def get_invited(self, room: Room):
        if len(room.invited.all()) == 1:
            return UserShortSocketRetrieveSerializer(instance=room.invited.all().first()).data
        else:
            return len(room.invited.all())

    def get_logo(self, room: Room):
        if room.logo and hasattr(room.logo, 'url'):
            return return_file_url(self, room.logo.url)
        return ''

    class Meta:
        model = Room
        fields = '__all__'


class RoomCreationSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(
        required=False, queryset=User.objects.all())
    invited = serializers.PrimaryKeyRelatedField(
        required=False, many=True, queryset=User.objects.all())

    class Meta:
        model = Room
        exclude = 'date',

    def validate(self, attrs):
        if attrs.get('invited'):
            creator = Room.objects.filter(
                creator=attrs['creator'],
                invited=attrs['invited'][0]
            )
            invited = Room.objects.filter(
                invited=attrs['creator'],
                creator=attrs['invited'][0]
            )
            if attrs['creator'] == attrs['invited'][0]:
                raise serializers.ValidationError
            if creator.exists():
                for el in creator:
                    if len(el.invited.all()) == 1:
                        raise ValueError(el.pk)
            if invited.exists():
                for el in invited:
                    if len(el.invited.all()) == 1:
                        raise ValueError(el.pk)
        return attrs


class RoomUpdateSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(
        required=False, queryset=User.objects.all())
    invited = serializers.PrimaryKeyRelatedField(
        required=False, many=True, queryset=User.objects.all())

    class Meta:
        model = Room
        exclude = 'date',


class ChatGetSerializer(serializers.ModelSerializer):

    room = RoomGetSerializer()
    user = UserShortChatRetrieveSerializer()
    attachment = AttachmentSerializer(many=True)
    date = TimestampField(required=False)

    class Meta:
        model = Chat
        fields = '__all__'


class ChatCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        exclude = 'date',

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['user'] = request.user
        return attrs


class ChatPartialSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(
        required=False, queryset=User.objects.all())
    room = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Room.objects.all())
    attachment = serializers.PrimaryKeyRelatedField(many=True,
                                                    required=False, queryset=Attachment.objects.all())
    text = serializers.CharField(required=False)

    class Meta:
        model = Chat
        exclude = 'date',


class UserMessageGetSerializer(serializers.ModelSerializer):

    user = UserProfileSerializer()
    message = ChatGetSerializer()

    class Meta:
        model = UserMessage
        fields = '__all__'


class UserMessageCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMessage
        fields = '__all__'


class ChatMessagesSerializer(serializers.Serializer):

    room_id = serializers.IntegerField()
    message_id = serializers.IntegerField()


class ChatMessagesReadSerializer(serializers.Serializer):

    room_id = serializers.IntegerField()


class RetrieveChatsSerializer(serializers.Serializer):

    limit = serializers.IntegerField(required=False)
    offset = serializers.IntegerField(required=False)


class NewMessagesCountSerializer(serializers.Serializer):

    newMessagesCount = serializers.IntegerField(required=False)


class RoomInviteUserSerializer(serializers.ModelSerializer):

    invited = serializers.PrimaryKeyRelatedField(
        required=True, many=True, queryset=User.objects.all())

    class Meta:
        model = Room
        fields = 'invited',


class BookmarkCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    output = serializers.CharField()
    created_date = TimestampField(required=False)

    class Meta:
        model = Bookmark
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['user'] = request.user
        return attrs

class BookmarkGetSerializer(serializers.ModelSerializer):

    user = UserProfileSerializer()
    output = serializers.CharField()
    created_date = TimestampField(required=False)

    class Meta:
        model = Bookmark
        fields = '__all__'


class FavouriteCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    prompt = serializers.CharField()
    created_date = TimestampField(required=False)

    class Meta:
        model = Favourite
        fields = '__all__'


class FavouriteGetSerializer(serializers.ModelSerializer):

    user = UserProfileSerializer()
    prompt = serializers.CharField()
    created_date = TimestampField(required=False)

    class Meta:
        model = Favourite
        fields = '__all__'
