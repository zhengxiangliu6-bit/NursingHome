import uuid
from django.db import models


class BaseModel(models.Model):
    """所有模型的基类，提供审计字段和软删除。"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
