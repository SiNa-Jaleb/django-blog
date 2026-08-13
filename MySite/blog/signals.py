from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from .models import Post, Ticket

@receiver(m2m_changed, sender=Post.likes.through)
def like_signal(sender, instance, **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()

@receiver(pre_save, sender=Ticket)
def update_ticket_status(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_ticket = Ticket.objects.get(id=instance.id)

    if old_ticket.answer != instance.answer:
        instance.status = Ticket.Status.CHECK