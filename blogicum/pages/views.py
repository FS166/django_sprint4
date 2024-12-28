from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import StaticPage
from .forms import StaticPageForm


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


class StaticPageCreateView(CreateView):
    model = StaticPage
    form_class = StaticPageForm
    template_name = 'pages/create_static_page.html'
    success_url = reverse_lazy('pages:static_page_list')


class StaticPageUpdateView(UpdateView):
    model = StaticPage
    form_class = StaticPageForm
    template_name = 'pages/update_static_page.html'
    success_url = reverse_lazy('pages:static_page_list')


class StaticPageListView(ListView):
    model = StaticPage
    template_name = 'pages/static_page_list.html'
    context_object_name = 'pages'


def csrf_failure(request, reason=""):
    return render(request, 'pages/403csrf.html', {'reason': reason},
                  status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)
