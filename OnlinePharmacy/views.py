from django.shortcuts import render


def error404_view(request, exception):
    return render(request, 'error_page.html', status=404)
