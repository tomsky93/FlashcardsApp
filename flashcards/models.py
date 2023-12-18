from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date
import uuid


class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0) 
   
    class Meta:
        verbose_name_plural = "Categories"
        
        indexes = [
            models.Index(fields=['user', 'category_name']),
        ]

    def __str__(self):
        return self.category_name
    
    def get_absolute_url(self):
        return reverse('flashcards:category_detail', args=[str(self.id)])
   

class Flashcard(models.Model):
    question =  models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateField(auto_now_add= True)
    repeated_date = models.DateField(null=True, blank=True)
    repetitions_num = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    flashcard_display_count = models.PositiveIntegerField(default=0)
    flashcard_know_count = models.PositiveIntegerField(default=0)
    flashcard_dont_know_count = models.PositiveIntegerField(default=0)
    is_favorite = models.BooleanField(default=False)
    answers_ratio = models.DecimalField(default=0, decimal_places=2, max_digits=3)

    class Meta:
        verbose_name_plural = "Flashcards"
        indexes = [
            models.Index(fields=['user', '-question']),
        ]

    def __str__(self):
        return self.question


    @property
    def calculate_ratio(self):
        total_answers = self.correct_answers + self.wrong_answers
        if total_answers == 0:
            return 0

        correct_ratio = self.correct_answers / total_answers

        if self.flashcard_dont_know_count == 0:
            know_ratio = 1
        else:
            know_ratio = self.flashcard_know_count / (self.flashcard_know_count + self.flashcard_dont_know_count)
       
        final_ratio = (correct_ratio * 0.6) + (know_ratio * 0.4)
        return final_ratio

    
    def update_instance(self, is_correct):
        if is_correct:
            self.correct_answers +=1
        else:
            self.wrong_answers +=1
        self.repetitions_num +=1
        self.repeated_date = date.today()
        self.answers_ratio = self.calculate_ratio
        self.save()
   
