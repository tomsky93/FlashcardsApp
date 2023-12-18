from django import template
from ..models import Category, Flashcard
import random
register = template.Library()

    
@register.simple_tag
def get_categories(user):
    return Category.objects.filter(user=user)

@register.inclusion_tag('flashcards/flashcard_list_tag.html')
def favourites_by_category(user,category):
    favourites = Flashcard.objects.filter(user=user, category=category, is_favorite=True)
    return {'flashcards': favourites}   

@register.inclusion_tag('flashcards/flashcard_list_tag.html')
def flashcards_by_category(user,category):
    flashcards = Flashcard.objects.filter(user=user, category=category)
    return {'flashcards': flashcards}   

@register.inclusion_tag('flashcards/flashcard_list_tag.html')
def learned_flashcards(user,category):
    flashcards = Flashcard.objects.filter(user=user, category=category,  answers_ratio__gte=0.8)
    return {'flashcards': flashcards}   

@register.inclusion_tag('flashcards/flashcard_list_tag.html')
def studying_flashcards(user,category):
    flashcards = Flashcard.objects.filter(user=user, category=category,  answers_ratio__lte=0.8)
    return {'flashcards': flashcards}   


@register.inclusion_tag('flashcards/word_cloud_tag.html')
def flashcard_cloud(user):
    def round_to_nearest_fifth(number):
        return round(number * 20) / 20
   
    questions = list(Flashcard.objects.filter(user_id=user, answers_ratio__lt=0.81)[:50])
    random.shuffle(questions)
    flashcards = [{'question': q.question, 'answer': q.answer, 'answers_ratio': round_to_nearest_fifth(q.answers_ratio)} for q in questions]

    return {'flashcards': flashcards}