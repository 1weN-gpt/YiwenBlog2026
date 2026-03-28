from .models import SiteConfig


TECH_ICONS = {
    'python': ('fab fa-python', 'text-blue-500'),
    'django': ('fas fa-globe', 'text-green-600'),
    'java': ('fab fa-java', 'text-red-500'),
    'spring': ('fas fa-leaf', 'text-green-500'),
    'go': ('fab fa-golang', 'text-cyan-500'),
    'rust': ('fab fa-rust', 'text-orange-500'),
    'nodejs': ('fab fa-node-js', 'text-green-500'),
    'react': ('fab fa-react', 'text-blue-400'),
    'vue': ('fab fa-vuejs', 'text-green-500'),
    'angular': ('fab fa-angular', 'text-red-600'),
    'typescript': ('fas fa-code', 'text-blue-600'),
    'javascript': ('fab fa-js', 'text-yellow-400'),
    'html5': ('fab fa-html5', 'text-orange-500'),
    'css3': ('fab fa-css3-alt', 'text-blue-500'),
    'tailwind': ('fas fa-wind', 'text-cyan-400'),
    'bootstrap': ('fab fa-bootstrap', 'text-purple-500'),
    'mysql': ('fas fa-database', 'text-blue-600'),
    'postgresql': ('fas fa-database', 'text-blue-400'),
    'mongodb': ('fas fa-leaf', 'text-green-500'),
    'redis': ('fas fa-server', 'text-red-500'),
    'elasticsearch': ('fas fa-search', 'text-yellow-500'),
    'docker': ('fab fa-docker', 'text-blue-500'),
    'kubernetes': ('fas fa-dharmachakra', 'text-blue-600'),
    'aws': ('fab fa-aws', 'text-orange-400'),
    'linux': ('fab fa-linux', 'text-yellow-600'),
    'nginx': ('fas fa-server', 'text-green-500'),
    'git': ('fab fa-git-alt', 'text-orange-600'),
    'webpack': ('fas fa-box', 'text-blue-400'),
}

TECH_NAMES = {
    'python': 'Python',
    'django': 'Django',
    'java': 'Java',
    'spring': 'Spring',
    'go': 'Go',
    'rust': 'Rust',
    'nodejs': 'Node.js',
    'react': 'React',
    'vue': 'Vue',
    'angular': 'Angular',
    'typescript': 'TypeScript',
    'javascript': 'JavaScript',
    'html5': 'HTML5',
    'css3': 'CSS3',
    'tailwind': 'Tailwind CSS',
    'bootstrap': 'Bootstrap',
    'mysql': 'MySQL',
    'postgresql': 'PostgreSQL',
    'mongodb': 'MongoDB',
    'redis': 'Redis',
    'elasticsearch': 'Elasticsearch',
    'docker': 'Docker',
    'kubernetes': 'Kubernetes',
    'aws': 'AWS',
    'linux': 'Linux',
    'nginx': 'Nginx',
    'git': 'Git',
    'webpack': 'Webpack',
}


def site_config(request):
    """全局站点配置上下文处理器"""
    try:
        config = SiteConfig.objects.first()
        if not config:
            config = SiteConfig.objects.create()
    except:
        config = None
    
    # 获取技术栈列表
    tech_stack = []
    if config:
        for i in range(1, 9):
            tech_key = getattr(config, f'tech_{i}', '')
            if tech_key:
                icon, color = TECH_ICONS.get(tech_key, ('fas fa-code', 'text-gray-500'))
                name = TECH_NAMES.get(tech_key, tech_key)
                tech_stack.append({
                    'key': tech_key,
                    'name': name,
                    'icon': icon,
                    'color': color,
                })
    
    return {
        'site_config': config,
        'tech_stack': tech_stack,
    }
