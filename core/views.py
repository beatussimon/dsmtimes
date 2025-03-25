from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Category, SubscriptionPlan, Comment, NewsletterSubscription, UserProfile, Tag  # Added Tag import

def home(request):
    featured_article = Article.objects.filter(status='published', is_premium=False).order_by('-published_at').first()
    latest_articles = Article.objects.filter(status='published').order_by('-published_at')[:12]  # Increased to 12
    trending_articles = Article.objects.filter(status='published').order_by('-views_count')[:6]  # Increased to 6
    categories = Category.objects.all()
    return render(request, 'core/home.html', {
        'featured_article': featured_article,
        'latest_articles': latest_articles,
        'trending_articles': trending_articles,
        'categories': categories,
    })

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    if article.is_premium and (not request.user.is_authenticated or not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_subscriber):
        return render(request, 'core/premium_content.html', {'article': article})
    
    comments = article.comments.filter(is_approved=True)
    related_articles = Article.objects.filter(category=article.category, status='published').exclude(id=article.id).order_by('-published_at')[:3]
    
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        comment = Comment(article=article, user=request.user, content=content, is_approved=request.user.userprofile.is_editor if hasattr(request.user, 'userprofile') else False)
        comment.save()
        messages.success(request, 'Your comment has been submitted' + (' and approved' if comment.is_approved else ' for approval.'))
        return redirect('article_detail', slug=slug)
    
    return render(request, 'core/article_detail.html', {
        'article': article,
        'comments': comments,
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
        
        article = Article(
            title=title,
            author=request.user,
            category=Category.objects.get(id=category_id),
            content=content,
            summary=summary,
            featured_image=featured_image,
            is_premium=is_premium,
            status='pending'
        )
        article.save()
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            article.tags.add(tag)
        messages.success(request, 'Article submitted for approval.')
        return redirect('profile')
    
    categories = Category.objects.all()
    return render(request, 'core/submit_article.html', {'categories': categories})

@login_required
def subscribe(request):
    plans = SubscriptionPlan.objects.all()
    return render(request, 'core/subscribe.html', {'plans': plans})

@login_required
def profile(request):
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)
    profile = request.user.userprofile
    articles = Article.objects.filter(author=request.user).order_by('-submitted_at')
    return render(request, 'core/profile.html', {'profile': profile, 'articles': articles})

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
    return render(request, 'core/search.html', {'query': query, 'results': results})

def toggle_dark_mode(request):
    if 'dark_mode' in request.session:
        request.session['dark_mode'] = not request.session['dark_mode']
    else:
        request.session['dark_mode'] = True
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            messages.success(request, 'Registration successful! Welcome to DSM Times.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})