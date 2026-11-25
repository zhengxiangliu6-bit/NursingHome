import request from './index'

export const getCalls = (params) => request.get('/calls/', { params })
export const getCall = (id) => request.get(`/calls/${id}/`)
export const createCall = (data) => request.post('/calls/', data)
export const getActiveCalls = () => request.get('/calls/active/')
export const acceptCall = (id) => request.patch(`/calls/${id}/accept/`)
export const resolveCall = (id, data) => request.patch(`/calls/${id}/resolve/`, data)
export const cancelCall = (id) => request.patch(`/calls/${id}/cancel/`)
export const getCallStatistics = () => request.get('/calls/statistics/')

export const escalateCall = (id) => request.post(`/calls/${id}/escalate/`)

export const getCallDevices = (params) => request.get('/call-devices/', { params })
export const createCallDevice = (data) => request.post('/call-devices/', data)
export const updateCallDevice = (id, data) => request.put(`/call-devices/${id}/`, data)

// 升级规则
export const getEscalationRules = (params) => request.get('/escalation-rules/', { params })
export const createEscalationRule = (data) => request.post('/escalation-rules/', data)
export const updateEscalationRule = (id, data) => request.put(`/escalation-rules/${id}/`, data)
export const deleteEscalationRule = (id) => request.delete(`/escalation-rules/${id}/`)
