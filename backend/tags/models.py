from django.db import models

MAX_TAG_LENGTH = 10


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_LENGTH)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name