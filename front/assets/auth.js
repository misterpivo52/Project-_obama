
const AUTH = (() => {
  function requireAuth(){
    const access = localStorage.getItem("access_token");
    if(!access){
      UI.toast("CryptoTaro", I18N.t("needAuth"));
      setTimeout(()=>{ window.location.href = "register.html"; }, 900);
      return false;
    }
    return true;
  }

  async function syncProfilePill(){
    const pill = document.getElementById("ct_user_pill");
    if(!pill) return;
    const user = API.getUser();
    if(user?.email){
      pill.textContent = user.email;
      return;
    }
    try{
      const prof = await API.profile();
      API.setUser(prof);
      pill.textContent = prof.email || "—";
    }catch{
      pill.textContent = "—";
    }
  }

  async function doLogout(){
    try{ await API.logout(); }catch{}
    localStorage.clear();
    window.location.href = "register.html";
  }

  function markActiveNav(){
    const p = location.pathname.split("/").pop();
    document.querySelectorAll(".nav a[data-page]").forEach(a=>{
      a.classList.toggle("active", a.getAttribute("data-page") === p);
    });
  }

  return { requireAuth, syncProfilePill, doLogout, markActiveNav };
})();
