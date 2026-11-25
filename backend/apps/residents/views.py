from collections import defaultdict
from django.db import models, transaction
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsNurseOrAbove, IsAdmin, IsStaff
from .models import Resident, CareLevel, CareAssessment, Room, Bed, AdmissionApplication, ResidentLeave, BedTransfer
from .serializers import (
    ResidentSerializer, ResidentListSerializer,
    CareLevelSerializer, CareAssessmentSerializer,
    RoomSerializer, BedSerializer, AdmissionApplicationSerializer,
    ResidentLeaveSerializer, BedTransferSerializer,
)


class ResidentViewSet(viewsets.ModelViewSet):
    """老人管理。"""
    queryset = Resident.objects.select_related('care_level', 'bed__room', 'primary_nurse').filter(is_deleted=False)
    permission_classes = [IsNurseOrAbove]
    filterset_fields = ['status', 'care_level', 'gender']
    search_fields = ['name', 'id_card', 'phone']
    ordering_fields = ['name', 'admission_date', 'birth_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ResidentListSerializer
        return ResidentSerializer

    def _sync_bed_status(self, old_bed_id, new_bed_id):
        """当老人床位变更时，同步更新新旧床位的状态。"""
        if old_bed_id == new_bed_id:
            return
        # 释放旧床位
        if old_bed_id:
            Bed.objects.filter(id=old_bed_id, is_deleted=False).update(status='available')
        # 占用新床位
        if new_bed_id:
            Bed.objects.filter(id=new_bed_id, is_deleted=False).update(status='occupied')

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.bed_id:
            Bed.objects.filter(id=instance.bed_id, is_deleted=False).update(status='occupied')

    def perform_update(self, serializer):
        old_bed_id = serializer.instance.bed_id
        instance = serializer.save()
        self._sync_bed_status(old_bed_id, instance.bed_id)

    def perform_destroy(self, instance):
        """仅允许删除已退住的老人（软删除）。"""
        if instance.status != 'discharged':
            raise serializers.ValidationError({'detail': '仅可删除已退住的老人记录'})
        instance.is_deleted = True
        instance.save()

    @action(detail=True, methods=['get'])
    def assessments(self, request, pk=None):
        resident = self.get_object()
        assessments = CareAssessment.objects.filter(
            resident=resident, is_deleted=False
        ).select_related('assessor', 'recommended_level')
        serializer = CareAssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def discharge(self, request, pk=None):
        """办理退住：释放床位、更新状态。"""
        resident = self.get_object()
        if resident.status == 'discharged':
            return Response({'detail': '该老人已退住'}, status=status.HTTP_400_BAD_REQUEST)

        discharge_date = request.data.get('discharge_date') or str(timezone.now().date())
        reason = request.data.get('reason', '')

        # 记录最后床位信息，释放床位 → 清洁中
        if resident.bed:
            resident.last_bed_info = str(resident.bed)
            Bed.objects.filter(id=resident.bed_id, is_deleted=False).update(status='cleaning')

        resident.status = 'discharged'
        resident.discharge_date = discharge_date
        resident.bed = None
        if reason:
            resident.notes = f'{resident.notes}\n退住原因：{reason}'.strip()
        resident.save()
        return Response(ResidentSerializer(resident).data)

    @action(detail=True, methods=['post'], url_path='start_leave')
    def start_leave(self, request, pk=None):
        """办理请假：床位标记为请假，保留床位关系。"""
        resident = self.get_object()
        if resident.status != 'active':
            return Response({'detail': '仅在住老人可以请假'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否已有进行中的请假
        if ResidentLeave.objects.filter(resident=resident, status='on_leave', is_deleted=False).exists():
            return Response({'detail': '该老人已有进行中的请假记录'}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.data.get('start_date') or str(timezone.now().date())
        expected_return_date = request.data.get('expected_return_date')
        reason = request.data.get('reason', '')

        leave = ResidentLeave.objects.create(
            resident=resident,
            start_date=start_date,
            expected_return_date=expected_return_date,
            reason=reason,
            handler=request.user,
        )

        # 床位标记为请假（保留关系，不清空 bed）
        if resident.bed_id:
            Bed.objects.filter(id=resident.bed_id, is_deleted=False).update(status='leave')

        return Response(ResidentLeaveSerializer(leave).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='end_leave')
    def end_leave(self, request, pk=None):
        """销假：恢复床位为已占用。"""
        resident = self.get_object()
        leave = ResidentLeave.objects.filter(
            resident=resident, status='on_leave', is_deleted=False
        ).first()

        if not leave:
            return Response({'detail': '没有进行中的请假记录'}, status=status.HTTP_400_BAD_REQUEST)

        actual_return_date = request.data.get('actual_return_date') or str(timezone.now().date())
        leave.actual_return_date = actual_return_date
        leave.status = 'returned'
        leave.save()

        # 恢复床位状态
        if resident.bed_id:
            Bed.objects.filter(id=resident.bed_id, is_deleted=False).update(status='occupied')

        return Response(ResidentLeaveSerializer(leave).data)

    @action(detail=True, methods=['get'])
    def leaves(self, request, pk=None):
        """获取老人的请假记录列表。"""
        resident = self.get_object()
        leaves = ResidentLeave.objects.filter(
            resident=resident, is_deleted=False
        ).select_related('handler')
        serializer = ResidentLeaveSerializer(leaves, many=True)
        return Response(serializer.data)


class ResidentLeaveViewSet(viewsets.ReadOnlyModelViewSet):
    """请假记录查询（只读）。"""
    queryset = ResidentLeave.objects.select_related('resident', 'handler').filter(is_deleted=False)
    serializer_class = ResidentLeaveSerializer
    permission_classes = [IsNurseOrAbove]
    filterset_fields = ['resident', 'status']
    search_fields = ['resident__name']


class CareLevelViewSet(viewsets.ModelViewSet):
    queryset = CareLevel.objects.filter(is_deleted=False)
    serializer_class = CareLevelSerializer
    permission_classes = [IsStaff]


class CareAssessmentViewSet(viewsets.ModelViewSet):
    queryset = CareAssessment.objects.select_related(
        'resident', 'assessor', 'recommended_level'
    ).filter(is_deleted=False)
    serializer_class = CareAssessmentSerializer
    permission_classes = [IsNurseOrAbove]
    filterset_fields = ['resident', 'status']

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        assessment = self.get_object()
        assessment.status = 'approved'
        assessment.save()
        # 同时更新老人的护理等级
        if assessment.recommended_level:
            assessment.resident.care_level = assessment.recommended_level
            assessment.resident.save()
        return Response(CareAssessmentSerializer(assessment).data)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('building').prefetch_related('beds').filter(is_deleted=False)
    serializer_class = RoomSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['building', 'floor', 'room_type']


class BedViewSet(viewsets.ModelViewSet):
    queryset = Bed.objects.select_related('room').filter(is_deleted=False)
    serializer_class = BedSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['room', 'status']

    @action(detail=False, methods=['get'], url_path='map', permission_classes=[IsStaff])
    def map(self, request):
        """返回按楼栋/楼层/房间组织的床位状态图数据。"""
        beds = Bed.objects.select_related(
            'room__building', 'resident'
        ).filter(is_deleted=False, room__is_deleted=False)

        # 按楼栋 → 楼层 → 房间组织
        buildings_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        building_info = {}
        room_info = {}

        for bed in beds:
            room = bed.room
            building = room.building
            building_info[str(building.id)] = {'id': str(building.id), 'name': building.name}
            room_key = str(room.id)
            if room_key not in room_info:
                room_info[room_key] = {
                    'room_id': str(room.id),
                    'room_number': room.room_number,
                    'room_type': room.room_type,
                    'beds': [],
                }
            resident = getattr(bed, 'resident', None)
            room_info[room_key]['beds'].append({
                'bed_id': str(bed.id),
                'bed_number': bed.bed_number,
                'status': bed.status,
                'resident_name': resident.name if resident else None,
                'resident_id': str(resident.id) if resident else None,
            })
            buildings_map[str(building.id)][room.floor][room_key] = True

        result = []
        for bid, floor_map in buildings_map.items():
            floors = []
            for floor_num in sorted(floor_map.keys()):
                rooms = [room_info[rid] for rid in floor_map[floor_num]]
                rooms.sort(key=lambda r: r['room_number'])
                floors.append({'floor': floor_num, 'rooms': rooms})
            result.append({**building_info[bid], 'floors': floors})

        return Response(result)


class AdmissionApplicationViewSet(viewsets.ModelViewSet):
    """入住申请管理。"""
    queryset = AdmissionApplication.objects.select_related(
        'handler', 'resident', 'reserved_bed__room'
    ).filter(is_deleted=False)
    serializer_class = AdmissionApplicationSerializer
    permission_classes = [IsNurseOrAbove]
    filterset_fields = ['stage', 'handler']
    search_fields = ['name', 'phone']
    ordering_fields = ['created_at', 'name']

    def _release_reserved_bed(self, app):
        """释放申请预留的床位。"""
        if app.reserved_bed_id:
            Bed.objects.filter(id=app.reserved_bed_id, status='reserved', is_deleted=False).update(status='available')

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.reserved_bed_id:
            Bed.objects.filter(id=instance.reserved_bed_id, is_deleted=False).update(status='reserved')

    def perform_update(self, serializer):
        old_bed_id = serializer.instance.reserved_bed_id
        instance = serializer.save()
        new_bed_id = instance.reserved_bed_id
        if old_bed_id != new_bed_id:
            if old_bed_id:
                Bed.objects.filter(id=old_bed_id, status='reserved', is_deleted=False).update(status='available')
            if new_bed_id:
                Bed.objects.filter(id=new_bed_id, is_deleted=False).update(status='reserved')

    def perform_destroy(self, instance):
        """软删除，释放预留床位。"""
        self._release_reserved_bed(instance)
        instance.is_deleted = True
        instance.save()

    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        """推进到下一阶段（consulting→assessing→contracting）。"""
        app = self.get_object()
        flow = AdmissionApplication.STAGE_FLOW
        if app.stage not in flow:
            return Response({'detail': '当前状态不可推进'}, status=status.HTTP_400_BAD_REQUEST)
        idx = flow.index(app.stage)
        if idx >= len(flow) - 2:
            return Response({'detail': '请使用入住确认操作'}, status=status.HTTP_400_BAD_REQUEST)
        app.stage = flow[idx + 1]
        app.save()
        return Response(AdmissionApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝申请。"""
        app = self.get_object()
        if app.stage in ('admitted', 'rejected', 'withdrawn'):
            return Response({'detail': '当前状态不可拒绝'}, status=status.HTTP_400_BAD_REQUEST)
        self._release_reserved_bed(app)
        app.stage = 'rejected'
        app.notes = request.data.get('reason', app.notes)
        app.reserved_bed = None
        app.save()
        return Response(AdmissionApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """撤销申请。"""
        app = self.get_object()
        if app.stage in ('admitted', 'rejected', 'withdrawn'):
            return Response({'detail': '当前状态不可撤销'}, status=status.HTTP_400_BAD_REQUEST)
        self._release_reserved_bed(app)
        app.stage = 'withdrawn'
        app.reserved_bed = None
        app.save()
        return Response(AdmissionApplicationSerializer(app).data)

    @action(detail=True, methods=['post'])
    def admit(self, request, pk=None):
        """确认入住：从签约阶段创建老人记录，可同时分配床位/护理等级/责任护士。"""
        app = self.get_object()
        if app.stage != 'contracting':
            return Response({'detail': '仅签约阶段可办理入住'}, status=status.HTTP_400_BAD_REQUEST)
        if app.resident:
            return Response({'detail': '已办理入住'}, status=status.HTTP_400_BAD_REQUEST)

        admission_date = request.data.get('admission_date') or str(timezone.now().date())
        id_card = request.data.get('id_card', '').strip()
        if not id_card:
            return Response({'detail': '请填写身份证号'}, status=status.HTTP_400_BAD_REQUEST)
        if Resident.objects.filter(id_card=id_card, is_deleted=False).exists():
            return Response({'detail': '该身份证号已存在'}, status=status.HTTP_400_BAD_REQUEST)

        bed_id = request.data.get('bed_id') or (str(app.reserved_bed_id) if app.reserved_bed_id else None)
        care_level_id = request.data.get('care_level_id')
        primary_nurse_id = request.data.get('primary_nurse_id')

        create_kwargs = dict(
            name=app.name,
            gender=app.gender,
            birth_date=app.birth_date,
            id_card=id_card,
            phone=app.phone,
            emergency_contact_name=app.emergency_contact_name,
            emergency_contact_phone=app.emergency_contact_phone,
            admission_date=admission_date,
            status='active',
        )

        bed = None
        if bed_id:
            try:
                bed = Bed.objects.get(id=bed_id, is_deleted=False)
                create_kwargs['bed'] = bed
            except Bed.DoesNotExist:
                pass

        if care_level_id:
            create_kwargs['care_level_id'] = care_level_id

        if primary_nurse_id:
            create_kwargs['primary_nurse_id'] = primary_nurse_id

        resident = Resident.objects.create(**create_kwargs)

        if bed:
            bed.status = 'occupied'
            bed.save()

        app.stage = 'admitted'
        app.resident = resident
        app.reserved_bed = None
        app.save()
        return Response(AdmissionApplicationSerializer(app).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def discharge(self, request, pk=None):
        """从入住流程页面办理退住。"""
        app = self.get_object()
        if app.stage != 'admitted' or not app.resident:
            return Response({'detail': '仅已入住的申请可办理退住'}, status=status.HTTP_400_BAD_REQUEST)
        resident = app.resident
        if resident.status == 'discharged':
            return Response({'detail': '该老人已退住'}, status=status.HTTP_400_BAD_REQUEST)

        discharge_date = request.data.get('discharge_date') or str(timezone.now().date())
        reason = request.data.get('reason', '')

        if resident.bed:
            resident.last_bed_info = str(resident.bed)
            Bed.objects.filter(id=resident.bed_id, is_deleted=False).update(status='cleaning')

        resident.status = 'discharged'
        resident.discharge_date = discharge_date
        resident.bed = None
        if reason:
            resident.notes = f'{resident.notes}\n退住原因：{reason}'.strip()
        resident.save()
        return Response(AdmissionApplicationSerializer(app).data)


class BedTransferViewSet(viewsets.ModelViewSet):
    """床位调换申请管理。支持换到空床和两人互换。"""
    queryset = BedTransfer.objects.select_related(
        'resident_a', 'resident_b', 'bed_a__room', 'target_bed__room',
        'applicant', 'reviewer',
    ).filter(is_deleted=False)
    serializer_class = BedTransferSerializer
    permission_classes = [IsNurseOrAbove]
    filterset_fields = ['status']
    search_fields = ['resident_a__name', 'resident_b__name']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        ra = serializer.validated_data['resident_a']
        target_bed = serializer.validated_data['target_bed']

        if ra.status != 'active':
            raise serializers.ValidationError({'detail': '老人必须为在住状态'})
        if not ra.bed_id:
            raise serializers.ValidationError({'detail': '老人必须有当前床位'})
        if ra.bed_id == target_bed.id:
            raise serializers.ValidationError({'detail': '目标床位与当前床位相同'})

        # 检查是否有进行中的调换申请
        pending = BedTransfer.objects.filter(
            status='pending', is_deleted=False
        ).filter(
            models.Q(resident_a=ra) | models.Q(resident_b=ra)
        )
        if pending.exists():
            raise serializers.ValidationError({'detail': '该老人已有待审批的调换申请'})

        # 判断目标床位是否有人（互换）
        save_kwargs = dict(
            bed_a=ra.bed,
            applicant=self.request.user,
        )
        target_resident = Resident.objects.filter(
            bed=target_bed, status='active', is_deleted=False
        ).first()
        if target_resident:
            # 互换：目标床位有人
            save_kwargs['resident_b'] = target_resident
            # 也检查对方是否有待审批申请
            pending_b = BedTransfer.objects.filter(
                status='pending', is_deleted=False
            ).filter(
                models.Q(resident_a=target_resident) | models.Q(resident_b=target_resident)
            )
            if pending_b.exists():
                raise serializers.ValidationError({'detail': '对方老人已有待审批的调换申请'})
        elif target_bed.status != 'available':
            raise serializers.ValidationError({'detail': '目标床位不可用'})

        serializer.save(**save_kwargs)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批通过并自动执行床位调换。"""
        transfer = self.get_object()
        if transfer.status != 'pending':
            return Response({'detail': '仅待审批的申请可以通过'}, status=status.HTTP_400_BAD_REQUEST)

        ra = transfer.resident_a
        if ra.status != 'active':
            return Response({'detail': '老人状态已变更，无法执行调换'}, status=status.HTTP_400_BAD_REQUEST)
        if ra.bed_id != transfer.bed_a_id:
            return Response({'detail': '老人床位已变更，无法执行调换'}, status=status.HTTP_400_BAD_REQUEST)

        target_bed = transfer.target_bed
        rb = transfer.resident_b

        with transaction.atomic():
            if rb:
                # 互换：校验对方状态
                if rb.status != 'active' or rb.bed_id != target_bed.id:
                    return Response({'detail': '对方老人状态或床位已变更'}, status=status.HTTP_400_BAD_REQUEST)
                # 1. 临时清空 A 的床位（绕过 OneToOne 唯一约束）
                Resident.objects.filter(id=ra.id).update(bed=None)
                # 2. B 移到 A 的原床位
                Resident.objects.filter(id=rb.id).update(bed=transfer.bed_a_id)
                # 3. A 移到目标床位
                Resident.objects.filter(id=ra.id).update(bed=target_bed.id)
                # 两个床位状态保持 occupied
            else:
                # 换到空床位
                if target_bed.status != 'available':
                    return Response({'detail': '目标床位已不可用'}, status=status.HTTP_400_BAD_REQUEST)
                old_bed = transfer.bed_a
                Resident.objects.filter(id=ra.id).update(bed=target_bed.id)
                Bed.objects.filter(id=old_bed.id).update(status='available')
                Bed.objects.filter(id=target_bed.id).update(status='occupied')

        transfer.status = 'approved'
        transfer.reviewer = request.user
        transfer.reviewed_at = timezone.now()
        transfer.save()
        return Response(BedTransferSerializer(transfer).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝调换申请。"""
        transfer = self.get_object()
        if transfer.status != 'pending':
            return Response({'detail': '仅待审批的申请可以拒绝'}, status=status.HTTP_400_BAD_REQUEST)
        transfer.status = 'rejected'
        transfer.reject_reason = request.data.get('reason', '')
        transfer.reviewer = request.user
        transfer.reviewed_at = timezone.now()
        transfer.save()
        return Response(BedTransferSerializer(transfer).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消调换申请。"""
        transfer = self.get_object()
        if transfer.status != 'pending':
            return Response({'detail': '仅待审批的申请可以取消'}, status=status.HTTP_400_BAD_REQUEST)
        transfer.status = 'cancelled'
        transfer.save()
        return Response(BedTransferSerializer(transfer).data)
