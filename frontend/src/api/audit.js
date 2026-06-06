import request from './request'

export const getBatchErrors = (batchId) => {
  return request.get(`/audit/errors/batch/${batchId}`)
}

export const getAuditLogs = (params) => {
  return request.get('/audit/audit-logs', { params })
}

export const getAlerts = (params) => {
  return request.get('/audit/alerts', { params })
}

export const markAlertRead = (id) => {
  return request.put(`/audit/alerts/${id}/read`)
}
