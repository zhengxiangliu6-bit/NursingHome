import { ElNotification } from 'element-plus'

/**
 * 字段名中文映射（DRF field name → 中文）
 */
const FIELD_LABELS = {
  username: '用户名',
  password: '密码',
  phone: '手机号',
  email: '邮箱',
  first_name: '名',
  last_name: '姓',
  employee_id: '工号',
  role: '角色',
  department: '部门',
  name: '姓名',
  gender: '性别',
  birth_date: '出生日期',
  id_card: '身份证号',
  admission_date: '入住日期',
  care_level: '护理等级',
  bed: '床位',
  primary_nurse: '责任护士',
  room_number: '房间号',
  building: '楼栋',
  floor: '楼层',
  room_type: '房间类型',
  capacity: '容量',
  bed_number: '床位号',
  status: '状态',
  stage: '阶段',
  staff: '员工',
  date: '日期',
  shift: '班次',
  user: '用户',
  relationship: '关系',
  title: '职称',
  certification: '资质证书',
  daily_rate: '日费率',
  reserved_bed: '预留床位',
  start_date: '开始日期',
  expected_return_date: '预计返回日期',
  actual_return_date: '实际返回日期',
  reason: '原因',
  resident_a: '老人A',
  resident_b: '老人B',
  reject_reason: '拒绝原因',
  non_field_errors: '',
  __all__: '',
}

/**
 * 解析 DRF 错误响应并返回可读字符串
 * @param {Error} error - axios 错误对象
 * @param {string} fallback - 默认提示
 * @returns {string}
 */
export function parseAPIError(error, fallback = '操作失败') {
  const data = error?.response?.data
  if (!data) return fallback

  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  const lines = []
  for (const [field, errors] of Object.entries(data)) {
    const msgs = Array.isArray(errors) ? errors : [String(errors)]
    const label = FIELD_LABELS[field]
    if (label === '') {
      // non_field_errors / __all__
      lines.push(...msgs)
    } else if (label) {
      lines.push(`${label}：${msgs.join('；')}`)
    } else {
      lines.push(`${field}：${msgs.join('；')}`)
    }
  }

  return lines.length ? lines.join('\n') : fallback
}

/**
 * 显示 API 错误通知
 * @param {Error} error - axios 错误对象
 * @param {string} title - 通知标题
 * @param {string} fallback - 默认提示
 */
export function showAPIError(error, title = '保存失败', fallback = '操作失败') {
  const message = parseAPIError(error, fallback)
  ElNotification({
    type: 'error',
    title,
    message: message.replace(/\n/g, '<br/>'),
    dangerouslyUseHTMLString: true,
    duration: 5000,
  })
}
