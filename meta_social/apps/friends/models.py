"""
Meta social friend models
"""

from django.db import models
from django.contrib.auth.models import User


class FriendshipRequest(models.Model):
    """
    FriendshipRequest model
    """
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='3+'
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='4+'
    )
