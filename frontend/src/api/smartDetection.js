import request from './index'

export const getVitals = (params) => request.get('/vitals/', { params })
export const getLatestVitals = (residentId) => request.get(`/vitals/latest/${residentId}/`)
export const getVitalTrends = (residentId, params) => request.get(`/vitals/trends/${residentId}/`, { params })

export const getFallAlerts = (params) => request.get('/fall-alerts/', { params })
export const getActiveFallAlerts = () => request.get('/fall-alerts/active/')
export const respondFallAlert = (id) => request.patch(`/fall-alerts/${id}/respond/`)
export const resolveFallAlert = (id, data) => request.patch(`/fall-alerts/${id}/resolve/`, data)

export const getHealthChecks = (params) => request.get('/health-checks/', { params })
export const createHealthCheck = (data) => request.post('/health-checks/', data)

export const getCurrentPosition = (residentId) => request.get(`/positions/current/${residentId}/`)
export const getPositions = (params) => request.get('/positions/', { params })

export const getDetectionDevices = (params) => request.get('/detection-devices/', { params })
