import request from './index'

export const getOverview = () => request.get('/dashboard/overview/')
export const getCallStats = (params) => request.get('/dashboard/call-stats/', { params })
export const getHealthStats = () => request.get('/dashboard/health-stats/')
export const getPatrolStats = () => request.get('/dashboard/patrol-stats/')
