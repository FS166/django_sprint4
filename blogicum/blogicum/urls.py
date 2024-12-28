"""blogicum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog import views

handler403 = "pages.views.csrf_failure"
handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"

urlpatterns = [path('admin/', admin.site.urls),
               path('auth/', include('django.contrib.auth.urls')),
               path('', include(('blog.urls', 'blog'), namespace='blog')),
               path('pages/',
                    include(('pages.urls', 'pages'), namespace='pages')),

               path('auth/login/',
                    views.CustomLoginView.as_view(
                        template_name='registration/login.html'),
                    name='login'),

               path('auth/logout/',
                    auth_views.LogoutView.as_view(
                        template_name='registration/logged_out.html'
                    ),
                    name='logout'),

               path('auth/registration/', views.registration,
                    name='registration'),

               path('auth/password_reset/', views.password_reset,
                    name='password_reset'),
               path('auth/password_reset_done/', views.password_reset_done,
                    name='password_reset_done'),
               path('auth/password_reset_confirm/<int:uidb64>/<str:token>/',
                    views.password_reset_confirm,
                    name='password_reset_confirm'),
               path('auth/password_reset_complete/',
                    views.password_reset_complete,
                    name='password_reset_complete'),

               path('auth/password_change/', views.password_change,
                    name='password_change'),

               ] + static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
