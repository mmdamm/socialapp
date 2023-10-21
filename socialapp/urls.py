from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm

app_name = 'socialapp'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(), name="login"),
    # path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('logout/', views.log_out, name="logout"),
    path('ticket', views.ticket, name='ticket'),
    # reset password
    path('password-reset/', auth_views.PasswordResetView.as_view(success_url='done'), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(success_url='/password-reset/complete'),
         name="password_reset_confirm"),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('register/', views.register, name='register'),
    path('register/edit', views.edit_account, name='edit_account'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/create_post', views.create_post, name="create_post"),
    path('posts/<slug:tag_slug>', views.post_list, name='post_list_by_tag'),
    path('posts/detail/<int:pk>', views.post_detail, name='post_detail'),
    #tamrin
    path('posts/detail/comment/<post_id>', views.post_comment_user, name='post_comment'),
    path('posts/detail/comment/add/<post_id>', views.post_comment, name='post_comment_add'),
    path('search', views.post_search, name="post_search"),
    path('edit_post/<post_id>', views.edit_post, name="edit_post"),
    path('delete_post/<post_id>', views.delete_post, name="delete_post"),
    path('like_post/', views.like_post, name='like_post'),
    path('save_post/', views.save_post, name='save_post'),






]
