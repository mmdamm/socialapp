from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
from taggit.managers import TaggableManager
from django.urls import reverse
from django_resized import ResizedImageField

# Create your models here.


class User(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to="account_images/", blank=True, null=True)
    job = models.CharField(max_length=250, null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True)


class Account(models.Model):
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=200, blank=True, null=True)
    photo = ResizedImageField(upload_to="account_images/", size=[500, 500], quality=100, crop=['middle', 'center'],
                              blank=True, null=True)
    job = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    # relations

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')

    # data
    description = models.TextField(max_length=250)
    # date
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # tag
    tag = TaggableManager()
    # image_file = ResizedImageField(upload_to="post_images/", size=[600, 400], quality=100, crop=['middle', 'center'])
    likes = models.ManyToManyField(User, related_name='like_posts', blank=True)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):
        return self.author.username

    def get_absolute_url(self):
        return reverse('socialapp:post_detail', args=[self.id])

    # def delete(self, *args, **kwargs):
    #     storage, path = self.image_file.storage, self.image_file.path
    #     storage.delete(path)
    #     super().delete(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comment')
    name = models.CharField(max_length=30)
    body = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):
        return self.name
