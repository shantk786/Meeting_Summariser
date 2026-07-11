import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000,
});

export async function uploadAudio(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function processMeeting(meetingId) {
  const response = await api.post(`/process/${meetingId}`);
  return response.data;
}

export async function fetchMeetings(query = '') {
  const response = await api.get('/meetings', {
    params: query ? { query } : {},
  });
  return response.data;
}

export async function fetchMeeting(meetingId) {
  const response = await api.get(`/meeting/${meetingId}`);
  return response.data;
}

export async function deleteMeeting(meetingId) {
  const response = await api.delete(`/meeting/${meetingId}`);
  return response.data;
}

export function getFileUrl(path) {
  if (!path) return '';
  return `${api.defaults.baseURL}${path.startsWith('/') ? path : `/${path}`}`;
}

export default api;
