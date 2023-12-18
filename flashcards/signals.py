from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import Flashcard

@receiver(post_save, sender=Flashcard)
def update_category_flashcards_count_after_save(sender, instance, **kwargs):
    flashcard_count = Flashcard.objects.filter(category=instance.category).count()
    instance.category.count = flashcard_count
    instance.category.save()

@receiver(pre_delete, sender=Flashcard)
def update_category_flashcards_count_after_delete(sender, instance, **kwargs):
    instance.category.count -= 1
    instance.category.save()


pre_delete.connect(update_category_flashcards_count_after_delete, sender=Flashcard)


