const get = (key) => new URLSearchParams(window.location.search).get(key) || localStorage.getItem(`base44_${key}`) || import.meta.env[`VITE_BASE44_${key.toUpperCase()}`] || null;

export const appParams = {
  appId: get('app_id'),
  token: get('access_token'),
  functionsVersion: get('functions_version'),
  appBaseUrl: get('app_base_url'),
};