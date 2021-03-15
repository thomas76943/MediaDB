"""MediaDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from users import views as user_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', user_views.userProfile, name='userProfile'),

    path('user/<str:username>', user_views.memberProfile.as_view(), name='member-profile-detail'),
    path('user/<str:username>/activity', user_views.memberProfileActivity.as_view(), name='member-profile-activity-detail'),

    path('profile-section/<str:slug>', user_views.profileSection.as_view(), name='member-profile-section-edit'),

    path('list/', user_views.userList.as_view(), name='user-List'),

    path('feed/', user_views.activityFeed, name='activity-feed'),

    #MediaDB URLs
    path('', include('media.urls')),

    #Authentication Required for C/U/D Operations via the API
    path('api-auth/', include('rest_framework.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)