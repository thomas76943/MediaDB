from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users.views import register, userProfile, memberProfile, memberProfileActivity, memberProfileStats, profileSection, userList, activityFeed

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Django Administrator Back-End URLs
    path('admin/', admin.site.urls),

    # Media App URLs
    path('', include('media.urls')),

    #Register, login and logout
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    #Current User's Profile
    path('profile/', userProfile, name='userProfile'),

    # Current User's List
    path('list/', userList.as_view(), name='user-List'),

    # Current User's Feed
    path('feed/', activityFeed, name='activity-feed'),

    #Other User Profiles
    path('user/<str:username>', memberProfile.as_view(), name='member-profile-detail'),
    path('user/<str:username>/activity', memberProfileActivity.as_view(), name='member-profile-activity-detail'),
    path('user/<str:username>/stats', memberProfileStats.as_view(), name='member-profile-stats-detail'),

    #Profile Section Edit Page
    path('profile-section/<str:slug>', profileSection.as_view(), name='member-profile-section-edit'),

    #Authentication Required for C/U/D Operations via the Django REST API
    path('api-auth/', include('rest_framework.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)