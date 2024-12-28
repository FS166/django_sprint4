from django.urls import path

from .views import (AboutView, RulesView, StaticPageCreateView,
                    StaticPageUpdateView, StaticPageListView)

app_name = 'pages'

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('rules/', RulesView.as_view(), name='rules'),
    path('create/', StaticPageCreateView.as_view(), name='create_static_page'),
    path('list/', StaticPageListView.as_view(), name='static_page_list'),
    path('<int:pk>/edit/',
         StaticPageUpdateView.as_view(),
         name='edit_static_page'),
]
