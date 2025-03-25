from .models import Category

def global_context(request):
    categories = Category.objects.all()
    dark_mode = request.session.get('dark_mode', False)
    return {'categories': categories, 'dark_mode': dark_mode}