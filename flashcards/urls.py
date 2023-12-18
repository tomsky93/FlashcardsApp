from django.urls import path
from .views import *  

app_name = "flashcards"

urlpatterns = [

     path('dashboard/', FlashcardCreateView.as_view(template_name='flashcards/dashboard.html'), name='dashboard'),
     path('create/category/', CategoryCreateView.as_view(), name='category_create'),
     path('category/<str:category_id>/', CategoryDetailView.as_view(), name='category_detail'),
     path('update_category/<str:category_id>/', CategoryUpdateView.as_view(), name= 'category_update'),
     path('delete_category/<str:category_id>/', CategoryDeleteView.as_view(), name= 'category_delete'),
     path('create/flashcard/<str:category_id>/', FlashcardCreateView.as_view(template_name='flashcards/flashcard/create_form.html'), name='flashcard_create'),
     path('edit/<int:pk>/', FlashcardUpdateView.as_view(), name= 'flashcard_update'),
     path('delete/<int:pk>/', FlashcardDeleteView.as_view(), name= 'flashcard_delete'),
     path('random/<str:category_id>/', RandomFlashcardsView.as_view(), name='random_flashcards'),
     path('completion_quiz/<str:category_id>/', CompletionQuizView.as_view(), name='completion_quiz'),
     path('quiz/<str:category_id>/', QuizView.as_view(), name='quiz'),  
     path('add_to_favorites/<int:flashcard_id>/', add_to_favorites, name='add_to_favorites'),  
    
     
            ]