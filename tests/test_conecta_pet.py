import json
import threading
import unittest
import urllib.request

from conecta_pet.db.repository import db
from conecta_pet.infra.cache import cache
from conecta_pet.infra.uuidv7 import uuidv7
from conecta_pet.server import create_http_server


class TestConectaPetPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_http_server(host="127.0.0.1", port=0)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self) -> None:
        db.reset_seed_data()
        cache.invalidate_prefix("")

    def _request_json(self, method: str, path: str, body: dict | None = None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        with urllib.request.urlopen(req) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return resp.status, dict(resp.headers), payload

    def test_1_uuidv7_is_time_ordered_and_valid(self) -> None:
        u1 = uuidv7()
        u2 = uuidv7()
        self.assertEqual(len(u1), 36)
        self.assertEqual(u1[14], "7")
        self.assertTrue(u2 >= u1[:13])

    def test_2_metrics_and_health_endpoint(self) -> None:
        status, _, data = self._request_json("GET", "/api/metrics")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "healthy")
        self.assertGreaterEqual(data["counts"]["vets"], 6)

    def test_3_geo_search_and_cache_miss_to_hit(self) -> None:
        status1, headers1, data1 = self._request_json(
            "GET", "/api/vets?modality=HOME_VISIT&lat=-23.561&lng=-46.681"
        )
        self.assertEqual(status1, 200)
        self.assertEqual(headers1.get("X-Cache"), "MISS")
        self.assertGreater(len(data1["items"]), 0)
        self.assertIsInstance(data1["items"][0]["distanceKm"], float)

        # Segunda chamada dentro da mesma célula geográfica deve retornar HIT
        status2, headers2, _ = self._request_json(
            "GET", "/api/vets?modality=HOME_VISIT&lat=-23.562&lng=-46.682"
        )
        self.assertEqual(status2, 200)
        self.assertEqual(headers2.get("X-Cache"), "HIT")

    def test_4_register_vet_and_toggle_availability(self) -> None:
        status, _, created = self._request_json(
            "POST",
            "/api/vets/register",
            {
                "name": "Dr. Bruno Cavalcanti",
                "crmvNumber": "77412",
                "crmvState": "SP",
                "whatsappPhone": "5511988887777",
                "city": "São Paulo",
                "neighborhood": "Vila Madalena",
                "specialties": ["Clínica Geral", "Cardiologia"],
            },
        )
        self.assertEqual(status, 201)
        vet_id = created["vetProfile"]["id"]
        self.assertTrue(created["vetProfile"]["isOnlineNow"])

        # Alterna status do plantão
        st_patch, _, patched = self._request_json(
            "PATCH", f"/api/vets/{vet_id}/availability", {}
        )
        self.assertEqual(st_patch, 200)
        self.assertFalse(patched["isOnlineNow"])

    def test_5_full_service_request_quote_and_review_flow(self) -> None:
        _, _, vets_data = self._request_json("GET", "/api/vets")
        target_vet = vets_data["items"][0]

        # 1. Tutor solicita pré-orçamento de Consulta Online
        st_req, _, req_payload = self._request_json(
            "POST",
            "/api/requests",
            {
                "vetId": target_vet["id"],
                "modality": "ONLINE",
                "urgencyType": "IMMEDIATE",
                "scheduledFor": "Agora (Plantão Online)",
                "symptomsDescription": "Meu gato está espirrando desde cedo.",
                "newPetName": "Simba",
                "newPetSpecies": "CAT",
            },
        )
        self.assertEqual(st_req, 201)
        req_id = req_payload["request"]["id"]
        self.assertEqual(req_payload["request"]["status"], "PENDING_QUOTE")
        self.assertIn("https://wa.me/", req_payload["handoff"]["whatsappUrl"])

        # 2. Veterinário confirma orçamento e aceita o pedido
        st_acc, _, accepted = self._request_json(
            "PATCH",
            f"/api/requests/{req_id}/status",
            {
                "status": "ACCEPTED",
                "agreedPriceCents": 9500,
                "vetQuoteNotes": "Confirmado! Segue o link da videochamada.",
            },
        )
        self.assertEqual(st_acc, 200)
        self.assertEqual(accepted["status"], "ACCEPTED")
        self.assertTrue(accepted["externalMeetingLink"].startswith("https://meet.google.com/"))

        # 3. Conclui atendimento e envia avaliação 5 estrelas
        self._request_json(
            "PATCH", f"/api/requests/{req_id}/status", {"status": "COMPLETED"}
        )
        st_rev, _, review = self._request_json(
            "POST",
            "/api/reviews",
            {
                "serviceRequestId": req_id,
                "rating": 5,
                "comment": "Atendimento excelente e super rápido!",
            },
        )
        self.assertEqual(st_rev, 201)
        self.assertEqual(review["rating"], 5)

    def test_6_web_ui_and_mobile_simulator_ssr_render(self) -> None:
        with urllib.request.urlopen(f"{self.base_url}/?device=MOBILE_APP&section=VITRINE") as resp:
            html_body = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("Conecta", html_body)
            self.assertIn("Dra. Camila Soares", html_body)
            self.assertIn("Simulador Interativo do App Mobile", html_body)


if __name__ == "__main__":
    unittest.main()
