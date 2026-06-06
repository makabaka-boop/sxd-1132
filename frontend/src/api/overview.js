import request from './request'

export const getPatientOverview = (patientId, params) => {
  return request.get(`/overview/patient/${patientId}`, { params })
}
