// Simple API helper (vanilla JS). Edit BASE_URL to match your backend.
const BASE_URL = ''; // e.g. 'https://api.example.com'

const api = {
  _headers(){
    const token = localStorage.getItem('access_token');
    const h = {'Content-Type':'application/json'};
    if(token) h['Authorization'] = 'Bearer ' + token;
    return h;
  },
  async request(path, opts={}){
    const url = (BASE_URL||'') + path;
    const res = await fetch(url, Object.assign({headers:this._headers()}, opts));
    if(res.ok){
      if(res.status===204) return null;
      try{ return await res.json(); }catch(e){ return null; }
    }
    let errText = 'خطا';
    try{ const e = await res.json(); errText = e.detail || e.message || JSON.stringify(e); }catch(e){}
    throw new Error(errText || ('HTTP ' + res.status));
  },

  // auth
  login(body){ return this.request('/api/v1/auth/auth/login', {method:'POST', body: JSON.stringify(body)}); },
  refresh(refresh_token){ return this.request(`/api/v1/auth/auth/refresh?refresh_token=${encodeURIComponent(refresh_token)}`, {method:'POST'}); },

  // users
  getCurrentUser(){ return this.request('/api/v1/users/users/me'); },

  // patients
  getPatients(skip=0, limit=100){ return this.request(`/api/v1/patients/patients/?skip=${skip}&limit=${limit}`); },
  createPatient(body){ return this.request('/api/v1/patients/patients/', {method:'POST', body: JSON.stringify(body)}); },
  getPatient(id){ return this.request(`/api/v1/patients/patients/${id}`); },
  updatePatient(id, body){ return this.request(`/api/v1/patients/patients/${id}`, {method:'PUT', body: JSON.stringify(body)}); },
  deletePatient(id){ return this.request(`/api/v1/patients/patients/${id}`, {method:'DELETE'}); },

  // appointments
  getAppointments(skip=0, limit=100){ return this.request(`/api/v1/appointments/appointments/?skip=${skip}&limit=${limit}`); },
  getMyAppointments(skip=0, limit=100){ return this.request(`/api/v1/appointments/appointments/my?skip=${skip}&limit=${limit}`); },
  createAppointment(body){ return this.request('/api/v1/appointments/appointments/', {method:'POST', body: JSON.stringify(body)}); },
  updateAppointment(id, body){ return this.request(`/api/v1/appointments/appointments/${id}`, {method:'PUT', body: JSON.stringify(body)}); },
  deleteAppointment(id){ return this.request(`/api/v1/appointments/appointments/${id}`, {method:'DELETE'}); },

  // medications
  getMedications(skip=0, limit=100, search=''){ return this.request(`/api/v1/medications/medications/?skip=${skip}&limit=${limit}${search?('&search='+encodeURIComponent(search)) : ''}`); },
  createMedication(body){ return this.request('/api/v1/medications/medications/', {method:'POST', body: JSON.stringify(body)}); },
  getMedication(id){ return this.request(`/api/v1/medications/medications/${id}`); },
  updateMedication(id, body){ return this.request(`/api/v1/medications/medications/${id}`, {method:'PUT', body: JSON.stringify(body)}); },
  deleteMedication(id){ return this.request(`/api/v1/medications/medications/${id}`, {method:'DELETE'}); },

  // prescriptions
  getPrescriptions(skip=0, limit=100){ return this.request(`/api/v1/prescriptions/prescriptions/?skip=${skip}&limit=${limit}`); },
  getMyPrescriptions(skip=0, limit=100){ return this.request(`/api/v1/prescriptions/prescriptions/my?skip=${skip}&limit=${limit}`); },
  createPrescription(body){ return this.request('/api/v1/prescriptions/prescriptions/', {method:'POST', body: JSON.stringify(body)}); },

  // factors
  getFactors(skip=0, limit=100){ return this.request(`/api/v1/factors/factors/?skip=${skip}&limit=${limit}`); },

  // insurances
  getInsurances(skip=0, limit=100){ return this.request(`/api/v1/insurances/insurances/?skip=${skip}&limit=${limit}`); },

  // settings
  getSettings(){ return this.request('/api/v1/settings/settings/'); },
  updateSettings(body){ return this.request('/api/v1/settings/settings/', {method:'PUT', body: JSON.stringify(body)}); },
};

// Automatic token refresh helper (very simple)
(async function tokenRefresher(){
  const refresh = localStorage.getItem('refresh_token');
  if(!refresh) return;
  try{
    const data = await api.refresh(refresh);
    if(data.access_token) localStorage.setItem('access_token', data.access_token);
  }catch(e){ console.info('token refresh failed'); }
})();
