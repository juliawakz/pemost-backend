from django.conf import settings
from django.shortcuts import render


def index(request):
    context_data = {
        "title": f"{settings.PROJECT_NAME}",
        "heading": f"{settings.PROJECT_NAME}",
    }
    return render(request, "index.html", context=context_data)


def about(request):
    context_data = {"title": "About Pemost"}
    return render(request, "about.html", context=context_data)


def releases(request):
    context_data = {"title": "Check Out Release notes"}
    return render(request, "releases.html", context=context_data)


def chat_room(request):
    context_data = {"title": "Pemost Notification"}
    return render(request, "channels/notifications.html", context=context_data)


def handler404(request, exception):
    return render(request, "errors/404.html", context={}, status=404)


def handler500(request):
    return render(request, "errors/500.html", context={}, status=500)
