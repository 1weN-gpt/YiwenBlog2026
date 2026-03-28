from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from datetime import timedelta
from .models import Post, Category, Tag, Comment, PostLike, DailyVisit
from .forms import CommentForm, SearchForm


class HomeView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(status='published', is_featured=True)
        context['categories'] = Category.objects.all()[:10]
        context['tags'] = Tag.objects.all()[:20]
        context['total_posts'] = Post.objects.filter(status='published').count()
        
        # 日访问量统计
        today = timezone.now().date()
        daily_visit, created = DailyVisit.objects.get_or_create(date=today)
        daily_visit.count += 1
        daily_visit.save()
        context['daily_visits'] = daily_visit.count
        
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # 相关文章
        context['related_posts'] = Post.objects.filter(
            status='published',
            category=post.category
        ).exclude(id=post.id)[:4]
        
        # 上一篇
        context['previous_post'] = Post.objects.filter(
            status='published',
            created_at__lt=post.created_at
        ).order_by('-created_at').first()
        
        # 下一篇
        context['next_post'] = Post.objects.filter(
            status='published',
            created_at__gt=post.created_at
        ).order_by('created_at').first()
        
        # 热门文章（按浏览量）
        context['hot_posts'] = Post.objects.filter(
            status='published'
        ).exclude(id=post.id).order_by('-views')[:5]
        
        # 评论和评论表单
        context['comments'] = post.comments.filter(is_approved=True, parent=None)
        context['comment_form'] = CommentForm()
        
        # 点赞信息
        context['likes_count'] = post.likes.count()
        if self.request.user.is_authenticated:
            context['user_has_liked'] = post.likes.filter(user=self.request.user).exists()
        else:
            context['user_has_liked'] = False
        
        return context


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(status='published', category=self.category).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagView(ListView):
    model = Post
    template_name = 'blog/tag.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(status='published', tags=self.tag).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class CommentCreateView(View):
    @method_decorator(login_required, name='dispatch')
    def post(self, request, slug):
        from django.http import JsonResponse
        from django.utils import timezone
        post = get_object_or_404(Post, slug=slug, status='published')
        
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'success': False, 'error': '评论内容不能为空'})
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'username': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        })


class SearchView(ListView):
    model = Post
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Post.objects.filter(
                status='published'
            ).filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(summary__icontains=query)
            ).select_related('author', 'category').prefetch_related('tags')
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['search_form'] = SearchForm(initial={'q': self.request.GET.get('q', '')})
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 为每个分类计算文章数量
        for category in context['categories']:
            category.post_count = Post.objects.filter(category=category, status='published').count()
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.filter(status='published').count()
        return context


def about_view(request):
    from django.db.models import Sum, Count
    context = {
        'total_posts': Post.objects.filter(status='published').count(),
        'categories_count': Category.objects.count(),
        'tags_count': Tag.objects.count(),
        'total_views': Post.objects.filter(status='published').aggregate(Sum('views'))['views__sum'] or 0,
        'total_likes': PostLike.objects.count(),
        'total_comments': Comment.objects.filter(is_approved=True).count(),
    }
    return render(request, 'blog/about.html', context)


# 用户认证视图
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来，{user.username}！')
            # 获取next参数，如果没有则跳转到首页
            next_url = request.POST.get('next') or request.GET.get('next') or 'blog:home'
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'blog/login.html', {'next': request.GET.get('next', '')})


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 验证
        if password != password_confirm:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'blog/register.html')
        
        if len(password) < 6:
            messages.error(request, '密码长度至少为6位')
            return render(request, 'blog/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已被注册')
            return render(request, 'blog/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'blog/register.html')
        
        # 创建用户
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # 发送注册成功邮件
        from django.core.mail import send_mail
        from django.conf import settings
        
        blog_url = request.build_absolute_uri('/')
        subject = '欢迎加入逸文博客 - 注册成功'
        message = f'''亲爱的 {username}，您好！

恭喜您成功注册逸文博客！

您的注册信息如下：
- 用户名：{username}
- 博客地址：{blog_url}

温馨提示：
1. 请妥善保管您的密码，不要泄露给他人
2. 建议定期更换密码以保障账户安全
3. 如有任何问题，欢迎通过博客联系我们

感谢您对逸文博客的支持，祝您使用愉快！

此邮件由系统自动发送，请勿回复。
'''
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except:
            pass  # 邮件发送失败不影响注册流程
        
        messages.success(request, '注册成功！请登录')
        return redirect('blog:login')
    
    return render(request, 'blog/register.html')


def user_logout(request):
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('blog:home')


def forgot_password(request):
    """忘记密码 - 发送验证码"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 检查邮箱是否存在
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, '该邮箱未注册')
            return render(request, 'blog/forgot_password.html')
        
        # 检查是否有未过期的验证码记录
        from .models import PasswordResetCode
        
        # 获取该邮箱最新的验证码记录
        latest_code = PasswordResetCode.objects.filter(email=email).order_by('-created_at').first()
        
        # 检查是否被锁定
        if latest_code and latest_code.is_locked():
            remaining = latest_code.get_lock_remaining_minutes()
            messages.error(request, f'验证失败次数过多，请{remaining}分钟后重试')
            return render(request, 'blog/forgot_password.html')
        
        # 检查1分钟内是否已发送过验证码
        if latest_code and (timezone.now() - latest_code.created_at) < timedelta(minutes=1):
            messages.error(request, '验证码发送过于频繁，请1分钟后再试')
            return render(request, 'blog/forgot_password.html')
        
        # 生成6位数字验证码
        import random
        code = ''.join(random.choices('0123456789', k=6))
        
        # 保存验证码
        PasswordResetCode.objects.create(email=email, code=code)
        
        # 发送邮件
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = '逸文博客 - 密码重置验证码'
        message = f'''亲爱的 {user.username}，您好！

您正在申请重置密码，验证码为：

【{code}】

验证码10分钟内有效，请勿泄露给他人。

如非本人操作，请忽略此邮件。

此邮件由系统自动发送，请勿回复。
'''
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, '验证码已发送至您的邮箱，请查收')
            # 跳转到验证页面
            return redirect('blog:verify_code')
        except Exception as e:
            messages.error(request, '邮件发送失败，请稍后重试')
            return render(request, 'blog/forgot_password.html')
    
    return render(request, 'blog/forgot_password.html')


def verify_code(request):
    """验证验证码"""
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        
        from .models import PasswordResetCode
        
        # 获取该邮箱最新的未使用验证码
        reset_code = PasswordResetCode.objects.filter(
            email=email,
            is_used=False
        ).order_by('-created_at').first()
        
        if not reset_code:
            messages.error(request, '验证码不存在，请重新获取')
            return render(request, 'blog/verify_code.html')
        
        # 检查是否被锁定
        if reset_code.is_locked():
            remaining = reset_code.get_lock_remaining_minutes()
            messages.error(request, f'验证失败次数过多，请{remaining}分钟后重试')
            return render(request, 'blog/verify_code.html')
        
        # 检查验证码是否过期
        if not reset_code.is_valid():
            messages.error(request, '验证码已过期，请重新获取')
            return render(request, 'blog/verify_code.html')
        
        # 验证验证码
        if reset_code.code != code:
            reset_code.fail_count += 1
            
            # 失败5次锁定30分钟
            if reset_code.fail_count >= 5:
                reset_code.locked_until = timezone.now() + timedelta(minutes=30)
                reset_code.save()
                messages.error(request, '验证失败次数过多，请30分钟后重试')
                return render(request, 'blog/verify_code.html')
            else:
                remaining = 5 - reset_code.fail_count
                messages.error(request, f'验证码错误，还剩{remaining}次机会')
                reset_code.save()
                return render(request, 'blog/verify_code.html')
        
        # 验证成功，标记为已使用
        reset_code.is_used = True
        reset_code.save()
        
        # 将邮箱存入session，用于重置密码
        request.session['reset_email'] = email
        
        return redirect('blog:reset_password')
    
    return render(request, 'blog/verify_code.html')


def reset_password(request):
    """重置密码"""
    # 检查是否有重置权限
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, '请先验证邮箱')
        return redirect('blog:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 验证密码
        if password != password_confirm:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'blog/reset_password.html')
        
        if len(password) < 6:
            messages.error(request, '密码长度至少为6位')
            return render(request, 'blog/reset_password.html')
        
        # 重置密码
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            
            # 清除session
            del request.session['reset_email']
            
            messages.success(request, '密码重置成功，请使用新密码登录')
            return redirect('blog:login')
        except User.DoesNotExist:
            messages.error(request, '用户不存在')
            return redirect('blog:forgot_password')
    
    return render(request, 'blog/reset_password.html')


# 点赞视图
class PostLikeView(View):
    @method_decorator(login_required, name='dispatch')
    def post(self, request, slug):
        from django.http import JsonResponse
        post = get_object_or_404(Post, slug=slug, status='published')
        
        # 检查是否已点赞
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        
        if not created:
            # 已点赞，取消点赞
            like.delete()
            user_has_liked = False
        else:
            user_has_liked = True
        
        return JsonResponse({
            'success': True,
            'likes_count': post.likes.count(),
            'user_has_liked': user_has_liked
        })
