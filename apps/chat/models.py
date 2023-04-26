from blob.utils.func import room_logo
from django.db import models
from django.db.models.signals import post_save
from unixtimestampfield.fields import UnixTimeStampField

from apps.shop.models import Attachment
from apps.users.models import User


class Room(models.Model):
    creator = models.ForeignKey(
        User, related_name='user_creator', on_delete=models.DO_NOTHING)
    invited = models.ManyToManyField(User, related_name='invited_users')
    date = UnixTimeStampField(
        "Дата создания", auto_now_add=True, null=True, blank=True)
    logo = models.ImageField(
        upload_to=room_logo,
        verbose_name='room logo',
        null=True,
        blank=True
    )
    name = models.CharField('room name', blank=True,
                            null=True, max_length=255)

    def __str__(self):
        return f"{self.creator}-{self.pk}"

    @property
    def get_logo(self):
        if self.logo and hasattr(self.logo, 'url'):
            return 'http://{domain}{path}'.format(
                domain='hype-fans.com', path=self.logo.url)
        if self.creator.avatar and hasattr(self.creator.avatar, 'url'):
            return 'http://{domain}{path}'.format(
                domain='hype-fans.com', path=self.creator.avatar.url)
        return ''

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['-date']


class Chat(models.Model):
    room = models.ForeignKey(Room, verbose_name='Chat room',
                             related_name='chat_room', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='User',
                             related_name='user_sender', on_delete=models.CASCADE)
    text = models.TextField("Message", max_length=500, null=True, blank=True)
    attachment = models.ManyToManyField(
        Attachment, related_name='chat_attachment', blank=True, verbose_name='Attachments')
    date = UnixTimeStampField(
        "Send datetime", auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.pk}-{self.room}"

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        ordering = ['-date']
        unique_together = ['date', 'user', 'room']


class UserMessage(models.Model):
    message = models.ForeignKey(Chat, verbose_name='Delivered message',
                                related_name='delivered_message', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='destination_user',
                             verbose_name='Destination user', on_delete=models.CASCADE)
    readed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Message status'
        verbose_name_plural = 'Message statuses'
        ordering = ['-message__date']

    def __str__(self):
        return f"{self.message}-{self.user}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, related_name='user_bookmark',
                             verbose_name='User', on_delete=models.CASCADE)
    output = models.TextField("Output", max_length=500, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'

    def __str__(self):
        return f"{self.output}-{self.user}"


class Favourite(models.Model):
    user = models.ForeignKey(User, related_name='user_favourite',
                             verbose_name='User', on_delete=models.CASCADE)
    prompt = models.TextField("Prompt", max_length=500, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f"{self.prompt}-{self.user}"


def create_message(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        users = [user for user in room.invited.all()]
        users.append(room.creator)
        for user in users:
            if user.pk != instance.user.pk:
                UserMessage.objects.create(
                    message=instance,
                    user=user,
                    readed=False
                ).save()
                print(f'created {user}')


post_save.connect(create_message, sender=Chat)
