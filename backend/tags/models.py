from django.db import models


MAX_TAG_LENGTH = MAX_SLUG_LENGTH = 32


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_LENGTH)
    slug = models.SlugField(max_length=MAX_SLUG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return self.name
