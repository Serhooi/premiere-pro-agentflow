// API клиент для видеоредактора
class VideoEditorAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL
  }

  // Проекты
  async getProjects() {
    const response = await fetch(`${this.baseURL}/api/editor/projects`)
    if (!response.ok) throw new Error('Failed to fetch projects')
    return response.json()
  }

  async getProject(projectId) {
    const response = await fetch(`${this.baseURL}/api/editor/projects/${projectId}`)
    if (!response.ok) throw new Error('Failed to fetch project')
    return response.json()
  }

  async createProject(name, description, videoFile) {
    const formData = new FormData()
    formData.append('name', name)
    formData.append('description', description)
    formData.append('video_file', videoFile)

    const response = await fetch(`${this.baseURL}/api/editor/projects`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) throw new Error('Failed to create project')
    return response.json()
  }

  async updateProject(projectId, updates) {
    const response = await fetch(`${this.baseURL}/api/editor/projects/${projectId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updates)
    })
    
    if (!response.ok) throw new Error('Failed to update project')
    return response.json()
  }

  async deleteProject(projectId) {
    const response = await fetch(`${this.baseURL}/api/editor/projects/${projectId}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) throw new Error('Failed to delete project')
    return response.json()
  }

  // Waveform
  async getWaveform(projectId) {
    const response = await fetch(`${this.baseURL}/api/editor/projects/${projectId}/waveform`)
    if (!response.ok) throw new Error('Failed to fetch waveform')
    return response.json()
  }

  // Рендеринг
  async startRender(projectId, settings) {
    const response = await fetch(`${this.baseURL}/api/editor/projects/${projectId}/render`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings)
    })
    
    if (!response.ok) throw new Error('Failed to start render')
    return response.json()
  }

  async getRenderStatus(renderId) {
    const response = await fetch(`${this.baseURL}/api/editor/renders/${renderId}/status`)
    if (!response.ok) throw new Error('Failed to fetch render status')
    return response.json()
  }

  async getProjectRenders(projectId) {
    const response = await fetch(`${this.baseURL}/api/editor/projects/${projectId}/renders`)
    if (!response.ok) throw new Error('Failed to fetch project renders')
    return response.json()
  }

  // WebSocket для real-time
  connectWebSocket(projectId, onMessage) {
    const wsURL = this.baseURL.replace('http', 'ws')
    const ws = new WebSocket(`${wsURL}/api/editor/ws/${projectId}`)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    return ws
  }

  // Утилиты
  getVideoURL(filename) {
    return `${this.baseURL}/api/editor/videos/${filename}`
  }

  getWaveformURL(filename) {
    return `${this.baseURL}/api/editor/waveforms/${filename}`
  }

  getRenderURL(filename) {
    return `${this.baseURL}/api/editor/renders/${filename}`
  }

  getProxyURL(filename) {
    return `${this.baseURL}/api/editor/proxies/${filename}`
  }
}

export default VideoEditorAPI

