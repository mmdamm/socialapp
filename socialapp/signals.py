from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from .models import Post
from django.core.mail import send_mail


@receiver(m2m_changed, sender=Post.likes.through)
def user_like(sender, instance, **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()


@receiver(post_delete, sender=Post)
def delete_post(sender, instance, **kwargs):
    author = instance.author
    subject = f"Your post delete."
    message = f"Your post with id({instance.id}) has been delete."
    send_mail(subject, message, 'mohammad2547mohseny@gamil.com', [author.email],
              fail_silently=False)