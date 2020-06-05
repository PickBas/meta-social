"""
Models module
"""

from io import BytesIO
from PIL import Image

from django.db import models
from django.core.files import File
from django.contrib.auth.models import User

from music.models import Music


class MessageImages(models.Model):
    """
    Message image model

    :param image: image

    """
    image = models.ImageField(upload_to='messages/images')

    def save(self, *args: tuple, **kwargs: dict) -> None:
        """
        Resize and compress images before save
        :param args: args
        :param kwargs: kwargs
        :return: None
        """
        pil_image = Image.open(self.image)
        output = BytesIO()

        new_size = new_size = (720, (pil_image.size[1] * 720) // pil_image.size[0])
        pil_image = pil_image.resize(new_size, Image.ANTIALIAS)

        try:
            pil_image.save(output, 'JPEG', quality=60)
        except OSError:
            pil_image.save(output, 'PNG', quality=60)

        self.image = File(output, name=self.image.name)

        super().save(*args, **kwargs)


class Message(models.Model):
    """
    Chat messages model

    :param author: ForeignKey to :class:`User`
    :param message: message's text
    :param date: message's send date
    :param is_read: True if user's message was read
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_messages", null=True)
    message = models.TextField(null=True)
    date = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    images = models.ManyToManyField(MessageImages)
    music = models.ManyToManyField(Music)

    def __str__(self):
        """
        Returns a string representation of an object
        """
        return self.author.username


class Chat(models.Model):
    """
    Chat model
    """
    chat_name = models.CharField(max_length=50, null=True)
    participants = models.ManyToManyField(User, related_name="chat_participants")
    messages = models.ManyToManyField(Message, blank=True)
    is_dialog = models.BooleanField(default=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_owner', null=True)
    administrators = models.ManyToManyField(User, related_name='chat_administrators')

    base_image = models.ImageField(upload_to='avatars/users', default='avatars/users/0.png')
    image = models.ImageField(upload_to='avatars/users', default='avatars/users/0.png')

    def get_unread_messages(self):
        """
        Returns all unread message objects
        """
        return self.messages.all().filter(is_read=False)

    def last_message(self):
        """
        Returns last message
        """
        try:
            return list(self.messages.all().order_by('-date'))[0]
        except IndexError:
            return False

    def __str__(self):
        """
        Returns a string representation of an object
        """
        return "{}".format(self.pk)