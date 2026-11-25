import request from './index'

export const getBuildings = () => request.get('/campus/buildings/')
export const createBuilding = (data) => request.post('/campus/buildings/', data)
export const updateBuilding = (id, data) => request.put(`/campus/buildings/${id}/`, data)

export const getAreas = (params) => request.get('/campus/areas/', { params })
export const createArea = (data) => request.post('/campus/areas/', data)

export const getDevices = (params) => request.get('/campus/devices/', { params })
export const getDevice = (id) => request.get(`/campus/devices/${id}/`)
export const createDevice = (data) => request.post('/campus/devices/', data)
export const updateDevice = (id, data) => request.put(`/campus/devices/${id}/`, data)
export const addMaintenance = (id, data) => request.post(`/campus/devices/${id}/maintenance/`, data)
export const getDeviceStatusSummary = () => request.get('/campus/devices/status-summary/')

export const getNotices = (params) => request.get('/campus/notices/', { params })
export const createNotice = (data) => request.post('/campus/notices/', data)
export const updateNotice = (id, data) => request.put(`/campus/notices/${id}/`, data)
export const publishNotice = (id) => request.patch(`/campus/notices/${id}/publish/`)
