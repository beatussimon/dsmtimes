# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Category, SubscriptionPlan, Comment, NewsletterSubscription, UserProfile, Tag, ArticleMedia,Feedback,FAQ
from django import forms
from django.core.paginator import Paginator
import datetime
import random
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'social_twitter', 'social_facebook', 'social_instagram']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_special', 'color']
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}

def get_special_event():
    today = datetime.date.today()
    events = {
        (4, 7): "Karume Day",
        (1, 1): "Mwaka Mpya",
    }
    for (month, day), event in events.items():
        if today.month == month and today.day == day:
            return event
    return None

def home(request):
    breaking_news = Article.objects.filter(breaking_news=True, status='published').order_by('-published_at')[:1]
    featured_article = Article.objects.filter(status='published', is_premium=False).order_by('-published_at').first()
    latest_articles = Article.objects.filter(status='published').order_by('-published_at')
    paginator = Paginator(latest_articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    trending_articles = Article.objects.filter(status='published').order_by('-views_count')[:6]
    categories = Category.objects.all()
    return render(request, 'core/home.html', {
        'breaking_news': breaking_news,
        'featured_article': featured_article,
        'page_obj': page_obj,
        'trending_articles': trending_articles,
        'categories': categories,
    })

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status__in=['published', 'hidden'])
    if article.status == 'hidden' and (not request.user.is_authenticated or not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_chief_editor):
        return redirect('home')
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    if article.is_premium and (not request.user.is_authenticated or not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_subscriber):
        return render(request, 'core/premium_content.html', {'article': article})
    
    comments = Comment.objects.filter(article=article, parent=None).annotate(like_count=Count('likes'))
    media = article.media.all()
    
    if request.method == 'POST' and request.user.is_authenticated:
        action = request.POST.get('action')
        if action == 'comment':
            comment_id = request.POST.get('comment_id')
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')
            if comment_id:
                comment = get_object_or_404(Comment, id=comment_id, user=request.user)
                comment.content = content
                comment.save()
                messages.success(request, 'Comment updated successfully.')
            else:
                parent = Comment.objects.get(id=parent_id) if parent_id else None
                comment = Comment(article=article, user=request.user, content=content, parent=parent)
                comment.save()
                messages.success(request, 'Comment posted successfully.')
        elif action == 'like':
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id)
            if request.user in comment.likes.all():
                comment.likes.remove(request.user)
            else:
                comment.likes.add(request.user)
        elif action == 'like_article':
            if request.user in article.likes.all():
                article.likes.remove(request.user)
            else:
                article.likes.add(request.user)
        return redirect('article_detail', slug=slug)
    
    related_articles = Article.objects.filter(category=article.category, status='published').exclude(id=article.id).order_by('-published_at')[:3]
    return render(request, 'core/article_detail.html', {
        'article': article,
        'comments': comments,
        'media': media,
        'related_articles': related_articles,
    })

@login_required
def submit_article(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_editor:
        messages.error(request, 'Only editors can submit articles.')
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        content = request.POST.get('content')
        summary = request.POST.get('summary')
        featured_image = request.FILES.get('featured_image')
        is_premium = request.POST.get('is_premium') == 'on'
        tags = request.POST.get('tags', '').split(',')
        breaking_news = request.POST.get('breaking_news') == 'on'
        
        article = Article(
            title=title,
            author=request.user,
            category=Category.objects.get(id=category_id),
            content=content,
            summary=summary,
            featured_image=featured_image,
            is_premium=is_premium,
            breaking_news=breaking_news,
            status='published' if request.user.userprofile.is_chief_editor else 'pending'
        )
        article.save()
        
        media_files = request.FILES.getlist('media_files')
        media_urls = request.POST.getlist('media_urls')
        for media_file in media_files:
            ArticleMedia.objects.create(article=article, media_file=media_file, media_type='image')
        for url in media_urls:
            if url:
                ArticleMedia.objects.create(article=article, media_url=url, media_type='video')
        
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                article.tags.add(tag)
        messages.success(request, 'Article submitted successfully.')
        return redirect('profile')
    
    categories = Category.objects.all()
    return render(request, 'core/submit_article.html', {'categories': categories})

@login_required
def subscribe(request):
    plans = SubscriptionPlan.objects.all()
    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        profile = request.user.userprofile
        profile.pending_subscription = plan
        profile.save()
        messages.info(request, f'Subscription to {plan.name} submitted for approval.')
        return redirect('profile')
    return render(request, 'core/subscribe.html', {'plans': plans})

@login_required
def profile(request):
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)
    profile = request.user.userprofile
    articles = Article.objects.filter(author=request.user).order_by('-submitted_at')
    
    if request.method == 'POST':
        if 'request_editor' in request.POST:
            profile.editor_request = True
            profile.save()
            messages.success(request, 'Editor request submitted.')
        else:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'core/profile.html', {'profile': profile, 'articles': articles, 'form': form})

def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.userprofile
    articles = Article.objects.filter(author=user, status='published').order_by('-published_at')
    return render(request, 'core/public_profile.html', {'profile': profile, 'articles': articles})

def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subscription, created = NewsletterSubscription.objects.get_or_create(email=email)
        if created:
            send_mail(
                'Welcome to DSM Times Newsletter',
                'Thank you for subscribing to DSM Times! Expect the best in tech, science, and culture.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Thank you for subscribing!')
        else:
            messages.info(request, 'You are already subscribed.')
        return redirect('home')
    return render(request, 'core/newsletter_signup.html')

def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query),
            status='published'
        )
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/search.html', {'query': query, 'page_obj': page_obj})

def toggle_dark_mode(request):
    request.session['dark_mode'] = not request.session.get('dark_mode', False)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to DSM Times.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_logout(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('home')
    return redirect('home')

def live_updates(request):
    live_articles = Article.objects.filter(breaking_news=True, status='published').order_by('-published_at')
    paginator = Paginator(live_articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/live_updates.html', {'page_obj': page_obj})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=category, status='published').order_by('-published_at')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/category_detail.html', {'category': category, 'page_obj': page_obj})

def faq(request):
    faqs = FAQ.objects.all()  # Fetch all FAQs from the database
    return render(request, 'core/faq.html', {'faqs': faqs})

def feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        send_mail(
            'Feedback from DSM Times User',
            f'Message: {message}\nFrom: {request.user.username if request.user.is_authenticated else "Anonymous"}',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        messages.success(request, 'Feedback submitted successfully.')
        return redirect('feedback')
    return render(request, 'core/feedback.html')

def blog(request):
    articles = Article.objects.filter(status='published').order_by('-published_at')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/blog.html', {'page_obj': page_obj})

@login_required
def custom_admin(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_chief_editor:
        messages.error(request, 'Only the Chief Editor can access this page.')
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve_article':
            article_id = request.POST.get('article_id')
            article = get_object_or_404(Article, id=article_id, status='pending')
            article.status = 'published'
            article.published_at = timezone.now()
            article.save()
            messages.success(request, f'Article "{article.title}" approved.')
        elif action == 'hide_article':
            article_id = request.POST.get('article_id')
            article = get_object_or_404(Article, id=article_id)
            article.status = 'hidden'
            article.save()
            messages.success(request, f'Article "{article.title}" hidden.')
        elif action == 'unhide_article':
            article_id = request.POST.get('article_id')
            article = get_object_or_404(Article, id=article_id, status='hidden')
            article.status = 'published'
            article.save()
            messages.success(request, f'Article "{article.title}" unhidden.')
        elif action == 'edit_faq':
            faq_id = request.POST.get('faq_id')
            faq = get_object_or_404(FAQ, id=faq_id)
            faq.question = request.POST.get('question')
            faq.answer = request.POST.get('answer')
            faq.order = request.POST.get('order', 0)
            faq.save()
            messages.success(request, 'FAQ updated successfully.')
        elif action == 'add_faq':
            question = request.POST.get('question')
            answer = request.POST.get('answer')
            order = request.POST.get('order', 0)
            FAQ.objects.create(question=question, answer=answer, order=order)
            messages.success(request, 'FAQ added successfully.')
        elif action == 'delete_faq':
            faq_id = request.POST.get('faq_id')
            FAQ.objects.filter(id=faq_id).delete()
            messages.success(request, 'FAQ deleted successfully.')
        elif action == 'hide_feedback':
            feedback_id = request.POST.get('feedback_id')
            feedback = get_object_or_404(Feedback, id=feedback_id)
            feedback.is_hidden = True
            feedback.save()
            messages.success(request, 'Feedback hidden.')
        elif action == 'unhide_feedback':
            feedback_id = request.POST.get('feedback_id')
            feedback = get_object_or_404(Feedback, id=feedback_id)
            feedback.is_hidden = False
            feedback.save()
            messages.success(request, 'Feedback unhidden.')
        elif action == 'respond_feedback':
            feedback_id = request.POST.get('feedback_id')
            feedback = get_object_or_404(Feedback, id=feedback_id)
            feedback.response = request.POST.get('response')
            feedback.is_resolved = True
            feedback.save()
            messages.success(request, 'Feedback responded to.')
        # Existing actions (approve_subscription, promote_editor, etc.) remain unchanged
        elif action == 'approve_subscription':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            profile = user.userprofile
            if profile.pending_subscription:
                profile.is_subscriber = True
                profile.subscription_tier = 'premium' if profile.pending_subscription.name.lower() == 'premium' else 'basic'
                profile.pending_subscription = None
                profile.save()
                messages.success(request, f'Subscription approved for {user.username}.')
        elif action == 'promote_editor':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            profile = user.userprofile
            profile.is_editor = True
            profile.editor_request = False
            profile.contract_details = request.POST.get('contract_details', '')
            profile.save()
            messages.success(request, f'{user.username} promoted to editor.')
        elif action == 'fire_editor':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            profile = user.userprofile
            profile.is_editor = False
            profile.contract_details = ''
            profile.save()
            messages.success(request, f'{user.username} removed as editor.')
        elif action == 'add_category':
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category added successfully.')
            else:
                messages.error(request, 'Error adding category.')
        return redirect('custom_admin')

    # Data for template
    pending_articles = Article.objects.filter(status='pending')
    published_articles = Article.objects.filter(status='published')
    hidden_articles = Article.objects.filter(status='hidden')
    pending_subscriptions = UserProfile.objects.filter(pending_subscription__isnull=False)
    editors = UserProfile.objects.filter(is_editor=True, is_chief_editor=False)
    editor_requests = UserProfile.objects.filter(editor_request=True, is_editor=False)
    category_form = CategoryForm()
    faqs = FAQ.objects.all()
    feedbacks = Feedback.objects.all()

    return render(request, 'core/custom_admin.html', {
        'pending_articles': pending_articles,
        'published_articles': published_articles,
        'hidden_articles': hidden_articles,
        'pending_subscriptions': pending_subscriptions,
        'editors': editors,
        'editor_requests': editor_requests,
        'category_form': category_form,
        'faqs': faqs,
        'feedbacks': feedbacks,
    })

def feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        user = request.user if request.user.is_authenticated else None
        feedback_entry = Feedback(user=user, message=message)
        feedback_entry.save()
        # Optional: Keep the email notification if desired
        send_mail(
            'Feedback from DSM Times User',
            f'Message: {message}\nFrom: {user.username if user else "Anonymous"}',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=True,  # Changed to True to avoid errors if email fails
        )
        messages.success(request, 'Feedback submitted successfully.')
        return redirect('feedback')
    return render(request, 'core/feedback.html')