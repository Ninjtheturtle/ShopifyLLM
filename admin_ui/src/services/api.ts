import axios from 'axios'

// Configure axios with base URL and default settings
export const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for authentication (if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Redirect to login or refresh token
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// API service methods
export const experimentsAPI = {
  // Get list of experiments
  list: (params?: { page?: number; per_page?: number; status?: string }) => 
    api.get('/experiments', { params }),

  // Get single experiment
  get: (id: string) => 
    api.get(`/experiments/${id}`),

  // Create new experiment
  create: (data: any) => 
    api.post('/experiments', data),

  // Update experiment
  update: (id: string, data: any) => 
    api.put(`/experiments/${id}`, data),

  // Start experiment
  start: (id: string) => 
    api.post(`/experiments/${id}/start`),

  // Stop experiment
  stop: (id: string) => 
    api.post(`/experiments/${id}/stop`),

  // Get experiment results
  getResults: (id: string) => 
    api.get(`/experiments/${id}/results`),

  // Publish winner
  publishWinner: (id: string, variantId: string) => 
    api.post(`/experiments/${id}/publish-winner`, { variant_id: variantId }),

  // Delete experiment
  delete: (id: string) => 
    api.delete(`/experiments/${id}`)
}

export const variantsAPI = {
  // Create variant
  create: (data: any) => 
    api.post('/variants', data),

  // Get variant
  get: (id: string) => 
    api.get(`/variants/${id}`),

  // Update variant
  update: (id: string, data: any) => 
    api.put(`/variants/${id}`, data),

  // Delete variant
  delete: (id: string) => 
    api.delete(`/variants/${id}`),

  // List experiment variants
  listByExperiment: (experimentId: string) => 
    api.get(`/variants/experiment/${experimentId}`),

  // Generate variants
  generate: (data: any) => 
    api.post('/variants/generate', data),

  // Validate variant
  validate: (id: string) => 
    api.post(`/variants/${id}/validate`),

  // Duplicate variant
  duplicate: (id: string, data?: any) => 
    api.post(`/variants/${id}/duplicate`, data)
}

export const assignmentsAPI = {
  // Assign user to experiment
  assign: (userId: string, experimentId: string) => 
    api.post('/assignments/assign', { user_id: userId, experiment_id: experimentId }),

  // Bulk assign users
  bulkAssign: (userIds: string[], experimentId: string) => 
    api.post('/assignments/bulk-assign', { user_ids: userIds, experiment_id: experimentId }),

  // Get user assignments
  getUserAssignments: (userId: string) => 
    api.get(`/assignments/user/${userId}`),

  // Get assignment distribution
  getDistribution: (experimentId: string) => 
    api.get(`/assignments/experiment/${experimentId}/distribution`),

  // List experiment assignments
  listByExperiment: (experimentId: string, params?: { page?: number; per_page?: number; variant_id?: string }) => 
    api.get(`/assignments/experiment/${experimentId}`, { params }),

  // Remove assignment
  remove: (assignmentId: string) => 
    api.delete(`/assignments/${assignmentId}`),

  // Remove user from experiment
  removeUserFromExperiment: (userId: string, experimentId: string) => 
    api.delete(`/assignments/user/${userId}/experiment/${experimentId}`),

  // Validate experiment assignments
  validate: (experimentId: string) => 
    api.get(`/assignments/validate/${experimentId}`),

  // Get assignment stats
  getStats: (experimentId: string) => 
    api.get(`/assignments/stats/${experimentId}`)
}

export const eventsAPI = {
  // Track event
  track: (data: any) => 
    api.post('/events', data),

  // Track bulk events
  bulkTrack: (events: any[]) => 
    api.post('/events/bulk', { events }),

  // Get experiment events
  listByExperiment: (experimentId: string, params?: any) => 
    api.get(`/events/experiment/${experimentId}`, { params }),

  // Get user events
  getUserEvents: (userId: string, params?: { page?: number; per_page?: number }) => 
    api.get(`/events/user/${userId}`, { params }),

  // Get event stats
  getStats: (experimentId: string) => 
    api.get(`/events/stats/${experimentId}`),

  // Get single event
  get: (eventId: string) => 
    api.get(`/events/${eventId}`),

  // Delete event
  delete: (eventId: string) => 
    api.delete(`/events/${eventId}`)
}

export default api
