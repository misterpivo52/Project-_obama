
function mountLayout({pageTitle, pageSubtitle}){
  const root = document.getElementById("app");
  if(!root) return;

  root.innerHTML = `
    <div class="container">
      <div class="shell">
        <aside class="sidebar">
          <div class="brand">
            <div class="logo"></div>
            <div>
              <h1>CryptoTaro</h1>
              <small data-i18n="appTag"></small>
            </div>
          </div>
          <nav class="nav">
            <a href="dashboard.html" data-page="dashboard.html"><span>&#128200;</span><span data-i18n="navDashboard"></span></a>
            <a href="market.html" data-page="market.html"><span>&#129689;</span><span data-i18n="navMarket"></span></a>
            <a href="ai.html" data-page="ai.html"><span>&#10024;</span><span data-i18n="navAI"></span></a>
            <a href="calculator.html" data-page="calculator.html"><span>&#8721;</span><span data-i18n="navCalculator"></span></a>
            <a href="portfolio.html" data-page="portfolio.html"><span>&#128179;</span><span data-i18n="navPortfolio"></span></a>
            <div class="spacer"></div>
            <a href="settings.html" data-page="settings.html"><span>&#9881;</span><span data-i18n="navSettings"></span></a>
            <a href="index.html"><span>&#9786;</span><span data-i18n="navProfile"></span></a>
          </nav>
          <div class="sidebar-footer">
            <button class="btn" id="ct_lang_btn">🌐 <span id="ct_lang_lbl">UA</span></button>
            <button class="btn danger" id="ct_logout_btn">⎋ <span data-i18n="logout"></span></button>
          </div>
        </aside>

        <main class="main">
          <header class="topbar">
            <div class="title">
              <h2>${escapeHtml(pageTitle || "")}</h2>
              <p>${escapeHtml(pageSubtitle || "")}</p>
            </div>
            <div class="pills">
              <span class="pill"><span class="muted" data-i18n="connect"></span>: <b id="ct_conn_lbl">—</b></span>
              <span class="pill" id="ct_user_pill">—</span>
            </div>
          </header>

          <section id="page"></section>
        </main>
      </div>
    </div>
  `;

  const btn = document.getElementById("ct_lang_btn");
  const lbl = document.getElementById("ct_lang_lbl");
  const setLbl = () => lbl.textContent = (I18N.getLang() === "uk" ? "UA" : "EN");
  setLbl();
  btn.onclick = () => {
    I18N.setLang(I18N.getLang() === "uk" ? "en" : "uk");
    setLbl();
    I18N.apply();
    UI.toast("CryptoTaro", `Lang: ${I18N.getLang()}`);
    if(window.onLanguageChanged) window.onLanguageChanged(I18N.getLang());
  };

  document.getElementById("ct_logout_btn").onclick = () => AUTH.doLogout();

  const conn = document.getElementById("ct_conn_lbl");
  const updateConn = () => {
    conn.textContent = navigator.onLine ? I18N.t("online") : I18N.t("offline");
    conn.style.color = navigator.onLine ? "#b8f7cd" : "#fecaca";
  };
  window.addEventListener("online", updateConn);
  window.addEventListener("offline", updateConn);
  updateConn();

  AUTH.markActiveNav();
  I18N.apply();
}

function escapeHtml(s){
  return String(s ?? "").replace(/[&<>"']/g, m => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[m]));
}
