from django.shortcuts import render

from . models import Post


# Create your views here.
def list_blog(request):
    blogs = Post.objects.all().order_by('-created_add')[:10]
    blog_recend = Post.objects.all().order_by('created_add')[:10]
    
    print(blogs)
    context = {
        'blogs': blogs,
        'blog_recend': blog_recend,
    }

    return render(request, 'blogs/index.html', context)