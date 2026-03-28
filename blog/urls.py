from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('post/<slug:slug>/like/', views.PostLikeView.as_view(), name='post_like'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('tag/<slug:slug>/', views.TagView.as_view(), name='tag'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('about/', views.about_view, name='about'),
    # 用户认证
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    # 忘记密码
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
