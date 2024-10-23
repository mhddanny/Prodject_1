from category.models import Category

def category_links(request):
    links = Category.objects.filter(level=0)
    return dict(category_links=links)