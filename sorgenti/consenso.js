/* Consenso alle statistiche di Google Analytics 4, secondo le Linee guida cookie del Garante
   (provvedimento del 10 giugno 2021): nessun cookie di statistica prima del «sì», due tasti di pari peso,
   la X chiude senza consenso, la scelta si può cambiare dal piè di pagina e l'avviso torna dopo 6 mesi.
   L'identificativo GA4 arriva dall'attributo data-ga4 del tag che carica questo file. */
(() => {
  const ID = document.currentScript && document.currentScript.dataset.ga4;
  if (!ID) return;
  const CHIAVE = 'ms-consenso', DURATA = 182 * 864e5;
  const leggi = () => {
    try { const v = JSON.parse(localStorage.getItem(CHIAVE)); return v && Date.now() - v.t < DURATA ? v.scelta : null; }
    catch { return null; }
  };
  const salva = scelta => { try { localStorage.setItem(CHIAVE, JSON.stringify({ scelta, t: Date.now() })); } catch {} };

  let avviato = false;
  function avviaStatistiche() {
    if (avviato) return;
    avviato = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    gtag('js', new Date());
    gtag('config', ID, { cookie_expires: 15552000, allow_google_signals: false, allow_ad_personalization_signals: false });
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ID);
    document.head.appendChild(s);
  }
  function cancellaCookie() {
    const dominio = location.hostname.replace(/^www\./, '');
    document.cookie.split(';').map(c => c.split('=')[0].trim()).filter(n => /^_ga/.test(n)).forEach(n => {
      for (const d of ['', '; domain=' + dominio, '; domain=.' + dominio]) document.cookie = n + '=; Max-Age=0; path=/' + d;
    });
  }

  let avviso;
  function chiudi() { if (avviso) avviso.hidden = true; }
  function scegli(si) {
    const prima = leggi();
    salva(si ? 'si' : 'no');
    chiudi();
    if (si) avviaStatistiche();
    else if (prima === 'si' || avviato) { cancellaCookie(); location.reload(); }
  }
  function mostra() {
    if (!avviso) {
      avviso = document.createElement('section');
      avviso.className = 'consenso gutter';
      avviso.setAttribute('role', 'dialog');
      avviso.setAttribute('aria-labelledby', 'consenso-titolo');
      avviso.innerHTML =
        '<div class="interno"><button type="button" class="consenso__x" data-scelta="no" aria-label="Chiudi senza accettare">×</button>' +
        '<h2 id="consenso-titolo">Mi aiuti a migliorare il sito?</h2>' +
        '<p>Con il tuo permesso uso Google Analytics per contare in forma aggregata le visite e capire quali pagine servono di più. ' +
        'Niente pubblicità e niente profilazione. Se rifiuti, o chiudi con la X, il sito funziona allo stesso modo e non viene salvato alcun cookie di statistica. ' +
        'Puoi cambiare idea quando vuoi dal piè di pagina. <a href="/privacy/">Leggi l\'informativa</a>.</p>' +
        '<div class="consenso__tasti"><button type="button" class="grosso" data-scelta="no">Rifiuto</button>' +
        '<button type="button" class="grosso" data-scelta="si">Accetto</button></div></div>';
      avviso.addEventListener('click', e => { const b = e.target.closest('[data-scelta]'); if (b) scegli(b.dataset.scelta === 'si'); });
      document.body.appendChild(avviso);
    }
    avviso.hidden = false;
    avviso.querySelector('[data-scelta="si"]').focus({ preventScroll: true });
  }

  function prepara() {
    const piede = document.querySelector('.piede-nero .interno span:last-child');
    if (piede) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'piede-preferenze';
      b.dataset.consenso = '';
      b.textContent = 'Preferenze cookie';
      piede.append(' · ', b);
    }
    document.addEventListener('click', e => { if (e.target.closest('[data-consenso]')) mostra(); });
    const scelta = leggi();
    if (scelta === 'si') avviaStatistiche();
    else if (scelta === null) mostra();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', prepara);
  else prepara();
})();
