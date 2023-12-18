from django.contrib import admin
from .models import Flashcard, Category


# Register your models here.

class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'category','user','date_added',)

admin.site.register(Flashcard, FlashcardAdmin)
admin.site.register(Category)
