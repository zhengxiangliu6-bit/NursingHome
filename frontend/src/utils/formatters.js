import dayjs from 'dayjs'

export function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-'
}

export function formatDateTime(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

export function formatDuration(seconds) {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}时${m}分`
}

export function formatVitalStatus(value, type) {
  const ranges = {
    heart_rate: { low: 60, high: 100, unit: 'bpm' },
    systolic_bp: { low: 90, high: 140, unit: 'mmHg' },
    diastolic_bp: { low: 60, high: 90, unit: 'mmHg' },
    blood_oxygen: { low: 95, high: 100, unit: '%' },
    temperature: { low: 36.0, high: 37.3, unit: '°C' },
  }
  const range = ranges[type]
  if (!range || value == null) return 'normal'
  if (value < range.low || value > range.high) return 'abnormal'
  return 'normal'
}
