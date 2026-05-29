const db = globalThis.__B44_DB__ || { auth:{ isAuthenticated: async()=>false, me: async()=>null }, entities:new Proxy({}, { get:()=>({ filter:async()=>[], get:async()=>null, create:async()=>({}), update:async()=>({}), delete:async()=>({}) }) }), integrations:{ Core:{ UploadFile:async()=>({ file_url:'' }) } } };

import React, { createContext, useState, useContext, useEffect } from 'react';

import { appParams } from '@/lib/app-params';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);
  const [isLoadingPublicSettings, setIsLoadingPublicSettings] = useState(true);
  const [authError, setAuthError] = useState(null);

  useEffect(() => { init(); }, []);

  const init = async () => {
    try {
      const client = createAxiosClient({ baseURL: `/api/apps/public`, headers: { 'X-App-Id': appParams.appId }, token: appParams.token, interceptResponses: true });
      await client.get(`/prod/public-settings/by-id/${appParams.appId}`);
      setIsLoadingPublicSettings(false);
      if (appParams.token) {
        try {
          const u = await db.auth.me();
          setUser(u);
        } catch {}
      }
    } catch (e) {
      const reason = e?.data?.extra_data?.reason;
      if (reason) setAuthError({ type: reason, message: e.message });
      else setAuthError({ type: 'unknown', message: e?.message });
      setIsLoadingPublicSettings(false);
    }
    setIsLoadingAuth(false);
  };

  const navigateToLogin = () => db.auth.redirectToLogin(window.location.href);

  return (
    <AuthContext.Provider value={{ user, isLoadingAuth, isLoadingPublicSettings, authError, navigateToLogin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
