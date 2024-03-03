from django.db import models
from django.contrib.auth.models import User
import uuid

class Collection(models.Model):
    """
    Model representing a collection of movies.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

class Movie(models.Model):
    """
    Model representing a movie.
    """

    title = models.CharField(max_length=100)
    description = models.TextField()
    genres = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.UUIDField()
    collection = models.ForeignKey(Collection, related_name="movies", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class RequestCounter(models.Model):
    """
    Model representing a request counter.
    """

    count = models.IntegerField(default=0)

    def __str__(self):
        return self.count

