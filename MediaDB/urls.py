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

    #path('login/', user_views.loginPage, name='login'),

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