from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('toggle-watched/', views.toggle_watched, name='toggle_watched'),
    path('toggle-read/', views.toggle_read, name='toggle_read'),
    path('create-post/', views.create_post, name='create_post'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/followers/', views.get_followers, name='followers'),
    path('profile/<str:username>/following/', views.get_following, name='following'),
    path('profile/update-image/', views.update_profile_image, name='update_profile_image'),
    path('toggle-follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/get-comments/', views.get_comments, name='get_comments'),
]
