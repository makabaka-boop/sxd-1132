import request from './request'

export const uploadRecords = (formData) => {
  return request.post('/records/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getRecords = (params) => {
  return request.get('/records', { params })
}

export const getPatientScoreChanges = (patientId) => {
  return request.get(`/records/patient/${patientId}/score-changes`)
}

export const getBatchRecords = (batchId) => {
  return request.get(`/records/batch/${batchId}`)
}
