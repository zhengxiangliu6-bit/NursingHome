import request from './index'

export const getPatrolTasks = (params) => request.get('/patrol/tasks/', { params })
export const getPatrolTask = (id) => request.get(`/patrol/tasks/${id}/`)
export const createPatrolTask = (data) => request.post('/patrol/tasks/', data)
export const getTodayPatrols = () => request.get('/patrol/tasks/today/')
export const startPatrol = (id) => request.patch(`/patrol/tasks/${id}/start/`)
export const completePatrol = (id) => request.patch(`/patrol/tasks/${id}/complete/`)
export const scanCheckpoint = (taskId, data) => request.post(`/patrol/tasks/${taskId}/scan/`, data)
export const reportException = (taskId, data) => request.post(`/patrol/tasks/${taskId}/exception/`, data)
export const getPatrolStatistics = () => request.get('/patrol/tasks/statistics/')

export const getCheckpoints = (params) => request.get('/patrol/checkpoints/', { params })
export const createCheckpoint = (data) => request.post('/patrol/checkpoints/', data)
export const updateCheckpoint = (id, data) => request.put(`/patrol/checkpoints/${id}/`, data)

export const getPatrolRoutes = (params) => request.get('/patrol/routes/', { params })
export const createPatrolRoute = (data) => request.post('/patrol/routes/', data)
