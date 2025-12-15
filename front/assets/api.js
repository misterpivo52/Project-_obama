const API = (() => {
  const overrideOrigin =
    (typeof window !== "undefined" && (window.API_ORIGIN || localStorage.getItem("api_origin"))) ||
    null;
  const ORIGIN = overrideOrigin || "http://127.0.0.1:8000";
  const BASE = {
    api: `${ORIGIN}/api`,
    auth: `${ORIGIN}/auth`
  };

  function getTokens(){
    return {
      access: localStorage.getItem("access_token"),
      refresh: localStorage.getItem("refresh_token"),
    };
  }

  function setTokens(tokens){
    if(tokens?.access) localStorage.setItem("access_token", tokens.access);
    if(tokens?.refresh) localStorage.setItem("refresh_token", tokens.refresh);
  }

  function getUser(){
    const raw = localStorage.getItem("user");
    if(!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }

  function setUser(user){
    if(user) localStorage.setItem("user", JSON.stringify(user));
  }

  async function rawFetch(url, opts = {}){
    const { access } = getTokens();
    const headers = new Headers(opts.headers || {});
    if(!headers.has("Content-Type") && opts.body) headers.set("Content-Type","application/json");
    if(access && !headers.has("Authorization")) headers.set("Authorization", `Bearer ${access}`);
    const res = await fetch(url, { ...opts, headers });
    return res;
  }

  async function refreshAccess(){
    const { refresh } = getTokens();
    if(!refresh) return false;
    try{
      const res = await fetch(`${BASE.auth}/refresh/`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ refresh })
      });
      if(!res.ok) return false;
      const data = await res.json().catch(()=>null);
      const access = data?.access || data?.tokens?.access;
      if(access){
        localStorage.setItem("access_token", access);
        return true;
      }
      return false;
    }catch{
      return false;
    }
  }

  async function apiFetch(path, opts = {}){
    const url = path.startsWith("http") ? path : path;
    let res = await rawFetch(url, opts);

    if(res.status === 401){
      const ok = await refreshAccess();
      if(ok){
        res = await rawFetch(url, opts);
      }
    }
    const text = await res.text();
    let data = null;
    try{ data = text ? JSON.parse(text) : null; }catch{ data = text; }
    if(!res.ok){
      const msg = (data && (data.error || data.detail)) ? (data.error || data.detail) : `HTTP ${res.status}`;
      const err = new Error(msg);
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  const getQuote = (symbol) => apiFetch(`${BASE.api}/crypto/${encodeURIComponent(symbol)}/`, {method:"GET"});
  const getHistory = (symbol, limit=100) => apiFetch(`${BASE.api}/crypto/${encodeURIComponent(symbol)}/history/?limit=${encodeURIComponent(limit)}`, {method:"GET"});

  const aiCoin = (symbol, lang="uk") => apiFetch(`${BASE.api}/ai/analysis/`, {method:"POST", body: JSON.stringify({symbol, lang})});
  const openaiCoin = (symbol, lang="uk") => apiFetch(`${BASE.api}/openai/analysis/`, {method:"POST", body: JSON.stringify({symbol, lang})});
  const aiPortfolio = (lang="uk") => apiFetch(`${BASE.api}/ai/portfolio/?lang=${encodeURIComponent(lang)}`, {method:"GET"});
  const openaiPortfolio = (lang="uk") => apiFetch(`${BASE.api}/openai/portfolio/?lang=${encodeURIComponent(lang)}`, {method:"GET"});
  const calcValue = (symbol, amount) => apiFetch(`${BASE.api}/calculator/`, {method:"POST", body: JSON.stringify({symbol, amount})});

  const profile = () => apiFetch(`${BASE.auth}/profile/`, {method:"GET"});
  const updateProfile = (patch) => apiFetch(`${BASE.auth}/profile/update/`, {method:"PATCH", body: JSON.stringify(patch)});
  const unlinkDiscord = () => apiFetch(`${BASE.auth}/unlink-discord/`, {method:"POST", body: JSON.stringify({})});
  const logout = () => apiFetch(`${BASE.auth}/logout/`, {method:"POST", body: JSON.stringify({ refresh_token: localStorage.getItem("refresh_token") })});

  const listUserPortfolio = () => apiFetch(`${BASE.auth}/portfolio/`, {method:"GET"});
  const addUserAsset = (asset, amount) => {
    const payload = { amount };
    if(typeof asset === "number"){
      payload.crypto = asset;
    }else if(asset){
      payload.symbol = String(asset).toUpperCase();
    }
    return apiFetch(`${BASE.auth}/portfolio/add/`, {method:"POST", body: JSON.stringify(payload)});
  };
  const removeUserAsset = (asset, amount) => {
    const payload = { amount };
    if(typeof asset === "number"){
      payload.crypto = asset;
    }else if(asset){
      payload.symbol = String(asset).toUpperCase();
    }
    return apiFetch(`${BASE.auth}/portfolio/remove/`, {method:"POST", body: JSON.stringify(payload)});
  };
  const pinDashboardSymbol = (symbol) => apiFetch(`${BASE.auth}/dashboard/symbol/`, {method:"POST", body: JSON.stringify({symbol})});

  return {
    BASE,
    getTokens, setTokens, getUser, setUser,
    apiFetch,
    getQuote, getHistory,
    aiCoin, openaiCoin, aiPortfolio, openaiPortfolio, calcValue,
    profile, updateProfile, unlinkDiscord, logout,
    listUserPortfolio, addUserAsset, removeUserAsset, pinDashboardSymbol
  };
})();
