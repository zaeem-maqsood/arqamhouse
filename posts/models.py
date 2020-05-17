import itertools
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.crypto import get_random_string

from core.utils import strip_non_ascii
from core.models import TimestampedModel

from houses.models import House

# Create your models here.
class Post(TimestampedModel):

    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=150, null=True, blank=True)
    slug = models.SlugField(max_length=175, unique=False, blank=True)
    content = models.TextField(blank=True, null=True)
    post_number = models.PositiveIntegerField(null=True, blank=True, default=0)



    def set_post_number(self):
        self.issue_receipt = True
        posts = Post.objects.filter(house=self.house)
        posts_exist = posts.exists()
        if posts_exist:
            latest_post = posts.order_by("-created_at")[0]
            self.post_number = latest_post.post_number + 1
        else:
            self.post_number = 1


    def _generate_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)

        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Post.objects.filter(slug=slug_candidate, house=self.house).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate

    def _update_slug(self):
        max_length = self._meta.get_field('slug').max_length
        value = strip_non_ascii(self.name)
        updated_slug = slugify(value, allow_unicode=True)
        if Post.objects.filter(slug=updated_slug, house=self.house).exists():
            pass
        else:
            self.slug = updated_slug

    def save(self, *args, **kwargs):
        if not self.pk:
            self._generate_slug()
            self.set_post_number()

        self._update_slug()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
