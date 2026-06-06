import request from './request'

export const getTemplates = (params) => {
  return request.get('/templates', { params })
}

export const getTemplate = (id) => {
  return request.get(`/templates/${id}`)
}

export const createTemplate = (data) => {
  return request.post('/templates', data)
}

export const updateTemplate = (id, data) => {
  return request.put(`/templates/${id}`, data)
}

export const deleteTemplate = (id) => {
  return request.delete(`/templates/${id}`)
}
