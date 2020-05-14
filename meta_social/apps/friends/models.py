from django.db import models


class FriendshipRequest(models.Model):
    """
    FriendshipRequest model
    """
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='3+')
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='4+')
