from django.core.management.base import BaseCommand
from apps.accounts.models import Role, User
from apps.residents.models import CareLevel


class Command(BaseCommand):
    help = '初始化基础数据（角色、护理等级、管理员账号）'

    def handle(self, *args, **options):
        # 创建角色
        roles_data = [
            ('super_admin', '超级管理员'),
            ('admin', '管理员'),
            ('doctor', '医生'),
            ('nurse', '护士'),
            ('care_worker', '护工'),
            ('family_member', '家属'),
        ]
        for name, display in roles_data:
            Role.objects.get_or_create(name=name, defaults={'display_name': display})
        self.stdout.write(self.style.SUCCESS('角色数据初始化完成'))

        # 创建护理等级
        care_levels = [
            ('自理', 1, '生活完全自理，无需特殊护理', 80),
            ('半护', 2, '生活部分自理，需要协助', 150),
            ('全护', 3, '生活不能自理，需要全面护理', 250),
            ('特护', 4, '需要特殊医疗护理', 400),
        ]
        for name, level, desc, rate in care_levels:
            CareLevel.objects.get_or_create(
                level=level, defaults={'name': name, 'description': desc, 'daily_rate': rate}
            )
        self.stdout.write(self.style.SUCCESS('护理等级数据初始化完成'))

        # 创建超级管理员
        admin_role = Role.objects.get(name='super_admin')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123456',
                phone='13800000000',
                role=admin_role,
                first_name='系统',
                last_name='管理员',
            )
            self.stdout.write(self.style.SUCCESS('管理员账号创建完成: admin / admin123456'))
        else:
            self.stdout.write(self.style.WARNING('管理员账号已存在'))
