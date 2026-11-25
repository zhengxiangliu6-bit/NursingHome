import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue'),
        meta: { title: '综合看板', icon: 'DataBoard' },
      },
      // 呼叫响应
      {
        path: 'call-response',
        name: 'CallCenter',
        component: () => import('@/views/call-response/CallCenter.vue'),
        meta: { title: '呼叫监控', icon: 'Phone' },
      },
      {
        path: 'call-response/history',
        name: 'CallHistory',
        component: () => import('@/views/call-response/CallHistory.vue'),
        meta: { title: '呼叫历史', icon: 'Document' },
      },
      {
        path: 'call-response/devices',
        name: 'CallDeviceManage',
        component: () => import('@/views/call-response/CallDeviceManage.vue'),
        meta: { title: '呼叫设备', icon: 'Monitor' },
      },
      // 智能检测
      {
        path: 'smart-detection/vitals',
        name: 'VitalMonitor',
        component: () => import('@/views/smart-detection/VitalMonitor.vue'),
        meta: { title: '体征监控', icon: 'FirstAidKit' },
      },
      {
        path: 'smart-detection/fall',
        name: 'FallAlerts',
        component: () => import('@/views/smart-detection/FallAlerts.vue'),
        meta: { title: '跌倒预警', icon: 'Warning' },
      },
      {
        path: 'smart-detection/health',
        name: 'HealthRecords',
        component: () => import('@/views/smart-detection/HealthRecords.vue'),
        meta: { title: '健康检查', icon: 'Memo' },
      },
      {
        path: 'smart-detection/position',
        name: 'PositionMap',
        component: () => import('@/views/smart-detection/PositionMap.vue'),
        meta: { title: '定位地图', icon: 'Location' },
      },
      {
        path: 'smart-detection/alert-center',
        name: 'AlertCenter',
        component: () => import('@/views/smart-detection/AlertCenter.vue'),
        meta: { title: '告警中心', icon: 'AlarmClock' },
      },
      {
        path: 'smart-detection/rules',
        name: 'AlertRuleConfig',
        component: () => import('@/views/smart-detection/AlertRuleConfig.vue'),
        meta: { title: '告警规则', icon: 'Setting' },
      },
      // 巡更管理
      {
        path: 'patrol/schedule',
        name: 'PatrolSchedule',
        component: () => import('@/views/patrol/PatrolSchedule.vue'),
        meta: { title: '巡更排班', icon: 'Calendar' },
      },
      {
        path: 'patrol/monitor',
        name: 'PatrolMonitor',
        component: () => import('@/views/patrol/PatrolMonitor.vue'),
        meta: { title: '实时巡更', icon: 'MapLocation' },
      },
      {
        path: 'patrol/checkpoints',
        name: 'CheckpointManage',
        component: () => import('@/views/patrol/CheckpointManage.vue'),
        meta: { title: '巡更点管理', icon: 'Place' },
      },
      {
        path: 'patrol/records',
        name: 'PatrolRecords',
        component: () => import('@/views/patrol/PatrolRecords.vue'),
        meta: { title: '巡更记录', icon: 'Tickets' },
      },
      // 公共广播
      {
        path: 'broadcasting/control',
        name: 'BroadcastControl',
        component: () => import('@/views/broadcasting/BroadcastControl.vue'),
        meta: { title: '广播控制', icon: 'Microphone' },
      },
      {
        path: 'broadcasting/schedule',
        name: 'BroadcastSchedule',
        component: () => import('@/views/broadcasting/BroadcastSchedule.vue'),
        meta: { title: '定时广播', icon: 'AlarmClock' },
      },
      {
        path: 'broadcasting/logs',
        name: 'BroadcastLog',
        component: () => import('@/views/broadcasting/BroadcastLog.vue'),
        meta: { title: '广播日志', icon: 'Notebook' },
      },
      // 院区管理
      {
        path: 'campus/devices',
        name: 'DeviceManage',
        component: () => import('@/views/campus/DeviceManage.vue'),
        meta: { title: '设备管理', icon: 'Cpu' },
      },
      {
        path: 'campus/buildings',
        name: 'BuildingManage',
        component: () => import('@/views/campus/BuildingManage.vue'),
        meta: { title: '楼栋管理', icon: 'OfficeBuilding' },
      },
      {
        path: 'campus/notices',
        name: 'NoticeManage',
        component: () => import('@/views/campus/NoticeManage.vue'),
        meta: { title: '信息发布', icon: 'Bell' },
      },
      {
        path: 'campus/assessment',
        name: 'Assessment',
        component: () => import('@/views/campus/Assessment.vue'),
        meta: { title: '护理评估', icon: 'Edit' },
      },
      // 老人管理
      {
        path: 'residents',
        name: 'ResidentList',
        component: () => import('@/views/residents/ResidentList.vue'),
        meta: { title: '老人列表', icon: 'User' },
      },
      {
        path: 'residents/rooms',
        name: 'RoomManage',
        component: () => import('@/views/residents/RoomManage.vue'),
        meta: { title: '房间管理', icon: 'House' },
      },
      {
        path: 'residents/bed-map',
        name: 'BedMap',
        component: () => import('@/views/residents/BedMap.vue'),
        meta: { title: '床位状态图', icon: 'Grid' },
      },
      {
        path: 'residents/admission',
        name: 'AdmissionProcess',
        component: () => import('@/views/residents/AdmissionProcess.vue'),
        meta: { title: '入住流程', icon: 'DocumentAdd' },
      },
      {
        path: 'residents/bed-transfer',
        name: 'BedTransfer',
        component: () => import('@/views/residents/BedTransfer.vue'),
        meta: { title: '床位调换', icon: 'Sort' },
      },
      {
        path: 'residents/:id',
        name: 'ResidentDetail',
        component: () => import('@/views/residents/ResidentDetail.vue'),
        meta: { title: '老人详情' },
      },
      // 员工管理
      {
        path: 'campus/staff',
        name: 'StaffManage',
        component: () => import('@/views/campus/StaffManage.vue'),
        meta: { title: '员工档案', icon: 'UserFilled' },
      },
      {
        path: 'campus/schedule',
        name: 'StaffSchedule',
        component: () => import('@/views/campus/StaffSchedule.vue'),
        meta: { title: '排班管理', icon: 'Calendar' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth !== false && !authStore.isLoggedIn) {
    next('/login')
    return
  }

  if (to.path === '/login' && authStore.isLoggedIn) {
    next('/')
    return
  }

  // 如果已登录但没有用户信息，获取一下
  if (authStore.isLoggedIn && !authStore.user) {
    await authStore.fetchUser()
  }

  next()
})

export default router
