

from category.models import Category


def menu_links(request):
    
    links = Category.objects.all()
    return dict(links = links)
#now we can access links variable in any template we must register it in settings.py