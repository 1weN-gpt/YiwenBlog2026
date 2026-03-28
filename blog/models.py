from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from ckeditor.fields import RichTextField


class Category(models.Model):
    name = models.CharField('分类名称', max_length=100)
    slug = models.SlugField('URL别名', unique=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField('标签名称', max_length=100)
    slug = models.SlugField('URL别名', unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]

    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('URL别名', unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    cover_image = models.ImageField('封面图', upload_to='posts/%Y/%m/', blank=True)
    summary = models.TextField('摘要', max_length=500, blank=True)
    content = RichTextField('内容')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField('浏览量', default=0)
    is_featured = models.BooleanField('推荐', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    content = models.TextField('评论内容')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    is_approved = models.BooleanField('已审核', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='文章')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)

    class Meta:
        verbose_name = '文章点赞'
        verbose_name_plural = '文章点赞'
        unique_together = ['post', 'user']  # 一个用户只能点赞一次

    def __str__(self):
        return f'{self.user.username} 点赞了 {self.post.title}'


class SiteConfig(models.Model):
    # 头像
    avatar = models.ImageField('头像', upload_to='site/', blank=True)
    
    # 联系方式
    github_url = models.URLField('GitHub链接', blank=True, default='#')
    wechat_id = models.CharField('微信号', max_length=100, blank=True, default='')
    email = models.EmailField('邮箱地址', blank=True, default='')
    
    # 友情链接
    friend_link_1_name = models.CharField('友情链接1名称', max_length=50, blank=True, default='')
    friend_link_1_url = models.URLField('友情链接1地址', blank=True, default='')
    friend_link_2_name = models.CharField('友情链接2名称', max_length=50, blank=True, default='')
    friend_link_2_url = models.URLField('友情链接2地址', blank=True, default='')
    friend_link_3_name = models.CharField('友情链接3名称', max_length=50, blank=True, default='')
    friend_link_3_url = models.URLField('友情链接3地址', blank=True, default='')
    
    # 技术栈配置（最多8个）
    TECH_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('java', 'Java'),
        ('spring', 'Spring'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('nodejs', 'Node.js'),
        ('react', 'React'),
        ('vue', 'Vue'),
        ('angular', 'Angular'),
        ('typescript', 'TypeScript'),
        ('javascript', 'JavaScript'),
        ('html5', 'HTML5'),
        ('css3', 'CSS3'),
        ('tailwind', 'Tailwind CSS'),
        ('bootstrap', 'Bootstrap'),
        ('mysql', 'MySQL'),
        ('postgresql', 'PostgreSQL'),
        ('mongodb', 'MongoDB'),
        ('redis', 'Redis'),
        ('elasticsearch', 'Elasticsearch'),
        ('docker', 'Docker'),
        ('kubernetes', 'Kubernetes'),
        ('aws', 'AWS'),
        ('linux', 'Linux'),
        ('nginx', 'Nginx'),
        ('git', 'Git'),
        ('webpack', 'Webpack'),
    ]
    
    tech_1 = models.CharField('技术栈1', max_length=20, choices=TECH_CHOICES, blank=True, default='python')
    tech_2 = models.CharField('技术栈2', max_length=20, choices=TECH_CHOICES, blank=True, default='django')
    tech_3 = models.CharField('技术栈3', max_length=20, choices=TECH_CHOICES, blank=True, default='tailwind')
    tech_4 = models.CharField('技术栈4', max_length=20, choices=TECH_CHOICES, blank=True, default='mysql')
    tech_5 = models.CharField('技术栈5', max_length=20, choices=TECH_CHOICES, blank=True, default='')
    tech_6 = models.CharField('技术栈6', max_length=20, choices=TECH_CHOICES, blank=True, default='')
    tech_7 = models.CharField('技术栈7', max_length=20, choices=TECH_CHOICES, blank=True, default='')
    tech_8 = models.CharField('技术栈8', max_length=20, choices=TECH_CHOICES, blank=True, default='')
    
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '站点配置'
        verbose_name_plural = '站点配置'

    def __str__(self):
        return '站点配置'

    def save(self, *args, **kwargs):
        # 确保只有一个配置记录
        if not self.pk and SiteConfig.objects.exists():
            SiteConfig.objects.first().delete()
        super().save(*args, **kwargs)


class DailyVisit(models.Model):
    date = models.DateField('日期', unique=True, default=timezone.now)
    count = models.PositiveIntegerField('访问次数', default=0)

    class Meta:
        verbose_name = '日访问量'
        verbose_name_plural = '日访问量'
        ordering = ['-date']

    def __str__(self):
        return f'{self.date}: {self.count}次访问'


class PasswordResetCode(models.Model):
    """密码重置验证码"""
    email = models.EmailField('邮箱')
    code = models.CharField('验证码', max_length=6)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_used = models.BooleanField('已使用', default=False)
    fail_count = models.PositiveIntegerField('失败次数', default=0)
    locked_until = models.DateTimeField('锁定至', null=True, blank=True)

    class Meta:
        verbose_name = '密码重置验证码'
        verbose_name_plural = '密码重置验证码'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email}: {self.code}'

    def is_valid(self):
        """验证码是否有效（10分钟内）"""
        from datetime import timedelta
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=10)

    def is_locked(self):
        """是否被锁定"""
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

    def get_lock_remaining_minutes(self):
        """获取剩余锁定时间（分钟）"""
        if self.locked_until:
            remaining = self.locked_until - timezone.now()
            return max(0, int(remaining.total_seconds() / 60))
        return 0
