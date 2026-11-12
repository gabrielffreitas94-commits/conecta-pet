from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from typing import Any, Dict, Optional
import urllib.parse

from conecta_pet import services
from conecta_pet.web import ui


class ConectaPetRequestHandler(BaseHTTPRequestHandler):
    """
    Handler HTTP Stateless Multi-Thread em Python.
    Serve tanto a REST API JSON (/api/*) quanto o Site Web e Simulador Mobile SSR (/, /actions/*).
    """

    def log_message(self, format_str: str, *args: Any) -> None:
        # Mantém logs limpos sem poluir saída de testes automatizados
        return

    def _send_json(
        self,
        status_code: int,
        payload: Dict[str, Any],
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("X-Instance-Id", services.INSTANCE_ID)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, status_code: int, html_str: str) -> None:
        raw = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def _read_body_data(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw_bytes = self.rfile.read(length)
        content_type = (self.headers.get("Content-Type") or "").lower()

        if "application/x-www-form-urlencoded" in content_type:
            parsed = urllib.parse.parse_qs(raw_bytes.decode("utf-8"), keep_blank_values=True)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

        text = raw_bytes.decode("utf-8").strip()
        if not text:
            return {}
        return json.loads(text)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(204, {})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        pathname = parsed.path
        qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        query_params = {k: v[0] for k, v in qs.items() if v}

        try:
            # 1. Telemetria & Healthcheck
            if pathname in ("/api/health", "/api/metrics"):
                self._send_json(200, services.get_system_metrics())
                return

            # 2. Vitrine de Veterinários (Geo-Search + Cache)
            if pathname == "/api/vets":
                modality = query_params.get("modality", "ALL")
                online_now = query_params.get("onlineNow", "false").lower() == "true"
                specialty = query_params.get("specialty", "")
                search = query_params.get("search", "")
                sort_by = query_params.get("sortBy", "RECOMMENDED")
                lat = float(query_params.get("lat", "-23.5615"))
                lng = float(query_params.get("lng", "-46.6858"))

                payload, cache_status = services.search_vets(
                    modality=modality,
                    online_now=online_now,
                    specialty=specialty,
                    search=search,
                    sort_by=sort_by,
                    lat=lat,
                    lng=lng,
                )
                self._send_json(
                    200,
                    payload,
                    {
                        "X-Cache": cache_status,
                        "X-Geo-Cell": payload["meta"]["geoCell"],
                    },
                )
                return

            # 3. Detalhes de Veterinário
            vet_match = re.match(r"^/api/vets/([^/]+)$", pathname)
            if vet_match:
                vet_detail = services.get_vet_detail(vet_match.group(1))
                if not vet_detail:
                    self._send_json(404, {"error": "Veterinário não encontrado"})
                    return
                self._send_json(200, vet_detail)
                return

            # 4. Sessão do Tutor e Pets
            if pathname == "/api/tutor-session":
                self._send_json(200, services.get_tutor_session())
                return

            # 5. Listagem de Solicitações / Pré-Orçamentos
            if pathname == "/api/requests":
                items = services.list_requests(
                    tutor_id=query_params.get("tutorId"),
                    vet_id=query_params.get("vetId"),
                )
                self._send_json(200, {"items": items})
                return

            # 6. Interface Web & Simulador do App Mobile (SSR em Python)
            if pathname in ("/", "/index.html"):
                html_page = ui.render_page(query_params)
                self._send_html(200, html_page)
                return

            self._send_json(404, {"error": f"Rota não encontrada: GET {pathname}"})
        except Exception as exc:  # noqa: BLE001
            self._send_json(500, {"error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        pathname = parsed.path

        try:
            body = self._read_body_data()

            # API JSON: Cadastro de Veterinário
            if pathname == "/api/vets/register":
                created = services.register_vet(body)
                self._send_json(201, created)
                return

            # API JSON: Cadastro de Pet
            if pathname == "/api/pets":
                pet = services.create_pet(body)
                self._send_json(201, pet)
                return

            # API JSON: Criar Solicitação / Pré-Orçamento
            if pathname == "/api/requests":
                created_req = services.create_service_request(body)
                self._send_json(201, created_req)
                return

            # API JSON: Avaliação Pós-Atendimento
            if pathname == "/api/reviews":
                review = services.create_review(body)
                self._send_json(201, review)
                return

            # ------------------------------------------------------------------
            # Rotas de Ação SSR do Site / Simulador App Mobile (/actions/*)
            # ------------------------------------------------------------------
            if pathname == "/actions/create-request":
                created_req = services.create_service_request(body)
                wa_url = created_req["handoff"]["whatsappUrl"]
                target = "/?" + urllib.parse.urlencode(
                    {
                        "section": "REQUESTS",
                        "toast": "Solicitação de pré-orçamento enviada com sucesso!",
                        "handoffWa": wa_url,
                    }
                )
                self._redirect(target)
                return

            if pathname == "/actions/toggle-availability":
                vet_id = str(body.get("vetId") or "")
                services.toggle_vet_availability(vet_id)
                target = "/?" + urllib.parse.urlencode(
                    {
                        "section": "VET_PANEL",
                        "activeVetId": vet_id,
                        "toast": "Status de Plantão atualizado na vitrine em tempo real!",
                    }
                )
                self._redirect(target)
                return

            if pathname == "/actions/request-status":
                req_id = str(body.get("requestId") or "")
                status = str(body.get("status") or "ACCEPTED")
                reais = body.get("agreedPriceReais")
                agreed_cents = int(float(reais) * 100) if reais else None
                services.update_request_status(
                    req_id,
                    {
                        "status": status,
                        "agreedPriceCents": agreed_cents,
                        "vetQuoteNotes": body.get("vetQuoteNotes"),
                    },
                )
                return_sec = str(body.get("returnSection") or "REQUESTS")
                params = {
                    "section": return_sec,
                    "toast": f"Status do pedido atualizado para {status}!",
                }
                if body.get("activeVetId"):
                    params["activeVetId"] = str(body["activeVetId"])
                self._redirect("/?" + urllib.parse.urlencode(params))
                return

            if pathname == "/actions/register-vet":
                payload = {
                    "name": body.get("name"),
                    "crmvNumber": body.get("crmvNumber"),
                    "crmvState": body.get("crmvState", "SP"),
                    "whatsappPhone": body.get("whatsappPhone"),
                    "neighborhood": body.get("neighborhood", "Pinheiros"),
                    "specialties": body.get("specialties", "Clínica Geral"),
                    "modalities": {
                        "CLINIC": {
                            "isActive": True,
                            "basePriceCents": int(float(body.get("priceClinic") or 150) * 100),
                        },
                        "HOME_VISIT": {
                            "isActive": True,
                            "basePriceCents": int(float(body.get("priceHome") or 200) * 100),
                        },
                        "ONLINE": {
                            "isActive": True,
                            "basePriceCents": int(float(body.get("priceOnline") or 90) * 100),
                        },
                    },
                }
                created = services.register_vet(payload)
                vet_id = created["vetProfile"]["id"]
                self._redirect(
                    "/?"
                    + urllib.parse.urlencode(
                        {
                            "section": "VET_PANEL",
                            "activeVetId": vet_id,
                            "toast": f"{created['vetProfile']['name']} cadastrado(a) e publicado(a) na Vitrine!",
                        }
                    )
                )
                return

            if pathname == "/actions/create-review":
                services.create_review(body)
                self._redirect(
                    "/?"
                    + urllib.parse.urlencode(
                        {
                            "section": "REQUESTS",
                            "toast": "Avaliação publicada! Nota média recalculada pelo worker assíncrono.",
                        }
                    )
                )
                return

            self._send_json(404, {"error": f"Rota não encontrada: POST {pathname}"})
        except LookupError as exc:
            self._send_json(404, {"error": str(exc)})
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._send_json(500, {"error": str(exc)})

    def do_PATCH(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        pathname = parsed.path

        try:
            body = self._read_body_data()

            # PATCH /api/vets/<id>/availability
            avail_match = re.match(r"^/api/vets/([^/]+)/availability$", pathname)
            if avail_match:
                res = services.toggle_vet_availability(
                    avail_match.group(1),
                    body.get("isOnlineNow") if isinstance(body.get("isOnlineNow"), bool) else None,
                )
                if not res:
                    self._send_json(404, {"error": "Veterinário não encontrado"})
                    return
                self._send_json(200, res)
                return

            # PATCH /api/requests/<id>/status
            status_match = re.match(r"^/api/requests/([^/]+)/status$", pathname)
            if status_match:
                updated = services.update_request_status(status_match.group(1), body)
                if not updated:
                    self._send_json(404, {"error": "Solicitação não encontrada"})
                    return
                self._send_json(200, updated)
                return

            self._send_json(404, {"error": f"Rota não encontrada: PATCH {pathname}"})
        except Exception as exc:  # noqa: BLE001
            self._send_json(500, {"error": str(exc)})


def create_http_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), ConectaPetRequestHandler)
