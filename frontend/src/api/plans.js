import request from './request'

export const getPlans = (params) => {
  return request.get('/plans', { params })
}

export const createPlan = (data) => {
  return request.post('/plans', data)
}

export const updatePlan = (id, data) => {
  return request.put(`/plans/${id}`, data)
}

export const deletePlan = (id) => {
  return request.delete(`/plans/${id}`)
}
