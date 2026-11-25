import request from './index'

// 告警规则
export const getAlertRules = (params) => request.get('/alert-rules/', { params })
export const createAlertRule = (data) => request.post('/alert-rules/', data)
export const updateAlertRule = (id, data) => request.put(`/alert-rules/${id}/`, data)
export const deleteAlertRule = (id) => request.delete(`/alert-rules/${id}/`)
export const toggleAlertRule = (id) => request.post(`/alert-rules/${id}/toggle/`)

// 告警
export const getAlerts = (params) => request.get('/alerts/', { params })
export const getAlert = (id) => request.get(`/alerts/${id}/`)
export const getActiveAlerts = () => request.get('/alerts/active/')
export const getAlertStatistics = () => request.get('/alerts/statistics/')
export const assignAlert = (id, data) => request.post(`/alerts/${id}/assign/`, data)
export const startProcessAlert = (id) => request.post(`/alerts/${id}/start_process/`)
export const resolveAlert = (id, data) => request.post(`/alerts/${id}/resolve/`, data)
export const dismissAlert = (id, data) => request.post(`/alerts/${id}/dismiss/`, data)

// MQTT设备映射
export const getMQTTMappings = (params) => request.get('/mqtt-mappings/', { params })
export const createMQTTMapping = (data) => request.post('/mqtt-mappings/', data)
export const updateMQTTMapping = (id, data) => request.put(`/mqtt-mappings/${id}/`, data)
export const deleteMQTTMapping = (id) => request.delete(`/mqtt-mappings/${id}/`)
