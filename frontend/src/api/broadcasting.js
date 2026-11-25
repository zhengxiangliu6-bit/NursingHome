import request from './index'

export const getBroadcastTasks = (params) => request.get('/broadcast/tasks/', { params })
export const createBroadcastTask = (data) => request.post('/broadcast/tasks/', data)
export const startBroadcast = (id) => request.post(`/broadcast/tasks/${id}/start/`)
export const stopBroadcast = (id) => request.post(`/broadcast/tasks/${id}/stop/`)

export const getBroadcastZones = () => request.get('/broadcast/zones/')
export const createBroadcastZone = (data) => request.post('/broadcast/zones/', data)

export const getBroadcastDevices = (params) => request.get('/broadcast/devices/', { params })
export const getBroadcastSchedules = () => request.get('/broadcast/schedules/')
export const createBroadcastSchedule = (data) => request.post('/broadcast/schedules/', data)

export const getBroadcastLogs = (params) => request.get('/broadcast/logs/', { params })
