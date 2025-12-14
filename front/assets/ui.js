
const UI = (() => {
  const wrapId = "ct_toast_wrap";
  function ensureWrap(){
    let w = document.getElementById(wrapId);
    if(!w){
      w = document.createElement("div");
      w.id = wrapId;
      w.className = "toast-wrap";
      document.body.appendChild(w);
    }
    return w;
  }
  function toast(title, message){
    const w = ensureWrap();
    const el = document.createElement("div");
    el.className = "toast";
    el.innerHTML = `<b>${escapeHtml(title)}</b><p>${escapeHtml(message)}</p>`;
    w.appendChild(el);
    setTimeout(()=>{ el.style.opacity="0"; el.style.transform="translateY(6px)"; }, 3500);
    setTimeout(()=>{ el.remove(); }, 4200);
  }
  function escapeHtml(s){
    return String(s ?? "").replace(/[&<>"']/g, m => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    }[m]));
  }

  function modal({title, bodyHtml, okText, cancelText, onOk}){
    let backdrop = document.getElementById("ct_modal_backdrop");
    if(!backdrop){
      backdrop = document.createElement("div");
      backdrop.id = "ct_modal_backdrop";
      backdrop.className = "modal-backdrop";
      backdrop.innerHTML = `
        <div class="modal">
          <h3 id="ct_modal_title"></h3>
          <div id="ct_modal_body"></div>
          <div class="modal-actions">
            <button class="btn ghost" id="ct_modal_cancel"></button>
            <button class="btn primary" id="ct_modal_ok"></button>
          </div>
        </div>
      `;
      document.body.appendChild(backdrop);
    }
    backdrop.style.display = "flex";
    backdrop.querySelector("#ct_modal_title").textContent = title || "";
    backdrop.querySelector("#ct_modal_body").innerHTML = bodyHtml || "";
    const okBtn = backdrop.querySelector("#ct_modal_ok");
    const cancelBtn = backdrop.querySelector("#ct_modal_cancel");
    okBtn.textContent = okText || I18N.t("ok");
    cancelBtn.textContent = cancelText || I18N.t("cancel");

    const close = () => { backdrop.style.display = "none"; };
    cancelBtn.onclick = () => close();
    backdrop.onclick = (e) => { if(e.target === backdrop) close(); };
    okBtn.onclick = async () => {
      try{
        const res = onOk ? await onOk(backdrop) : true;
        if(res !== false) close();
      }catch(err){
        toast(I18N.t("apiError"), String(err?.message || err));
      }
    };
  }

  function formatMoney(v, c="USD"){
    const n = Number(v);
    if(!Number.isFinite(n)) return "—";
    try{
      return new Intl.NumberFormat(undefined, {style:"currency", currency:c, maximumFractionDigits: 2}).format(n);
    }catch{
      return "$" + n.toFixed(2);
    }
  }
  function formatNumber(v){
    const n = Number(v);
    if(!Number.isFinite(n)) return "—";
    try{ return new Intl.NumberFormat(undefined, {maximumFractionDigits: 8}).format(n); }catch{ return String(n); }
  }
  function formatPct(v){
    const n = Number(v);
    if(!Number.isFinite(n)) return "—";
    const s = (n >= 0 ? "+" : "") + n.toFixed(2) + "%";
    return s;
  }
  return { toast, modal, formatMoney, formatNumber, formatPct };
})();
