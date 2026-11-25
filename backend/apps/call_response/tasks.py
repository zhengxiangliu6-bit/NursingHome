from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, max_retries=0)
def check_call_escalation(self, call_record_id):
    """
    Celery延迟任务：检查呼叫是否仍pending，若是则升级到下一级。
    每次升级后自动调度下一轮超时检查。
    """
    from .models import CallRecord, EscalationRule, CallEscalation
    from .broadcast import broadcast_call_event

    try:
        call = CallRecord.objects.select_related(
            'caller_resident', 'call_device'
        ).get(id=call_record_id, is_deleted=False)
    except CallRecord.DoesNotExist:
        return

    # 仅在仍然pending时升级
    if call.status != 'pending':
        return

    current_level = call.current_escalation_level

    # 查找下一级升级规则
    next_rule = EscalationRule.objects.filter(
        priority=call.priority,
        escalation_order=current_level + 1,
        is_deleted=False
    ).first()

    if not next_rule:
        # 已到最高级别，标记超时
        call.status = 'timeout'
        call.save(update_fields=['status', 'updated_at'])
        broadcast_call_event(
            'call_timeout',
            {
                'call_id': str(call.id),
                'call_number': call.call_number,
            },
            building_id=str(call.building_id) if call.building_id else None
        )
        return

    # 创建升级审计记录
    CallEscalation.objects.create(
        call_record=call,
        from_level=current_level,
        to_level=current_level + 1,
        target_role=next_rule.target_role,
        reason='timeout'
    )

    # 更新呼叫级别
    call.current_escalation_level = current_level + 1
    call.save(update_fields=['current_escalation_level', 'updated_at'])

    # 广播升级事件
    broadcast_call_event(
        'call_escalated',
        {
            'call_id': str(call.id),
            'call_number': call.call_number,
            'caller_name': call.caller_resident.name,
            'priority': call.priority,
            'from_level': current_level,
            'to_level': current_level + 1,
            'target_role': next_rule.target_role,
            'location_description': call.location_description,
            'escalated_at': timezone.now().isoformat(),
        },
        building_id=str(call.building_id) if call.building_id else None
    )

    # 调度下一轮超时检查
    result = check_call_escalation.apply_async(
        args=[str(call.id)],
        countdown=next_rule.timeout_seconds
    )
    call.escalation_task_id = result.id
    call.save(update_fields=['escalation_task_id'])


def schedule_initial_escalation(call):
    """新呼叫创建时调用，查找第一级规则并调度超时检查。"""
    from .models import EscalationRule

    first_rule = EscalationRule.objects.filter(
        priority=call.priority,
        escalation_order=0,
        is_deleted=False
    ).first()

    if not first_rule:
        return

    result = check_call_escalation.apply_async(
        args=[str(call.id)],
        countdown=first_rule.timeout_seconds
    )
    call.escalation_task_id = result.id
    call.save(update_fields=['escalation_task_id'])


def cancel_escalation_timer(call):
    """呼叫被接受/解决/取消时调用，取消待执行的Celery升级任务。"""
    if call.escalation_task_id:
        from config.celery import app as celery_app
        celery_app.control.revoke(call.escalation_task_id, terminate=False)
        call.escalation_task_id = ''
        call.save(update_fields=['escalation_task_id'])
