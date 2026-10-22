from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import Comment, Post


def recount_comments(post_id):
    Post.objects.filter(pk=post_id).update(
        comments_count=Comment.objects.filter(post_id=post_id).count()
    )


def recount_likes(post_id):
    Post.objects.filter(pk=post_id).update(
        likes_count=Post.likes.through.objects.filter(post_id=post_id).count()
    )


@receiver(post_save, sender=Comment)
def comment_saved(sender, instance, created, **kwargs):
    if created:
        recount_comments(instance.post_id)


@receiver(post_delete, sender=Comment)
def comment_deleted(sender, instance, **kwargs):
    recount_comments(instance.post_id)


@receiver(m2m_changed, sender=Post.likes.through)
def likes_changed(sender, instance, action, reverse, pk_set, **kwargs):
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    if reverse:
        for post_id in (pk_set or []):
            recount_likes(post_id)
    else:
        recount_likes(instance.pk)