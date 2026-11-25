// 呼叫优先级
export const CALL_PRIORITY = {
  emergency: { label: '紧急呼叫', color: '#F56C6C', type: 'danger' },
  normal: { label: '普通呼叫', color: '#E6A23C', type: 'warning' },
  consultation: { label: '咨询呼叫', color: '#409EFF', type: 'primary' },
}

// 呼叫状态
export const CALL_STATUS = {
  pending: { label: '待响应', color: '#F56C6C', type: 'danger' },
  accepted: { label: '已接受', color: '#E6A23C', type: 'warning' },
  in_progress: { label: '处理中', color: '#409EFF', type: 'primary' },
  resolved: { label: '已解决', color: '#67C23A', type: 'success' },
  cancelled: { label: '已取消', color: '#909399', type: 'info' },
  timeout: { label: '超时', color: '#F56C6C', type: 'danger' },
}

// 设备状态
export const DEVICE_STATUS = {
  online: { label: '在线', color: '#67C23A', type: 'success' },
  offline: { label: '离线', color: '#909399', type: 'info' },
  fault: { label: '故障', color: '#F56C6C', type: 'danger' },
  maintenance: { label: '维护中', color: '#E6A23C', type: 'warning' },
}

// 跌倒告警状态
export const FALL_ALERT_STATUS = {
  alerting: { label: '告警中', color: '#F56C6C', type: 'danger' },
  responding: { label: '响应中', color: '#E6A23C', type: 'warning' },
  resolved: { label: '已处理', color: '#67C23A', type: 'success' },
  dismissed: { label: '已忽略', color: '#909399', type: 'info' },
}

// 巡更任务状态
export const PATROL_STATUS = {
  scheduled: { label: '已排班', color: '#409EFF', type: 'primary' },
  in_progress: { label: '巡更中', color: '#E6A23C', type: 'warning' },
  completed: { label: '已完成', color: '#67C23A', type: 'success' },
  missed: { label: '未执行', color: '#F56C6C', type: 'danger' },
  abnormal: { label: '异常', color: '#F56C6C', type: 'danger' },
}

// 升级目标角色
export const ESCALATION_ROLES = {
  care_worker: { label: '护工', order: 0 },
  nurse: { label: '护士', order: 1 },
  admin: { label: '管理员', order: 2 },
  super_admin: { label: '超级管理员', order: 3 },
}

// 告警类型
export const ALERT_TYPE = {
  vital_abnormal: { label: '体征异常', color: '#F56C6C', icon: 'FirstAidKit' },
  fall: { label: '跌倒告警', color: '#F56C6C', icon: 'Warning' },
  sos: { label: 'SOS求助', color: '#F56C6C', icon: 'Bell' },
  bed_exit: { label: '离床告警', color: '#E6A23C', icon: 'Moon' },
  restricted_zone: { label: '越界告警', color: '#E6A23C', icon: 'Location' },
  device_offline: { label: '设备离线', color: '#909399', icon: 'SwitchButton' },
  battery_low: { label: '电量不足', color: '#E6A23C', icon: 'Lightning' },
}

// 告警级别
export const ALERT_SEVERITY = {
  critical: { label: '严重', color: '#F56C6C', type: 'danger' },
  warning: { label: '警告', color: '#E6A23C', type: 'warning' },
  info: { label: '提示', color: '#909399', type: 'info' },
}

// 告警状态
export const ALERT_STATUS = {
  pending: { label: '待处理', color: '#F56C6C', type: 'danger' },
  assigned: { label: '已指派', color: '#E6A23C', type: 'warning' },
  processing: { label: '处理中', color: '#409EFF', type: 'primary' },
  resolved: { label: '已解决', color: '#67C23A', type: 'success' },
  dismissed: { label: '已忽略', color: '#909399', type: 'info' },
  auto_resolved: { label: '自动解除', color: '#67C23A', type: 'success' },
}

// 告警规则指标
export const ALERT_METRICS = {
  heart_rate: { label: '心率', unit: 'bpm' },
  systolic_bp: { label: '收缩压', unit: 'mmHg' },
  diastolic_bp: { label: '舒张压', unit: 'mmHg' },
  blood_oxygen: { label: '血氧', unit: '%' },
  temperature: { label: '体温', unit: '°C' },
  respiratory_rate: { label: '呼吸频率', unit: '次/分' },
}

// 告警规则操作符
export const ALERT_OPERATORS = {
  gt: { label: '>', desc: '大于' },
  gte: { label: '>=', desc: '大于等于' },
  lt: { label: '<', desc: '小于' },
  lte: { label: '<=', desc: '小于等于' },
  eq: { label: '=', desc: '等于' },
  neq: { label: '!=', desc: '不等于' },
}

// 角色
export const ROLES = {
  super_admin: '超级管理员',
  admin: '管理员',
  doctor: '医生',
  nurse: '护士',
  care_worker: '护工',
  family_member: '家属',
}
