from django.db import models
from apps.common.models import BaseModel


class CareLevel(BaseModel):
    """护理等级定义。"""
    name = models.CharField('等级名称', max_length=50)  # 自理/半护/全护/特护
    level = models.IntegerField('等级数值', unique=True)  # 1-4
    description = models.TextField('描述')
    daily_rate = models.DecimalField('日费用', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = '护理等级'
        verbose_name_plural = verbose_name
        ordering = ['level']

    def __str__(self):
        return self.name


class Resident(BaseModel):
    """老人信息。"""
    GENDER_CHOICES = [('M', '男'), ('F', '女')]
    STATUS_CHOICES = [
        ('active', '在住'),
        ('discharged', '离院'),
        ('hospitalized', '住院中'),
        ('deceased', '已故'),
    ]

    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField('出生日期')
    id_card = models.CharField('身份证号', max_length=18, unique=True)
    photo = models.ImageField('照片', upload_to='residents/', null=True, blank=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    admission_date = models.DateField('入住日期')
    discharge_date = models.DateField('离院日期', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    bed = models.OneToOneField(
        'Bed', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='resident', verbose_name='床位'
    )
    care_level = models.ForeignKey(
        CareLevel, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='护理等级'
    )
    primary_nurse = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='primary_residents', verbose_name='责任护士'
    )
    medical_history = models.TextField('既往病史', blank=True)
    allergy_info = models.TextField('过敏信息', blank=True)
    emergency_contact_name = models.CharField('紧急联系人', max_length=50)
    emergency_contact_phone = models.CharField('紧急联系电话', max_length=20)
    last_bed_info = models.CharField('最后床位', max_length=50, blank=True)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '老人'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CareAssessment(BaseModel):
    """护理评估。"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已审核'),
    ]

    resident = models.ForeignKey(
        Resident, on_delete=models.CASCADE, related_name='assessments', verbose_name='老人'
    )
    assessor = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='评估人'
    )
    assessment_date = models.DateTimeField('评估日期')
    adl_score = models.IntegerField('日常生活能力评分')
    cognitive_score = models.IntegerField('认知能力评分')
    mobility_score = models.IntegerField('行动能力评分')
    overall_score = models.IntegerField('综合评分')
    recommended_level = models.ForeignKey(
        CareLevel, on_delete=models.SET_NULL, null=True, verbose_name='建议护理等级'
    )
    notes = models.TextField('评估备注', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')

    class Meta:
        verbose_name = '护理评估'
        verbose_name_plural = verbose_name
        ordering = ['-assessment_date']


class Room(BaseModel):
    """房间。"""
    ROOM_TYPE_CHOICES = [
        ('single', '单人间'),
        ('double', '双人间'),
        ('multi', '多人间'),
    ]

    room_number = models.CharField('房间号', max_length=20, unique=True)
    building = models.ForeignKey(
        'campus.Building', on_delete=models.CASCADE, related_name='rooms', verbose_name='所属楼栋'
    )
    floor = models.IntegerField('楼层')
    room_type = models.CharField('房间类型', max_length=20, choices=ROOM_TYPE_CHOICES)
    capacity = models.IntegerField('容纳人数', default=2)
    status = models.CharField('状态', max_length=20, default='available')

    class Meta:
        verbose_name = '房间'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.room_number


class Bed(BaseModel):
    """床位。"""
    STATUS_CHOICES = [
        ('available', '空闲'),
        ('occupied', '已占用'),
        ('leave', '请假'),
        ('reserved', '预留'),
        ('maintenance', '维护中'),
        ('cleaning', '清洁中'),
    ]

    bed_number = models.CharField('床位号', max_length=10)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds', verbose_name='所属房间')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='available')

    class Meta:
        verbose_name = '床位'
        verbose_name_plural = verbose_name
        unique_together = ['bed_number', 'room']

    def __str__(self):
        return f'{self.room.room_number}-{self.bed_number}'


class AdmissionApplication(BaseModel):
    """入住申请，跟踪咨询→评估→签约→入住的全生命周期。"""
    STAGE_CHOICES = [
        ('consulting', '咨询中'),
        ('assessing', '评估中'),
        ('contracting', '签约中'),
        ('admitted', '已完成'),
        ('rejected', '已拒绝'),
        ('withdrawn', '已撤销'),
    ]
    STAGE_FLOW = ['consulting', 'assessing', 'contracting', 'admitted']

    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=Resident.GENDER_CHOICES)
    birth_date = models.DateField('出生日期')
    phone = models.CharField('联系电话', max_length=20)
    emergency_contact_name = models.CharField('紧急联系人', max_length=50, blank=True)
    emergency_contact_phone = models.CharField('紧急联系电话', max_length=20, blank=True)
    inquiry_source = models.CharField('来源渠道', max_length=50, blank=True)
    notes = models.TextField('备注', blank=True)
    stage = models.CharField('当前阶段', max_length=20, choices=STAGE_CHOICES, default='consulting')
    handler = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='handled_applications', verbose_name='负责人'
    )
    expected_admission_date = models.DateField('预计入住日期', null=True, blank=True)
    contract_signed_at = models.DateTimeField('签约时间', null=True, blank=True)
    reserved_bed = models.ForeignKey(
        Bed, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='reserved_by_application', verbose_name='预留床位'
    )
    resident = models.OneToOneField(
        Resident, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='admission_application', verbose_name='关联老人'
    )

    class Meta:
        verbose_name = '入住申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_stage_display()})'


class ResidentLeave(BaseModel):
    """老人请假记录。"""
    STATUS_CHOICES = [
        ('on_leave', '请假中'),
        ('returned', '已销假'),
        ('cancelled', '已取消'),
    ]

    resident = models.ForeignKey(
        Resident, on_delete=models.CASCADE, related_name='leaves', verbose_name='老人'
    )
    start_date = models.DateField('开始日期')
    expected_return_date = models.DateField('预计返回日期', null=True, blank=True)
    actual_return_date = models.DateField('实际返回日期', null=True, blank=True)
    reason = models.TextField('请假原因', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='on_leave')
    handler = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='操作人'
    )

    class Meta:
        verbose_name = '请假记录'
        verbose_name_plural = verbose_name
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.resident.name} {self.start_date} ({self.get_status_display()})'


class BedTransfer(BaseModel):
    """床位调换申请。支持两种场景：老人换到空床位，或两个老人互换床位。"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
        ('cancelled', '已取消'),
    ]

    resident_a = models.ForeignKey(
        Resident, on_delete=models.CASCADE, related_name='transfers_as_a', verbose_name='申请老人'
    )
    bed_a = models.ForeignKey(
        Bed, on_delete=models.CASCADE, related_name='+', verbose_name='原床位'
    )
    target_bed = models.ForeignKey(
        Bed, on_delete=models.CASCADE, related_name='+', verbose_name='目标床位'
    )
    resident_b = models.ForeignKey(
        Resident, on_delete=models.CASCADE, null=True, blank=True,
        related_name='transfers_as_b', verbose_name='对方老人（互换时）'
    )
    reason = models.TextField('调换原因', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    applicant = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True,
        related_name='bed_transfer_applications', verbose_name='申请人'
    )
    reviewer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bed_transfer_reviews', verbose_name='审批人'
    )
    reviewed_at = models.DateTimeField('审批时间', null=True, blank=True)
    reject_reason = models.TextField('拒绝原因', blank=True)

    class Meta:
        verbose_name = '床位调换申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        if self.resident_b:
            return f'{self.resident_a.name} ↔ {self.resident_b.name} ({self.get_status_display()})'
        return f'{self.resident_a.name} → {self.target_bed} ({self.get_status_display()})'
