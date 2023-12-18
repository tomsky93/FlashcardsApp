import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import (CreateView, DeleteView, ListView, 
                                  UpdateView)
from .forms import CategoryForm, FlashcardForm  
from .models import Category, Flashcard


class CategoryMixin(LoginRequiredMixin, UserPassesTestMixin):  
    model = Category
    context_object_name = 'categories'
    
    def get_object(self):
        category_id = self.kwargs['category_id']
        return get_object_or_404(Category, pk=category_id)

    def test_func(self):
        return self.get_object().user == self.request.user
   
    
    def get_success_url(self):
        return reverse('flashcards:category_detail', kwargs={'pk': self.object.pk})
    

class CategoryCreateView(LoginRequiredMixin, CreateView): 
    form_class = CategoryForm
    template_name = 'flashcards/category/create_update_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        messages.success(self.request, 'Category has been created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request,"Something went wrong. Try again.")
        return self.form_invalid(form)

class CategoryDetailView(CategoryMixin, ListView): 
    template_name = 'flashcards/category/detail.html'
    context_object_name = 'flashcards'

    def get_queryset(self):
        return Flashcard.objects.filter(category=self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context

class CategoryUpdateView(CategoryMixin, UpdateView): 
    template_name = 'flashcards/category/create_update_form.html'
    fields = ['category_name']

    def get_success_url(self):
        return reverse ('flashcards:dashboard')   
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        messages.success(self.request, 'The category has been updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.warning(self.request,"Something went wrong. Try again.")
        return self.form_invalid(form)

class CategoryDeleteView(CategoryMixin, DeleteView):   
    template_name = 'flashcards/category/delete.html'  
    
    def get_success_url(self):
        messages.success(self.request, 'The category has been deleted.')
        return reverse('flashcards:dashboard')
    

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'flashcards/category/delete.html'
    context_object_name = 'category'

    def get_object(self, queryset=None):
        category_id = self.kwargs.get('category_id')
        return get_object_or_404(Category, pk=category_id)

    def get_success_url(self):
        messages.success(self.request, 'The category has been deleted.')
        return reverse('flashcards:dashboard')

    def test_func(self):
        category = self.get_object()
        return category.user == self.request.user
        
class FlashcardMixin(LoginRequiredMixin, UserPassesTestMixin):  
    model = Flashcard
    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return self.get_object().category.get_absolute_url()

    
class FlashcardCreateView(LoginRequiredMixin, CreateView): 
    form_class = FlashcardForm
    redirect_url = 'flashcards:dashboard'
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["category_id"] = self.kwargs.get("category_id")
        context["form"].fields["category"].initial = context["category_id"]
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def create_flashcard(self, form):
        form_type = self.request.POST['form_type']
       
        if form_type == 'separate_fields':
            flashcard = form.save(commit=False)
            flashcard.user = self.request.user
            flashcard.save()
                
        elif form_type == 'list_data':
            flashcards = self.request.POST.get('question').split('\n')
            for entry in flashcards:
                flashcard_data = entry.strip().split('-')
                if len(flashcard_data) == 2:
                    question, answer = map(str.strip, flashcard_data)
                    question = question[:100]
                    answer = answer[:100]
                    flashcard = Flashcard(question=question, answer=answer, user=self.request.user, category_id=self.kwargs.get("category_id")) 
                    flashcard.save()
            
    def form_valid(self, form):
        self.create_flashcard(form)
        messages.success(self.request, "Flashcard added successfully.")
        category_id = self.kwargs.get("category_id")
        if category_id:
            return redirect('flashcards:category_detail', category_id=category_id)
        else:
            return redirect('flashcards:dashboard')

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error in {field}: {error}")
        return super().form_invalid(form)

class FlashcardUpdateView(FlashcardMixin, UpdateView): 
    fields = ['question', 'answer']
    template_name = 'flashcards/flashcard/update_form.html'  

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        messages.success(self.request, 'Flashcard has been updated successfully.')
        return super().form_valid(form)


class FlashcardDeleteView(FlashcardMixin,DeleteView):
    template_name = 'flashcards/flashcard/delete.html'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['return_url'] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class QuizMixin(LoginRequiredMixin):  
    def get_category_object(self,request,category_id):
        return get_object_or_404(Category, id=category_id, user=request.user)
 
    def get_random_flashcard(self, category, n=1):
        if category.count < 1:
            return None
        
        flashcards = Flashcard.objects.filter(category=category)
        flashcards_with_weights = []

        for flashcard in flashcards:
            weight = 1 / max(0.01, float(flashcard.answers_ratio))  
            flashcards_with_weights.append((flashcard, weight))

        selected_flashcards = random.sample(flashcards_with_weights, k=min(n, len(flashcards_with_weights)))

        if n == 1:
            return selected_flashcards[0][0]
        else:
            return [flashcard for flashcard, _ in selected_flashcards]


    def get(self, request, category_id):
        category = self.get_category_object(request,category_id)
        
        if category.count < 4:
            messages.warning(request, "Not enough flashcards in category (less than 4).")
            return redirect('flashcards:dashboard')

        
        random_flashcard = self.get_random_flashcard(category)  
        if not random_flashcard:
            messages.warning(request, "No flashcards in category.")
            return redirect('flashcards:dashboard')
        
        return render(request, self.template_name, {'category': category, 'random_flashcard': random_flashcard})

class RandomFlashcardsView(QuizMixin, View):   
    template_name = 'flashcards/flashcard/detail.html'  
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def post(self,request,category_id):
        question_id = request.POST.get('question_id')
        action = request.POST.get('action')
        flashcard = Flashcard.objects.get(pk=question_id)
        
        if action == 'know':
            flashcard.flashcard_know_count += 1
        elif action == 'dont_know':
            flashcard.flashcard_dont_know_count += 1
        
        flashcard.flashcard_display_count += 1
        flashcard.save()
        return redirect(reverse('flashcards:random_flashcards', args=[category_id]))

class QuizView(QuizMixin, View): 
    template_name = 'flashcards/quiz/quiz.html'

    def get(self, request, category_id):
        category = self.get_category_object(request,category_id)
        if category.count < 4:
            messages.warning(request, "Not enough flashcards in category (less than 4).")
            return redirect('flashcards:dashboard')
           
        choices = self.get_random_flashcard(category, n=4)
        if not choices:
            messages.warning(request, "No flashcards in category.")
            return redirect('flashcards:dashboard')
        
        question = random.choice(choices)
        random.shuffle(choices)
        return render(request, self.template_name, {'category': category, 'question': question, 'choices': choices})
    
    def post(self, request,category_id):
        category = self.get_category_object(request,category_id) 
        session_data = request.session.setdefault('quiz_data', {
         'category_id': category_id,   
        'question_count': 0,
        'correct_count': 0,
        'incorrect_count': 0,
        })

        if session_data['category_id'] != category_id:
            session_data['category_id'] = category_id
            session_data['question_count'] = 0
            session_data['correct_count'] = 0
            session_data['incorrect_count'] = 0

        flashcard = Flashcard.objects.get(pk=request.POST.get('question_id'))  
        user_answer = request.POST.get('answer')  
        correct_answer = flashcard.question 
        is_correct = (user_answer == correct_answer) 
        flashcard.update_instance(is_correct)
        
        session_data['question_count'] += 1
        if is_correct:
            session_data['correct_count'] += 1
        else:
            session_data['incorrect_count'] += 1
      
        QUIZ_QUESTIONS = 20
        if session_data['question_count'] == QUIZ_QUESTIONS:
            correct_count = session_data['correct_count']
            accuracy_score = correct_count * (100/QUIZ_QUESTIONS)
            accuracy_percent = (correct_count / QUIZ_QUESTIONS) * 100
            request.session.pop('quiz_data', None)
            MAX_CIRCUMFERENCE = 880  
            stroke_dashoffset = MAX_CIRCUMFERENCE - (accuracy_score * 8.8)  
            context = {
                'category': category_id,
                'accuracy_percent': accuracy_percent,
                'stroke_dashoffset': stroke_dashoffset,
            }

            return render(request, 'flashcards/quiz/quiz_summary.html', context)
            
        request.session.modified = True 
        
        choices = self.get_random_flashcard(category, n=4)
        next_question = random.choice(choices)
        progress_percentage = (session_data['question_count'] / QUIZ_QUESTIONS) * 100  
        context = {
                'category': category_id,
                'question': next_question,
                'choices': choices,
                'progress_percentage': progress_percentage
                }
        return render(request, self.template_name, context)
     
class CompletionQuizView(QuizMixin, View):   
    template_name = 'flashcards/quiz/completion_quiz.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response
  
    def post(self, request, category_id):
        user_answer = request.POST.get('user_translation')
        flashcard = Flashcard.objects.get(id=request.POST.get('flashcard_id'), category=category_id)
        is_correct = (user_answer.strip().lower() == flashcard.question.strip().lower())
        flashcard.update_instance(is_correct)
        return redirect(reverse('flashcards:completion_quiz', args=[category_id]))

@require_POST
def add_to_favorites(request, flashcard_id):
    if request.method == 'POST':
        flashcard = Flashcard.objects.get(pk=flashcard_id)
        flashcard.is_favorite = not flashcard.is_favorite
        flashcard.save()
        return JsonResponse({'is_favorite': flashcard.is_favorite})
    
