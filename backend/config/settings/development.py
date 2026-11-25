from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 生产环境切换为 PostgreSQL 时使用以下配置:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'elderly_care'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# CORS - allow all in development
CORS_ALLOW_ALL_ORIGINS = True

# 开发环境使用内存 Channel Layer（无需 Redis）
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
