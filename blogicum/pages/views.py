from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def error_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def error_csrf(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def error_500(request):
    return render(request, 'pages/500.html', status=500)
