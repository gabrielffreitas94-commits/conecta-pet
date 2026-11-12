import html
from typing import Any, Dict, List, Optional
import urllib.parse

from conecta_pet import services

LOCATIONS = [
    {"label": "Pinheiros, São Paulo - SP", "lat": -23.5615, "lng": -46.6858},
    {"label": "Vila Mariana, São Paulo - SP", "lat": -23.5842, "lng": -46.6365},
    {"label": "Moema, São Paulo - SP", "lat": -23.5991, "lng": -46.6612},
    {"label": "Perdizes, São Paulo - SP", "lat": -23.5362, "lng": -46.6744},
    {"label": "Tatuapé, São Paulo - SP", "lat": -23.5401, "lng": -46.5766},
]

SPECIALTIES = [
    "Todas",
    "Clínica Geral",
    "Urgência Domiciliar",
    "Medicina Felina",
    "Dermatologia",
    "Ortopedia",
    "Pets Exóticos e Silvestres",
    "Telemedicina & Triagem",
    "Cardiologia",
    "Vacinação",
]


def format_brl(cents: Optional[int]) -> str:
    if cents is None:
        return "R$ 0,00"
    reais = cents / 100.0
    formatted = f"{reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def modality_label(mod: str) -> str:
    return {
        "CLINIC": "No Consultório",
        "HOME_VISIT": "Visita Domiciliar",
        "ONLINE": "Consulta Online",
    }.get(mod, mod)


def status_badge(status: str) -> Dict[str, str]:
    return {
        "PENDING_QUOTE": {"label": "Aguardando Confirmação do Vet", "cls": "badge-amber"},
        "ACCEPTED": {"label": "Confirmado pelo Veterinário", "cls": "badge-emerald"},
        "COMPLETED": {"label": "Atendimento Concluído", "cls": "badge-blue"},
        "REJECTED": {"label": "Indisponível no Momento", "cls": "badge-rose"},
    }.get(status, {"label": status, "cls": "badge-slate"})


def build_query(base_params: Dict[str, str], **overrides: Any) -> str:
    merged = {**base_params}
    for k, v in overrides.items():
        if v is None or v == "":
            merged.pop(k, None)
        else:
            merged[k] = str(v)
    return "/?" + urllib.parse.urlencode(merged)


CSS_STYLES = """
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu, sans-serif;
  background: #f8fafc;
  color: #0f172a;
  line-height: 1.5;
}
a { text-decoration: none; color: inherit; }
button, input, select, textarea { font-family: inherit; font-size: inherit; }
button { cursor: pointer; }

.topbar {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.96);
  border-bottom: 1px solid #e2e8f0;
  padding: 0.75rem 1.25rem;
}
.topbar-inner {
  max-width: 1240px; margin: 0 auto;
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.75rem;
}
.brand { display: flex; align-items: center; gap: 0.75rem; }
.brand-icon {
  width: 42px; height: 42px; border-radius: 14px;
  background: linear-gradient(135deg, #f43f5e, #be123c);
  color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.35rem;
}
.brand-title { font-weight: 800; font-size: 1.2rem; color: #0f172a; }
.brand-title span { color: #e11d48; }
.brand-sub { font-size: 0.75rem; color: #64748b; }

.nav-pills {
  display: flex; flex-wrap: wrap; gap: 0.35rem;
  background: #f1f5f9; padding: 0.3rem; border-radius: 12px;
}
.nav-pill {
  padding: 0.45rem 0.85rem; border-radius: 9px; font-size: 0.82rem; font-weight: 700;
  color: #475569; display: inline-flex; align-items: center; gap: 0.35rem;
}
.nav-pill.active { background: #fff; color: #e11d48; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.device-toggle {
  display: flex; background: #0f172a; padding: 0.25rem; border-radius: 12px; gap: 0.25rem;
}
.device-btn {
  padding: 0.38rem 0.75rem; border-radius: 9px; font-size: 0.78rem; font-weight: 700; color: #cbd5e1;
}
.device-btn.active { background: #e11d48; color: #fff; }

.container { max-width: 1240px; margin: 0 auto; padding: 1.5rem 1.25rem 4rem; }
.hero {
  background: linear-gradient(110deg, #0f172a 0%, #1e293b 55%, #4c0519 100%);
  color: #fff; border-radius: 24px; padding: 1.5rem; margin-bottom: 1.25rem;
}
.hero-top {
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;
}
.hero h1 { margin: 0.35rem 0; font-size: 1.65rem; font-weight: 800; }
.hero p { margin: 0; font-size: 0.88rem; color: #cbd5e1; max-width: 640px; }

.modality-tabs {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 0.65rem; margin-top: 1.25rem;
}
.mod-tab {
  background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.16);
  color: #fff; border-radius: 16px; padding: 0.8rem 1rem; display: flex; align-items: center; gap: 0.75rem;
}
.mod-tab.active {
  background: #fff; color: #0f172a; border-color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.18);
}
.mod-tab-title { font-weight: 800; font-size: 0.88rem; }
.mod-tab-desc { font-size: 0.74rem; opacity: 0.85; }
.mod-tab.active .mod-tab-desc { color: #e11d48; font-weight: 700; opacity: 1; }

.filter-bar {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 1rem; margin-bottom: 1rem;
}
.filter-row {
  display: flex; flex-wrap: wrap; gap: 0.65rem; align-items: center;
}
.input, .select {
  padding: 0.6rem 0.85rem; border-radius: 11px; border: 1px solid #cbd5e1; background: #fff; font-size: 0.85rem;
}
.input-grow { flex: 1; min-width: 210px; }
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.4rem;
  padding: 0.58rem 1rem; border-radius: 11px; font-weight: 700; font-size: 0.82rem; border: 1px solid transparent;
}
.btn-primary { background: #e11d48; color: #fff; }
.btn-primary:hover { background: #be123c; }
.btn-teal { background: #0d9488; color: #fff; }
.btn-emerald { background: #059669; color: #fff; }
.btn-blue { background: #2563eb; color: #fff; }
.btn-amber { background: #f59e0b; color: #0f172a; }
.btn-outline { background: #f8fafc; border-color: #cbd5e1; color: #334155; }

.spec-row {
  display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.85rem; padding-top: 0.75rem; border-top: 1px solid #f1f5f9;
}
.spec-pill {
  padding: 0.3rem 0.75rem; border-radius: 999px; font-size: 0.76rem; font-weight: 600;
  background: #f1f5f9; color: #475569;
}
.spec-pill.active { background: #e11d48; color: #fff; }

.vet-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem;
}
.vet-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 20px; overflow: hidden;
  display: flex; flex-direction: column; justify-content: space-between;
}
.vet-card-body { padding: 1.15rem; }
.vet-header { display: flex; gap: 0.9rem; align-items: flex-start; }
.vet-avatar { width: 68px; height: 68px; border-radius: 16px; object-fit: cover; border: 1px solid #e2e8f0; }
.vet-name { font-weight: 800; font-size: 1.05rem; margin: 0; }
.vet-meta { font-size: 0.76rem; color: #64748b; margin-top: 0.2rem; }
.vet-bio { font-size: 0.8rem; color: #475569; margin: 0.75rem 0; }

.mod-box {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.55rem 0.75rem; border-radius: 12px; margin-top: 0.45rem; font-size: 0.8rem;
}
.mod-clinic { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; }
.mod-home { background: #fffbeb; border: 1px solid #fde68a; color: #78350f; }
.mod-online { background: #faf5ff; border: 1px solid #e9d5ff; color: #581c87; }

.vet-footer {
  background: #f8fafc; border-top: 1px solid #f1f5f9; padding: 0.75rem 1.15rem;
  display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; font-size: 0.75rem; color: #64748b;
}

.badge {
  display: inline-flex; align-items: center; padding: 0.2rem 0.6rem; border-radius: 999px;
  font-size: 0.72rem; font-weight: 700;
}
.badge-emerald { background: #d1fae5; color: #065f46; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-rose { background: #ffe4e6; color: #9f1239; }
.badge-slate { background: #e2e8f0; color: #334155; }

.modal-backdrop {
  position: fixed; inset: 0; z-index: 50; background: rgba(15, 23, 42, 0.65);
  display: flex; align-items: center; justify-content: center; padding: 1rem; overflow-y: auto;
}
.modal-card {
  background: #fff; border-radius: 24px; max-width: 540px; width: 100%; padding: 1.5rem;
  box-shadow: 0 25px 50px rgba(0,0,0,0.3);
}
.form-group { margin-bottom: 0.85rem; }
.form-label { display: block; font-size: 0.78rem; font-weight: 700; color: #334155; margin-bottom: 0.3rem; }

.phone-frame-wrapper {
  background: #0f172a; min-height: calc(100vh - 64px); padding: 1.5rem 1rem;
  display: flex; flex-direction: column; align-items: center;
}
.phone-mockup {
  width: 412px; max-width: 100%; height: 800px; background: #f8fafc;
  border: 12px solid #1e293b; border-radius: 42px; overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5);
}
.toast-banner {
  background: #065f46; color: #fff; padding: 0.75rem 1.25rem; border-radius: 14px;
  margin-bottom: 1rem; font-size: 0.85rem; font-weight: 700; display: flex; justify-content: space-between; align-items: center;
}
"""


def render_page(query_params: Dict[str, str]) -> str:
    section = query_params.get("section", "VITRINE").upper()
    device = query_params.get("device", "WEB").upper()
    loc_idx = int(query_params.get("loc", "0"))
    if loc_idx < 0 or loc_idx >= len(LOCATIONS):
        loc_idx = 0
    loc = LOCATIONS[loc_idx]

    modality = query_params.get("modality", "ALL").upper()
    online_now = query_params.get("onlineNow", "false").lower() == "true"
    specialty = query_params.get("specialty", "Todas")
    search_q = query_params.get("search", "")
    sort_by = query_params.get("sortBy", "RECOMMENDED").upper()
    active_vet_id = query_params.get("activeVetId", "01932000-0000-7000-8000-000000000201")
    quote_vet_id = query_params.get("quoteVetId", "")
    quote_modality = query_params.get("quoteModality", "")
    show_new_vet = query_params.get("newVetModal", "") == "1"
    review_req_id = query_params.get("reviewReqId", "")
    toast_msg = query_params.get("toast", "")
    handoff_wa = query_params.get("handoffWa", "")

    base_q = {
        "section": section,
        "device": device,
        "loc": str(loc_idx),
        "modality": modality,
        "onlineNow": "true" if online_now else "false",
        "specialty": specialty,
        "search": search_q,
        "sortBy": sort_by,
        "activeVetId": active_vet_id,
    }

    catalog_data, cache_status = services.search_vets(
        modality=modality,
        online_now=online_now,
        specialty=specialty,
        search=search_q,
        sort_by=sort_by,
        lat=loc["lat"],
        lng=loc["lng"],
    )
    vets = catalog_data["items"]
    all_vets_data, _ = services.search_vets(lat=loc["lat"], lng=loc["lng"])
    all_vets = all_vets_data["items"]

    session = services.get_tutor_session()
    pets = session["pets"]
    requests_list = services.list_requests()
    metrics = services.get_system_metrics()

    pending_vet_count = sum(
        1
        for r in requests_list
        if r["vetId"] == active_vet_id and r["status"] == "PENDING_QUOTE"
    )

    # Top Navigation Bar
    topbar_html = f"""
    <header class="topbar">
      <div class="topbar-inner">
        <a href="{build_query(base_q, section='VITRINE', toast=None, handoffWa=None)}" class="brand">
          <div class="brand-icon">🐾</div>
          <div>
            <div class="brand-title">Conecta<span>Pet</span> <span class="badge badge-emerald">100% Gratuito • Python Backend</span></div>
            <div class="brand-sub">Consultório, Visita Domiciliar e Telemedicina Veterinária</div>
          </div>
        </a>

        <nav class="nav-pills">
          <a href="{build_query(base_q, section='VITRINE', toast=None, handoffWa=None)}"
             class="nav-pill {'active' if section == 'VITRINE' else ''}">
             🏪 Vitrine (Tutor)
          </a>
          <a href="{build_query(base_q, section='REQUESTS', toast=None, handoffWa=None)}"
             class="nav-pill {'active' if section == 'REQUESTS' else ''}">
             📋 Meus Pedidos <span class="badge badge-rose">{len(requests_list)}</span>
          </a>
          <a href="{build_query(base_q, section='VET_PANEL', toast=None, handoffWa=None)}"
             class="nav-pill {'active' if section == 'VET_PANEL' else ''}">
             🩺 Área do Veterinário
             {f'<span class="badge badge-amber">{pending_vet_count}</span>' if pending_vet_count else ''}
          </a>
          <a href="{build_query(base_q, section='SCALE_ARCH', toast=None, handoffWa=None)}"
             class="nav-pill {'active' if section == 'SCALE_ARCH' else ''}">
             ⚡ Escala & Backend
          </a>
        </nav>

        <div class="device-toggle">
          <a href="{build_query(base_q, device='WEB', toast=None)}"
             class="device-btn {'active' if device == 'WEB' else ''}">🖥️ Site Web</a>
          <a href="{build_query(base_q, device='MOBILE_APP', toast=None)}"
             class="device-btn {'active' if device == 'MOBILE_APP' else ''}">📱 App Mobile</a>
        </div>
      </div>
    </header>
    """

    toast_html = ""
    if toast_msg:
        wa_btn = (
            f'<a href="{html.escape(handoff_wa)}" target="_blank" class="btn btn-amber">💬 Abrir WhatsApp do Veterinário Agora</a>'
            if handoff_wa
            else ""
        )
        toast_html = f"""
        <div class="toast-banner">
          <span>✨ {html.escape(toast_msg)}</span>
          {wa_btn}
        </div>
        """

    if section == "REQUESTS":
        main_content = _render_requests_section(requests_list, session, base_q)
    elif section == "VET_PANEL":
        main_content = _render_vet_panel_section(all_vets, active_vet_id, requests_list, base_q)
    elif section == "SCALE_ARCH":
        main_content = _render_scale_section(metrics, base_q)
    else:
        main_content = _render_vitrine_section(
            vets=vets,
            meta=catalog_data["meta"],
            cache_status=cache_status,
            loc_idx=loc_idx,
            modality=modality,
            online_now=online_now,
            specialty=specialty,
            search_q=search_q,
            sort_by=sort_by,
            base_q=base_q,
        )

    modals_html = ""
    if quote_vet_id:
        target_vet = next((v for v in all_vets if v["id"] == quote_vet_id), None)
        if target_vet:
            modals_html += _render_quote_modal(target_vet, quote_modality, pets, loc["label"], base_q)
    if show_new_vet:
        modals_html += _render_new_vet_modal(base_q)
    if review_req_id:
        target_req = next((r for r in requests_list if r["id"] == review_req_id), None)
        if target_req:
            modals_html += _render_review_modal(target_req, base_q)

    if device == "MOBILE_APP":
        body_inner = f"""
        {topbar_html}
        <div class="phone-frame-wrapper">
          <div style="color:#cbd5e1; font-size:0.8rem; font-weight:700; margin-bottom:0.6rem;">
            📱 Simulador Interativo do App Mobile (iOS / Android)
          </div>
          <div class="phone-mockup">
            <div style="background:#0f172a; color:#fff; padding:0.5rem 1rem; font-size:0.72rem; font-weight:700; display:flex; justify-content:space-between;">
              <span>9:41</span><span>Conecta Pet App</span><span>5G 100% 🔋</span>
            </div>
            <div style="padding:0.85rem;">
              {toast_html}
              {main_content}
            </div>
          </div>
        </div>
        {modals_html}
        """
    else:
        body_inner = f"""
        {topbar_html}
        <main class="container">
          {toast_html}
          {main_content}
        </main>
        {modals_html}
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Conecta Pet — Veterinários no Consultório, em Casa ou Online</title>
  <style>{CSS_STYLES}</style>
</head>
<body>
  {body_inner}
</body>
</html>"""


def _render_vitrine_section(
    vets: List[Dict[str, Any]],
    meta: Dict[str, Any],
    cache_status: str,
    loc_idx: int,
    modality: str,
    online_now: bool,
    specialty: str,
    search_q: str,
    sort_by: str,
    base_q: Dict[str, str],
) -> str:
    loc_options = "".join(
        f'<option value="{idx}" {"selected" if idx == loc_idx else ""}>{html.escape(l["label"])}</option>'
        for idx, l in enumerate(LOCATIONS)
    )

    tabs_data = [
        ("ALL", "✨", "Todas Modalidades", "Visão completa"),
        ("CLINIC", "🏥", "No Consultório", "Vá até a clínica"),
        ("HOME_VISIT", "🚗", "Visita Domiciliar", "O vet vai até você"),
        ("ONLINE", "💻", "Consulta Online", "Telemedicina rápida"),
    ]
    tabs_html = "".join(
        f"""
        <a href="{build_query(base_q, modality=tab_id, toast=None, handoffWa=None)}"
           class="mod-tab {'active' if modality == tab_id else ''}">
          <span style="font-size:1.6rem;">{icon}</span>
          <div>
            <div class="mod-tab-title">{title}</div>
            <div class="mod-tab-desc">{desc}</div>
          </div>
        </a>
        """
        for tab_id, icon, title, desc in tabs_data
    )

    spec_pills_html = "".join(
        f"""
        <a href="{build_query(base_q, specialty=spec, toast=None, handoffWa=None)}"
           class="spec-pill {'active' if specialty == spec else ''}">
          {html.escape(spec)}
        </a>
        """
        for spec in SPECIALTIES
    )

    cards_html = ""
    if not vets:
        cards_html = f"""
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:20px; padding:2.5rem; text-align:center;">
          <div style="font-size:2.5rem;">🐶</div>
          <h3>Nenhum veterinário encontrado com esses filtros</h3>
          <a href="{build_query(base_q, modality='ALL', onlineNow='false', specialty='Todas', search='', toast=None)}"
             class="btn btn-primary">Limpar Filtros</a>
        </div>
        """
    else:
        card_items = []
        for vet in vets:
            clinic_cfg = vet["modalities"].get("CLINIC", {})
            home_cfg = vet["modalities"].get("HOME_VISIT", {})
            online_cfg = vet["modalities"].get("ONLINE", {})

            mods_html = ""
            if clinic_cfg.get("isActive"):
                mods_html += f"""
                <div class="mod-box mod-clinic">
                  <div>
                    <strong>🏥 No Consultório</strong>
                    <div style="font-size:0.7rem;">{html.escape(clinic_cfg.get('clinicAddress', ''))}</div>
                  </div>
                  <div style="display:flex; align-items:center; gap:0.5rem;">
                    <strong>{format_brl(clinic_cfg.get('basePriceCents'))}</strong>
                    <a href="{build_query(base_q, quoteVetId=vet['id'], quoteModality='CLINIC', toast=None)}"
                       class="btn btn-blue" style="padding:0.3rem 0.65rem; font-size:0.72rem;">Pedir</a>
                  </div>
                </div>
                """
            if home_cfg.get("isActive"):
                mods_html += f"""
                <div class="mod-box mod-home">
                  <div>
                    <strong>🚗 Visita Domiciliar (Raio {home_cfg.get('coverageRadiusKm')}km)</strong>
                    <div style="font-size:0.7rem;">Taxa deslocamento: +{format_brl(home_cfg.get('displacementFeeCents'))}</div>
                  </div>
                  <div style="display:flex; align-items:center; gap:0.5rem;">
                    <strong>{format_brl(home_cfg.get('basePriceCents'))}</strong>
                    <a href="{build_query(base_q, quoteVetId=vet['id'], quoteModality='HOME_VISIT', toast=None)}"
                       class="btn btn-amber" style="padding:0.3rem 0.65rem; font-size:0.72rem;">Pedir</a>
                  </div>
                </div>
                """
            if online_cfg.get("isActive"):
                mods_html += f"""
                <div class="mod-box mod-online">
                  <div>
                    <strong>💻 Consulta Online (Telemedicina)</strong>
                    <div style="font-size:0.7rem;">Videochamada + Orientação imediata</div>
                  </div>
                  <div style="display:flex; align-items:center; gap:0.5rem;">
                    <strong>{format_brl(online_cfg.get('basePriceCents'))}</strong>
                    <a href="{build_query(base_q, quoteVetId=vet['id'], quoteModality='ONLINE', toast=None)}"
                       class="btn btn-primary" style="padding:0.3rem 0.65rem; font-size:0.72rem;">Pedir</a>
                  </div>
                </div>
                """

            specs_badges = " ".join(
                f'<span class="badge badge-rose" style="margin-right:0.25rem;">{html.escape(s)}</span>'
                for s in vet.get("specialties", [])
            )
            online_badge = (
                '<span class="badge badge-emerald">🟢 DISPONÍVEL AGORA</span>'
                if vet.get("isOnlineNow")
                else '<span class="badge badge-slate">Agendamento</span>'
            )

            card_items.append(
                f"""
                <div class="vet-card">
                  <div class="vet-card-body">
                    <div class="vet-header">
                      <img src="{vet['avatarUrl']}" alt="{html.escape(vet['name'])}" class="vet-avatar" />
                      <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:0.4rem;">
                          <h3 class="vet-name">{html.escape(vet['name'])}</h3>
                          <span class="badge badge-amber">★ {vet['ratingAvg']:.2f} ({vet['ratingCount']})</span>
                        </div>
                        <div class="vet-meta">
                          ✓ CRMV-{html.escape(vet['crmvState'])} {html.escape(vet['crmvNumber'])} •
                          📍 {html.escape(vet['neighborhood'])} ({vet.get('distanceKm')} km) •
                          ⚡ ~{vet['responseTimeMins']} min
                        </div>
                        <div style="margin-top:0.4rem;">{online_badge}</div>
                      </div>
                    </div>
                    <div style="margin-top:0.65rem;">{specs_badges}</div>
                    <p class="vet-bio">{html.escape(vet.get('bio', ''))}</p>
                    <div>{mods_html}</div>
                  </div>
                  <div class="vet-footer">
                    <span>💳 Direto ao Vet: <strong>{html.escape(' • '.join(vet.get('acceptedPaymentMethods', [])))}</strong></span>
                    <a href="{build_query(base_q, quoteVetId=vet['id'], quoteModality=modality if modality != 'ALL' else '', toast=None)}"
                       class="btn btn-primary">Solicitar Orçamento →</a>
                  </div>
                </div>
                """
            )
        cards_html = f'<div class="vet-grid">{"".join(card_items)}</div>'

    return f"""
    <section class="hero">
      <div class="hero-top">
        <div>
          <span class="badge badge-rose">🐾 Marketplace Veterinário • Zero Taxas</span>
          <h1>Qual atendimento seu pet precisa hoje?</h1>
          <p>Escolha o veterinário na vitrine por preço, distância e avaliação. Combine o pré-orçamento e pague 100% direto ao profissional.</p>
        </div>
        <form method="GET" action="/" style="background:rgba(255,255,255,0.1); padding:0.75rem; border-radius:14px;">
          <input type="hidden" name="section" value="VITRINE" />
          <input type="hidden" name="device" value="{html.escape(base_q['device'])}" />
          <input type="hidden" name="modality" value="{html.escape(modality)}" />
          <label style="display:block; font-size:0.7rem; font-weight:700; color:#fecdd3; margin-bottom:0.3rem;">
            📍 SUA LOCALIZAÇÃO ATUAL (CÁLCULO HAVERSINE/GEO)
          </label>
          <div style="display:flex; gap:0.4rem;">
            <select name="loc" class="select" style="background:#0f172a; color:#fff; border-color:#334155;">
              {loc_options}
            </select>
            <button type="submit" class="btn btn-primary">Atualizar</button>
          </div>
        </form>
      </div>
      <div class="modality-tabs">{tabs_html}</div>
    </section>

    <section class="filter-bar">
      <form method="GET" action="/" class="filter-row">
        <input type="hidden" name="section" value="VITRINE" />
        <input type="hidden" name="device" value="{html.escape(base_q['device'])}" />
        <input type="hidden" name="loc" value="{loc_idx}" />
        <input type="hidden" name="modality" value="{html.escape(modality)}" />
        <input type="hidden" name="specialty" value="{html.escape(specialty)}" />
        <input type="text" name="search" value="{html.escape(search_q)}"
               placeholder="Buscar por nome do veterinário, especialidade, bairro ou sintoma..."
               class="input input-grow" />
        <select name="sortBy" class="select">
          <option value="RECOMMENDED" {"selected" if sort_by == "RECOMMENDED" else ""}>⭐ Recomendados (iFood Score)</option>
          <option value="DISTANCE" {"selected" if sort_by == "DISTANCE" else ""}>📍 Mais Próximos (Menor km)</option>
          <option value="PRICE_ASC" {"selected" if sort_by == "PRICE_ASC" else ""}>💰 Menor Preço Base</option>
          <option value="RATING_DESC" {"selected" if sort_by == "RATING_DESC" else ""}>🏆 Melhor Avaliação</option>
        </select>
        <button type="submit" class="btn btn-primary">🔍 Filtrar</button>
        <a href="{build_query(base_q, onlineNow='false' if online_now else 'true', toast=None)}"
           class="btn {'btn-emerald' if online_now else 'btn-outline'}">
           ⚡ Disponível Agora (Plantão)
        </a>
      </form>
      <div class="spec-row">{spec_pills_html}</div>
    </section>

    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.85rem; font-size:0.82rem; color:#475569;">
      <span>Encontramos <strong>{len(vets)} veterinários</strong> disponíveis para você</span>
      <div>
        <span class="badge badge-slate">GeoCell: {html.escape(meta.get('geoCell', ''))}</span>
        <span class="badge {'badge-emerald' if cache_status == 'HIT' else 'badge-amber'}">Cache: {cache_status}</span>
      </div>
    </div>

    {cards_html}
    """


def _render_requests_section(
    requests_list: List[Dict[str, Any]],
    session: Dict[str, Any],
    base_q: Dict[str, str],
) -> str:
    tutor = session.get("tutor") or {}
    pets = session.get("pets") or []

    rows = []
    for req in requests_list:
        st = status_badge(req["status"])
        wa_url = services.build_whatsapp_url(
            req["vetWhatsapp"],
            f"Olá {req['vetName']}! Sobre o pedido #{req['id'][-6:]} do pet {req['petName']} no Conecta Pet:",
        )
        price_val = req.get("agreedPriceCents") or req.get("estimatedPriceCents")
        meet_html = (
            f'<div style="margin-top:0.4rem;"><a href="{html.escape(req["externalMeetingLink"])}" target="_blank" style="color:#7e22ce; font-weight:700; text-decoration:underline;">🎥 Entrar na Videochamada ({html.escape(req["externalMeetingLink"])})</a></div>'
            if req.get("externalMeetingLink")
            else ""
        )

        actions_html = ""
        if req["status"] == "ACCEPTED":
            actions_html += f"""
            <form method="POST" action="/actions/request-status" style="display:inline;">
              <input type="hidden" name="requestId" value="{req['id']}" />
              <input type="hidden" name="status" value="COMPLETED" />
              <input type="hidden" name="returnSection" value="REQUESTS" />
              <button type="submit" class="btn btn-blue">✓ Marcar Atendimento como Concluído</button>
            </form>
            """
        if req["status"] == "COMPLETED" and not req.get("hasReview"):
            actions_html += f"""
            <a href="{build_query(base_q, section='REQUESTS', reviewReqId=req['id'], toast=None)}"
               class="btn btn-amber">⭐ Avaliar Veterinário (1 a 5 Estrelas)</a>
            """
        elif req.get("hasReview"):
            actions_html += '<span class="badge badge-amber">★ Avaliação enviada!</span>'

        rows.append(
            f"""
            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:18px; padding:1.25rem; margin-bottom:1rem;">
              <div style="display:flex; flex-wrap:wrap; justify-content:space-between; gap:0.75rem; border-bottom:1px solid #f1f5f9; padding-bottom:0.75rem;">
                <div>
                  <span class="badge badge-blue">{modality_label(req['modality'])}</span>
                  <span class="badge {st['cls']}">{st['label']}</span>
                  <span style="font-size:0.75rem; color:#94a3b8; font-family:monospace;">#{req['id'][-6:]}</span>
                  <h3 style="margin:0.35rem 0 0.15rem; font-size:1.05rem;">{html.escape(req['vetName'])} <span style="font-size:0.78rem; color:#64748b;">({html.escape(req['vetCrmv'])})</span></h3>
                  <div style="font-size:0.8rem; color:#475569;">🐾 Pet: <strong>{html.escape(req['petName'])}</strong> • 🕒 Horário: <strong>{html.escape(req['scheduledFor'])}</strong></div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:0.7rem; color:#64748b; font-weight:700;">VALOR COMBINADO (DIRETO AO VET)</div>
                  <div style="font-size:1.25rem; font-weight:800;">{format_brl(price_val)}</div>
                  <div style="font-size:0.72rem; color:#059669; font-weight:700;">Zero taxa do app</div>
                </div>
              </div>

              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:0.75rem; margin:0.85rem 0; font-size:0.8rem;">
                <div style="background:#f8fafc; padding:0.75rem; border-radius:12px;">
                  <strong>Sintomas / Solicitação enviada:</strong>
                  <p style="margin:0.25rem 0;">{html.escape(req['symptomsDescription'])}</p>
                  <div style="color:#64748b;">📍 {html.escape(req['tutorAddress'])}</div>
                </div>
                <div style="background:#f0fdfa; padding:0.75rem; border-radius:12px; border:1px solid #ccfbf1;">
                  <strong>Resposta / Pré-Orçamento do Veterinário:</strong>
                  <p style="margin:0.25rem 0;">{html.escape(req.get('vetQuoteNotes') or 'Aguardando confirmação do veterinário (você pode simular o aceite na aba Área do Veterinário).')}</p>
                  {meet_html}
                </div>
              </div>

              <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:0.5rem;">
                <a href="{wa_url}" target="_blank" class="btn btn-emerald">💬 Conversar no WhatsApp do Veterinário</a>
                <div>{actions_html}</div>
              </div>
            </div>
            """
        )

    return f"""
    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:18px; padding:1.25rem; margin-bottom:1.25rem; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h2 style="margin:0;">📋 Meus Pedidos & Pré-Orçamentos</h2>
        <p style="margin:0.2rem 0 0; font-size:0.82rem; color:#64748b;">Acompanhe as confirmações dos veterinários, acesse links de teleconsulta e avalie os atendimentos.</p>
      </div>
      <span class="badge badge-slate">Tutor: {html.escape(tutor.get('name', 'Lucas Mendes'))} ({len(pets)} pets)</span>
    </div>
    {"".join(rows)}
    """


def _render_vet_panel_section(
    all_vets: List[Dict[str, Any]],
    active_vet_id: str,
    requests_list: List[Dict[str, Any]],
    base_q: Dict[str, str],
) -> str:
    active_vet = next((v for v in all_vets if v["id"] == active_vet_id), all_vets[0] if all_vets else None)
    if not active_vet:
        return "<p>Nenhum veterinário cadastrado.</p>"

    vet_options = "".join(
        f'<option value="{v["id"]}" {"selected" if v["id"] == active_vet["id"] else ""}>{html.escape(v["name"])} (CRMV-{html.escape(v["crmvState"])} {html.escape(v["crmvNumber"])})</option>'
        for v in all_vets
    )

    vet_requests = [r for r in requests_list if r["vetId"] == active_vet["id"]]
    req_cards = []
    for req in vet_requests:
        st = status_badge(req["status"])
        price_reais = int((req.get("agreedPriceCents") or req.get("estimatedPriceCents") or 15000) / 100)
        if req["status"] == "PENDING_QUOTE":
            action_block = f"""
            <form method="POST" action="/actions/request-status" style="background:#f0fdfa; border:1px solid #99f6e4; border-radius:12px; padding:0.85rem; margin-top:0.75rem;">
              <input type="hidden" name="requestId" value="{req['id']}" />
              <input type="hidden" name="status" value="ACCEPTED" />
              <input type="hidden" name="returnSection" value="VET_PANEL" />
              <input type="hidden" name="activeVetId" value="{active_vet['id']}" />
              <div style="font-size:0.8rem; font-weight:800; color:#134e4a; margin-bottom:0.5rem;">Responder Pré-Orçamento & Confirmar Atendimento:</div>
              <div style="display:grid; grid-template-columns:140px 1fr; gap:0.6rem; margin-bottom:0.6rem;">
                <div>
                  <label class="form-label">Valor Final (R$)</label>
                  <input type="number" name="agreedPriceReais" value="{price_reais}" class="input" style="width:100%;" />
                </div>
                <div>
                  <label class="form-label">Mensagem / Orientação ao Tutor (Chave PIX, Horário)</label>
                  <input type="text" name="vetQuoteNotes" value="Confirmado! Posso atender no horário solicitado. O acerto pode ser feito por PIX ou cartão direto comigo." class="input" style="width:100%;" />
                </div>
              </div>
              <button type="submit" class="btn btn-teal">✓ Confirmar Orçamento e Aceitar Pedido</button>
            </form>
            """
        else:
            action_block = f"""
            <div style="font-size:0.8rem; color:#475569; margin-top:0.5rem;">
              Nota enviada: "{html.escape(req.get('vetQuoteNotes') or 'Atendimento confirmado')}"
            </div>
            """

        req_cards.append(
            f"""
            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:16px; padding:1.15rem; margin-bottom:0.85rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <span class="badge badge-blue">{modality_label(req['modality'])}</span>
                  <span class="badge {st['cls']}">{st['label']}</span>
                  <strong style="margin-left:0.4rem; font-size:0.88rem;">Tutor: {html.escape(req['tutorName'])} (Pet: {html.escape(req['petName'])})</strong>
                </div>
                <strong>{format_brl(req.get('agreedPriceCents') or req.get('estimatedPriceCents'))}</strong>
              </div>
              <div style="font-size:0.8rem; color:#475569; margin-top:0.5rem;">
                <strong>Sintomas:</strong> {html.escape(req['symptomsDescription'])} • <strong>Horário:</strong> {html.escape(req['scheduledFor'])}
              </div>
              {action_block}
            </div>
            """
        )

    return f"""
    <div class="hero" style="background:linear-gradient(110deg, #0f172a, #134e4a);">
      <div class="hero-top">
        <div>
          <span class="badge badge-emerald">🩺 Modo Parceiro Veterinário (100% Gratuito)</span>
          <h1>Painel de Plantão, Orçamentos e Vitrine</h1>
          <p>Gerencie sua disponibilidade em tempo real, confirme orçamentos e receba 100% do valor direto do tutor.</p>
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:0.6rem; align-items:flex-end;">
          <form method="GET" action="/">
            <input type="hidden" name="section" value="VET_PANEL" />
            <input type="hidden" name="device" value="{html.escape(base_q['device'])}" />
            <label style="display:block; font-size:0.7rem; color:#99f6e4; font-weight:700; margin-bottom:0.25rem;">SIMULAR VISÃO DO VETERINÁRIO:</label>
            <div style="display:flex; gap:0.4rem;">
              <select name="activeVetId" class="select" style="background:#0f172a; color:#fff; border-color:#334155;">
                {vet_options}
              </select>
              <button type="submit" class="btn btn-teal">Trocar</button>
            </div>
          </form>
          <a href="{build_query(base_q, section='VET_PANEL', newVetModal='1', toast=None)}" class="btn btn-amber">
            + Cadastrar Novo Veterinário (30s)
          </a>
        </div>
      </div>
    </div>

    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:18px; padding:1.25rem; margin-bottom:1.25rem; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:1rem;">
      <div style="display:flex; align-items:center; gap:0.85rem;">
        <img src="{active_vet['avatarUrl']}" class="vet-avatar" />
        <div>
          <h3 style="margin:0;">{html.escape(active_vet['name'])} <span class="badge badge-slate">CRMV-{html.escape(active_vet['crmvState'])} {html.escape(active_vet['crmvNumber'])}</span></h3>
          <div style="font-size:0.8rem; color:#64748b;">📍 {html.escape(active_vet['neighborhood'])}, {html.escape(active_vet['city'])} • Nota ★ {active_vet['ratingAvg']:.2f} ({active_vet['ratingCount']} avaliações)</div>
        </div>
      </div>
      <form method="POST" action="/actions/toggle-availability" style="display:flex; align-items:center; gap:0.85rem; background:#f8fafc; padding:0.75rem 1rem; border-radius:14px; border:1px solid #e2e8f0;">
        <input type="hidden" name="vetId" value="{active_vet['id']}" />
        <div>
          <div style="font-size:0.82rem; font-weight:800; color:{'#047857' if active_vet['isOnlineNow'] else '#475569'};">
            {'🟢 PLANTÃO ATIVO (Disponível Agora)' if active_vet['isOnlineNow'] else '⚪ MODO APENAS AGENDAMENTO'}
          </div>
          <div style="font-size:0.72rem; color:#64748b;">Destaque imediato no topo da vitrine</div>
        </div>
        <button type="submit" class="btn {'btn-primary' if active_vet['isOnlineNow'] else 'btn-emerald'}">
          {'Pausar Plantão' if active_vet['isOnlineNow'] else 'Ficar Online Agora'}
        </button>
      </form>
    </div>

    <h3>📥 Solicitações de Tutores para {html.escape(active_vet['name'])} ({len(vet_requests)})</h3>
    {"".join(req_cards) if req_cards else '<div style="background:#fff; padding:2rem; border-radius:16px; border:1px solid #e2e8f0; text-align:center; color:#64748b;">Nenhuma solicitação recebida para este veterinário ainda.</div>'}
    """


def _render_scale_section(metrics: Dict[str, Any], base_q: Dict[str, str]) -> str:
    cm = metrics.get("cacheMetrics", {})
    qm = metrics.get("queueMetrics", {})
    jobs_html = "".join(
        f"""
        <div style="padding:0.55rem 0; border-bottom:1px solid #f1f5f9; display:flex; justify-content:space-between; font-family:monospace; font-size:0.78rem;">
          <span><span class="badge badge-emerald">{j['status']}</span> <strong>[{html.escape(j['jobName'])}]</strong> {html.escape(j.get('summary', ''))}</span>
          <span style="color:#64748b;">{html.escape(j.get('completedAt', '')[:19])}</span>
        </div>
        """
        for j in qm.get("recentJobs", [])
    )

    return f"""
    <div class="hero" style="background:linear-gradient(110deg, #1e1b4b, #0f172a);">
      <div class="hero-top">
        <div>
          <span class="badge badge-blue">⚡ Engenharia de Grande Escala (Python 3 Stateless)</span>
          <h1>Telemetria da Arquitetura Conecta Pet</h1>
          <p>Monitoramento ao vivo da instância Python, taxa de acerto do cache geoespacial (Geo-Cell TTL) e fila assíncrona de workers.</p>
        </div>
        <a href="{build_query(base_q, section='SCALE_ARCH', toast=None)}" class="btn btn-blue">🔄 Atualizar Telemetria</a>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:1rem; margin-bottom:1.25rem;">
      <div style="background:#fff; padding:1.15rem; border-radius:16px; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b; font-weight:700;">INSTÂNCIA STATELESS ATIVA</div>
        <div style="font-size:1.1rem; font-weight:800; color:#4f46e5; font-family:monospace; margin-top:0.25rem;">{html.escape(metrics.get('instanceId', ''))}</div>
        <div style="font-size:0.72rem; color:#94a3b8;">Python ThreadingHTTPServer + WSGI/ASGI Ready</div>
      </div>
      <div style="background:#fff; padding:1.15rem; border-radius:16px; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b; font-weight:700;">GEO-CACHE HIT RATE (TTL)</div>
        <div style="font-size:1.5rem; font-weight:800; color:#059669; margin-top:0.25rem;">{cm.get('hitRatePercent', 0)}%</div>
        <div style="font-size:0.72rem; color:#94a3b8;">Hits: {cm.get('hits', 0)} • Misses: {cm.get('misses', 0)}</div>
      </div>
      <div style="background:#fff; padding:1.15rem; border-radius:16px; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b; font-weight:700;">FILA ASSÍNCRONA DE WORKERS</div>
        <div style="font-size:1.5rem; font-weight:800; color:#d97706; margin-top:0.25rem;">{qm.get('completed', 0)} jobs</div>
        <div style="font-size:0.72rem; color:#94a3b8;">Desacoplamento de notificações e notas</div>
      </div>
      <div style="background:#fff; padding:1.15rem; border-radius:16px; border:1px solid #e2e8f0;">
        <div style="font-size:0.75rem; color:#64748b; font-weight:700;">BANCO DE DADOS & CHAVES</div>
        <div style="font-size:1.05rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">PostgreSQL 16 + UUIDv7</div>
        <div style="font-size:0.72rem; color:#94a3b8;">Ordenação temporal RFC 9562</div>
      </div>
    </div>

    <div style="background:#fff; padding:1.25rem; border-radius:18px; border:1px solid #e2e8f0;">
      <h3 style="margin-top:0; font-size:0.95rem;">⚙️ Eventos Recentes Processados em Background</h3>
      {jobs_html or '<div style="font-size:0.8rem; color:#94a3b8;">Envie um pedido ou avaliação para visualizar os jobs assíncronos.</div>'}
    </div>
    """


def _render_quote_modal(
    vet: Dict[str, Any],
    preferred_mod: str,
    pets: List[Dict[str, Any]],
    default_address: str,
    base_q: Dict[str, str],
) -> str:
    active_mods = vet.get("activeModalities", ["ONLINE"])
    chosen_mod = preferred_mod if preferred_mod in active_mods else active_mods[0]

    mod_options = "".join(
        f'<option value="{m}" {"selected" if m == chosen_mod else ""}>{modality_label(m)} — {format_brl(vet["modalities"][m]["basePriceCents"])}</option>'
        for m in active_mods
    )
    slot_options = "".join(
        f'<option value="{html.escape(s)}">{html.escape(s)}</option>'
        for s in vet.get("nextAvailableSlots", ["Agora (Plantão)"])
    )
    pet_options = "".join(
        f'<option value="{p["id"]}">🐾 {html.escape(p["name"])} ({html.escape(p["breed"])})</option>'
        for p in pets
    )

    return f"""
    <div class="modal-backdrop">
      <div class="modal-card">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:0.75rem; margin-bottom:1rem;">
          <div>
            <div style="font-size:0.7rem; font-weight:800; color:#e11d48; text-transform:uppercase;">Pré-Orçamento Sem Compromisso</div>
            <h3 style="margin:0.15rem 0 0;">{html.escape(vet['name'])} (CRMV-{html.escape(vet['crmvState'])} {html.escape(vet['crmvNumber'])})</h3>
          </div>
          <a href="{build_query(base_q, quoteVetId=None, quoteModality=None)}" class="btn btn-outline">✕</a>
        </div>

        <form method="POST" action="/actions/create-request">
          <input type="hidden" name="vetId" value="{vet['id']}" />
          <div class="form-group">
            <label class="form-label">1. Modalidade de Atendimento</label>
            <select name="modality" class="select" style="width:100%;">{mod_options}</select>
          </div>
          <div class="form-group">
            <label class="form-label">2. Horário Desejado</label>
            <select name="scheduledFor" class="select" style="width:100%;">{slot_options}</select>
          </div>
          <div class="form-group">
            <label class="form-label">3. Selecione seu Pet (ou preencha um novo abaixo)</label>
            <select name="petId" class="select" style="width:100%;">{pet_options}</select>
          </div>
          <div class="form-group">
            <label class="form-label">Ou Cadastrar Novo Pet Rapidinho (Opcional)</label>
            <input type="text" name="newPetName" placeholder="Nome do novo pet (ex: Paçoca)" class="input" style="width:100%;" />
          </div>
          <div class="form-group">
            <label class="form-label">4. Endereço (para Visita Domiciliar)</label>
            <input type="text" name="tutorAddress" value="{html.escape(default_address)}" class="input" style="width:100%;" />
          </div>
          <div class="form-group">
            <label class="form-label">5. Descreva brevemente os sintomas ou motivo da consulta</label>
            <textarea name="symptomsDescription" rows="3" class="input" style="width:100%;" placeholder="Ex: Está sem apetite desde ontem, gostaria de avaliação...">Gostaria de realizar uma avaliação veterinária e confirmar disponibilidade.</textarea>
          </div>
          <div style="background:#0f172a; color:#fff; padding:0.85rem 1rem; border-radius:14px; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:0.75rem;">
              <div style="color:#34d399; font-weight:700;">✓ 100% Gratuito no App</div>
              <div>Pagamento direto ao veterinário no atendimento</div>
            </div>
            <button type="submit" class="btn btn-primary">Enviar Solicitação →</button>
          </div>
        </form>
      </div>
    </div>
    """


def _render_new_vet_modal(base_q: Dict[str, str]) -> str:
    return f"""
    <div class="modal-backdrop">
      <div class="modal-card">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:0.75rem; margin-bottom:1rem;">
          <div>
            <div style="font-size:0.7rem; font-weight:800; color:#0d9488; text-transform:uppercase;">Onboarding em 30 Segundos</div>
            <h3 style="margin:0.15rem 0 0;">Cadastrar Veterinário na Vitrine</h3>
          </div>
          <a href="{build_query(base_q, newVetModal=None)}" class="btn btn-outline">✕</a>
        </div>

        <form method="POST" action="/actions/register-vet">
          <div class="form-group">
            <label class="form-label">Nome Completo *</label>
            <input type="text" name="name" required placeholder="Ex: Dra. Fernanda Lima" class="input" style="width:100%;" />
          </div>
          <div style="display:grid; grid-template-columns:1fr 80px 1fr; gap:0.5rem;" class="form-group">
            <div>
              <label class="form-label">Nº CRMV *</label>
              <input type="text" name="crmvNumber" required placeholder="54321" class="input" style="width:100%;" />
            </div>
            <div>
              <label class="form-label">UF</label>
              <input type="text" name="crmvState" value="SP" class="input" style="width:100%;" />
            </div>
            <div>
              <label class="form-label">WhatsApp *</label>
              <input type="text" name="whatsappPhone" required value="5511999998888" class="input" style="width:100%;" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Bairro Principal (São Paulo)</label>
            <input type="text" name="neighborhood" value="Pinheiros" class="input" style="width:100%;" />
          </div>
          <div class="form-group">
            <label class="form-label">Especialidades (separadas por vírgula)</label>
            <input type="text" name="specialties" value="Clínica Geral, Dermatologia, Vacinação" class="input" style="width:100%;" />
          </div>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:0.5rem;" class="form-group">
            <div>
              <label class="form-label">🏥 Consultório (R$)</label>
              <input type="number" name="priceClinic" value="150" class="input" style="width:100%;" />
            </div>
            <div>
              <label class="form-label">🚗 Domicílio (R$)</label>
              <input type="number" name="priceHome" value="200" class="input" style="width:100%;" />
            </div>
            <div>
              <label class="form-label">💻 Online (R$)</label>
              <input type="number" name="priceOnline" value="90" class="input" style="width:100%;" />
            </div>
          </div>
          <button type="submit" class="btn btn-teal" style="width:100%; padding:0.75rem;">Publicar Perfil na Vitrine Agora</button>
        </form>
      </div>
    </div>
    """


def _render_review_modal(req: Dict[str, Any], base_q: Dict[str, str]) -> str:
    return f"""
    <div class="modal-backdrop">
      <div class="modal-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.85rem;">
          <h3 style="margin:0;">⭐ Avaliar Atendimento de {html.escape(req['vetName'])}</h3>
          <a href="{build_query(base_q, reviewReqId=None)}" class="btn btn-outline">✕</a>
        </div>
        <form method="POST" action="/actions/create-review">
          <input type="hidden" name="serviceRequestId" value="{req['id']}" />
          <div class="form-group">
            <label class="form-label">Nota (1 a 5 estrelas)</label>
            <select name="rating" class="select" style="width:100%;">
              <option value="5">⭐⭐⭐⭐⭐ (5 - Excelente!)</option>
              <option value="4">⭐⭐⭐⭐ (4 - Muito Bom)</option>
              <option value="3">⭐⭐⭐ (3 - Regular)</option>
              <option value="2">⭐⭐ (2 - Ruim)</option>
              <option value="1">⭐ (1 - Péssimo)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Comentário</label>
            <textarea name="comment" rows="3" class="input" style="width:100%;">Excelente profissional! Muito atencioso(a) e pontual.</textarea>
          </div>
          <button type="submit" class="btn btn-amber" style="width:100%;">Enviar Avaliação</button>
        </form>
      </div>
    </div>
    """
