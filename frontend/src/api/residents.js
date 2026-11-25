import request from './index'

export const getResidents = (params) => request.get('/residents/', { params })
export const getResident = (id) => request.get(`/residents/${id}/`)
export const createResident = (data) => request.post('/residents/', data)
export const updateResident = (id, data) => request.put(`/residents/${id}/`, data)
export const deleteResident = (id) => request.delete(`/residents/${id}/`)
export const getResidentAssessments = (id) => request.get(`/residents/${id}/assessments/`)
export const dischargeResident = (id, data) => request.post(`/residents/${id}/discharge/`, data)

export const getCareLevels = () => request.get('/care-levels/')
export const getAssessments = (params) => request.get('/assessments/', { params })
export const createAssessment = (data) => request.post('/assessments/', data)
export const approveAssessment = (id) => request.patch(`/assessments/${id}/approve/`)

export const getRooms = (params) => request.get('/rooms/', { params })
export const createRoom = (data) => request.post('/rooms/', data)
export const updateRoom = (id, data) => request.put(`/rooms/${id}/`, data)

export const getBeds = (params) => request.get('/beds/', { params })
export const createBed = (data) => request.post('/beds/', data)
export const updateBed = (id, data) => request.patch(`/beds/${id}/`, data)
export const deleteBed = (id) => request.delete(`/beds/${id}/`)
export const getBedMap = () => request.get('/beds/map/')

export const deleteRoom = (id) => request.delete(`/rooms/${id}/`)

export const getAdmissionApplications = (params) => request.get('/admission-applications/', { params })
export const getAdmissionApplication = (id) => request.get(`/admission-applications/${id}/`)
export const createAdmissionApplication = (data) => request.post('/admission-applications/', data)
export const updateAdmissionApplication = (id, data) => request.put(`/admission-applications/${id}/`, data)
export const deleteAdmissionApplication = (id) => request.delete(`/admission-applications/${id}/`)
export const advanceApplicationStage = (id) => request.post(`/admission-applications/${id}/advance/`)
export const rejectApplication = (id, data) => request.post(`/admission-applications/${id}/reject/`, data)
export const withdrawApplication = (id) => request.post(`/admission-applications/${id}/withdraw/`)
export const admitApplication = (id, data) => request.post(`/admission-applications/${id}/admit/`, data)
export const dischargeApplication = (id, data) => request.post(`/admission-applications/${id}/discharge/`, data)

export const startLeave = (id, data) => request.post(`/residents/${id}/start_leave/`, data)
export const endLeave = (id, data) => request.post(`/residents/${id}/end_leave/`, data)
export const getResidentLeaves = (id) => request.get(`/residents/${id}/leaves/`)

export const getBedTransfers = (params) => request.get('/bed-transfers/', { params })
export const createBedTransfer = (data) => request.post('/bed-transfers/', data)
export const approveBedTransfer = (id) => request.post(`/bed-transfers/${id}/approve/`)
export const rejectBedTransfer = (id, data) => request.post(`/bed-transfers/${id}/reject/`, data)
export const cancelBedTransfer = (id) => request.post(`/bed-transfers/${id}/cancel/`)
export const deleteBedTransfer = (id) => request.delete(`/bed-transfers/${id}/`)

export const getAvailableBeds = () => request.get('/beds/', { params: { status: 'available' } })
export const getFamilyRelations = (params) => request.get('/auth/family-relations/', { params })
