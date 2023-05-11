from django.shortcuts import render


def about(request):
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)


def error_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def error_csrf(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def error_500(request):
    return render(request, 'pages/500.html', status=500)
