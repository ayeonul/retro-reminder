import axios from 'axios'


const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || (
    process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8000/api' : '/api'
  ),
  timeout: 10000
})


export default apiClient
