from chat.models import Room

def room_links(request):
    link = Room.objects.all()
    return dict(link=link)