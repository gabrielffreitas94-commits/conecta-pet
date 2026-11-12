from datetime import datetime, timedelta, timezone
import threading
from typing import Any, Dict, List
import urllib.parse

from conecta_pet.infra.uuidv7 import uuidv7


def make_svg_avatar(initials: str, bg_hex: str = "#e11d48") -> str:
    """Gera um Avatar SVG Data URI 100% offline para evitar requisições externas."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160">'
        f'<rect width="160" height="160" rx="32" fill="{bg_hex}"/>'
        f'<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" '
        f'font-family="system-ui, sans-serif" font-size="56" font-weight="800">{initials}</text></svg>'
    )
    return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"


TUTOR_DEMO_ID = "01932000-0000-7000-8000-000000000001"
PET_DEMO_DOG_ID = "01932000-0000-7000-8000-000000000101"
PET_DEMO_CAT_ID = "01932000-0000-7000-8000-000000000102"


class ConectaPetRepository:
    """
    Repositório central thread-safe em Python (espelhando o schema PostgreSQL 16).
    Pré-carregado com dados realistas de Tutores, Pets, Veterinários (CRMV), Pedidos e Avaliações.
    """

    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.reset_seed_data()

    def reset_seed_data(self) -> None:
        now = datetime.now(timezone.utc)
        with self.lock:
            self.users: List[Dict[str, Any]] = [
                {
                    "id": TUTOR_DEMO_ID,
                    "role": "TUTOR",
                    "name": "Lucas Mendes",
                    "email": "lucas@exemplo.com",
                    "phone": "5511998765432",
                    "avatarUrl": make_svg_avatar("LM", "#0f172a"),
                    "createdAt": (now - timedelta(days=10)).isoformat(),
                },
                {
                    "id": "01932000-0000-7000-8000-000000000011",
                    "role": "VET",
                    "name": "Dra. Camila Soares",
                    "email": "camila.vet@exemplo.com",
                    "phone": "5511991112222",
                    "avatarUrl": make_svg_avatar("CS", "#e11d48"),
                    "createdAt": (now - timedelta(days=40)).isoformat(),
                },
                {
                    "id": "01932000-0000-7000-8000-000000000012",
                    "role": "VET",
                    "name": "Dr. Rafael Nogueira",
                    "email": "rafael.vet@exemplo.com",
                    "phone": "5511993334444",
                    "avatarUrl": make_svg_avatar("RN", "#0d9488"),
                    "createdAt": (now - timedelta(days=35)).isoformat(),
                },
                {
                    "id": "01932000-0000-7000-8000-000000000013",
                    "role": "VET",
                    "name": "Dra. Juliana Martins",
                    "email": "juliana.vet@exemplo.com",
                    "phone": "5511995556666",
                    "avatarUrl": make_svg_avatar("JM", "#7c3aed"),
                    "createdAt": (now - timedelta(days=28)).isoformat(),
                },
                {
                    "id": "01932000-0000-7000-8000-000000000014",
                    "role": "VET",
                    "name": "Dr. Henrique Costa",
                    "email": "henrique.vet@exemplo.com",
                    "phone": "5511997778888",
                    "avatarUrl": make_svg_avatar("HC", "#2563eb"),
                    "createdAt": (now - timedelta(days=20)).isoformat(),
                },
                {
                    "id": "01932000-0000-7000-8000-000000000015",
                    "role": "VET",
                    "name": "Dra. Beatriz Almeida",
                    "email": "beatriz.vet@exemplo.com",
                    "phone": "5511990001111",
                    "avatarUrl": make_svg_avatar("BA", "#d97706"),
                    "createdAt": (now - timedelta(days=15)).isoformat(),
                },
                {
                    "id": "01932000-0000-7000-8000-000000000016",
                    "role": "VET",
                    "name": "Dr. Marcelo Tavares",
                    "email": "marcelo.vet@exemplo.com",
                    "phone": "5511992223333",
                    "avatarUrl": make_svg_avatar("MT", "#059669"),
                    "createdAt": (now - timedelta(days=12)).isoformat(),
                },
            ]

            self.pets: List[Dict[str, Any]] = [
                {
                    "id": PET_DEMO_DOG_ID,
                    "tutorId": TUTOR_DEMO_ID,
                    "name": "Thor",
                    "species": "DOG",
                    "breed": "Golden Retriever",
                    "ageYears": 3,
                    "weightKg": 31.5,
                    "notes": "Super dócil, alergia leve a picada de pulga.",
                },
                {
                    "id": PET_DEMO_CAT_ID,
                    "tutorId": TUTOR_DEMO_ID,
                    "name": "Luna",
                    "species": "CAT",
                    "breed": "SRD (Siamês)",
                    "ageYears": 2,
                    "weightKg": 4.2,
                    "notes": "Assustada com barulho de carro, prefere atendimento domiciliar ou online.",
                },
            ]

            self.vet_profiles: List[Dict[str, Any]] = [
                {
                    "id": "01932000-0000-7000-8000-000000000201",
                    "userId": "01932000-0000-7000-8000-000000000011",
                    "name": "Dra. Camila Soares",
                    "avatarUrl": make_svg_avatar("CS", "#e11d48"),
                    "crmvNumber": "45892",
                    "crmvState": "SP",
                    "bio": "Especialista em Clínica Médica de Cães e Gatos com 9 anos de experiência. Atendimento humanizado no consultório, em domicílio com kit completo de coleta e teleorientação.",
                    "specialties": ["Clínica Geral", "Dermatologia", "Vacinação"],
                    "isVerified": True,
                    "isOnlineNow": True,
                    "responseTimeMins": 4,
                    "ratingAvg": 4.95,
                    "ratingCount": 142,
                    "whatsappPhone": "5511991112222",
                    "acceptedPaymentMethods": ["PIX", "Cartão de Crédito/Débito (Maquininha)", "Dinheiro"],
                    "city": "São Paulo",
                    "neighborhood": "Pinheiros",
                    "lat": -23.5615,
                    "lng": -46.6858,
                    "modalities": {
                        "CLINIC": {
                            "isActive": True,
                            "basePriceCents": 16000,
                            "clinicAddress": "Rua dos Pinheiros, 840 - Conj. 42, Pinheiros, São Paulo - SP",
                        },
                        "HOME_VISIT": {
                            "isActive": True,
                            "basePriceCents": 21000,
                            "displacementFeeCents": 3500,
                            "coverageRadiusKm": 15,
                        },
                        "ONLINE": {
                            "isActive": True,
                            "basePriceCents": 9500,
                        },
                    },
                    "nextAvailableSlots": [
                        "Agora (Plantão)",
                        "Hoje às 15:30",
                        "Hoje às 17:00",
                        "Amanhã às 09:00",
                    ],
                },
                {
                    "id": "01932000-0000-7000-8000-000000000202",
                    "userId": "01932000-0000-7000-8000-000000000012",
                    "name": "Dr. Rafael Nogueira",
                    "avatarUrl": make_svg_avatar("RN", "#0d9488"),
                    "crmvNumber": "38104",
                    "crmvState": "SP",
                    "bio": "Veterinário volante focado em urgências domiciliares, ortopedia e manejo sem estresse para cães de grande porte. Levo ultrassom portátil e medicação.",
                    "specialties": ["Urgência Domiciliar", "Ortopedia", "Clínica Geral"],
                    "isVerified": True,
                    "isOnlineNow": True,
                    "responseTimeMins": 5,
                    "ratingAvg": 4.91,
                    "ratingCount": 98,
                    "whatsappPhone": "5511993334444",
                    "acceptedPaymentMethods": ["PIX", "Cartão na Maquininha"],
                    "city": "São Paulo",
                    "neighborhood": "Vila Mariana",
                    "lat": -23.5842,
                    "lng": -46.6365,
                    "modalities": {
                        "CLINIC": {"isActive": False, "basePriceCents": 0, "clinicAddress": ""},
                        "HOME_VISIT": {
                            "isActive": True,
                            "basePriceCents": 19500,
                            "displacementFeeCents": 2500,
                            "coverageRadiusKm": 25,
                        },
                        "ONLINE": {"isActive": True, "basePriceCents": 8900},
                    },
                    "nextAvailableSlots": ["Agora (Saída Imediata)", "Hoje às 16:00", "Hoje às 19:30"],
                },
                {
                    "id": "01932000-0000-7000-8000-000000000203",
                    "userId": "01932000-0000-7000-8000-000000000013",
                    "name": "Dra. Juliana Martins",
                    "avatarUrl": make_svg_avatar("JM", "#7c3aed"),
                    "crmvNumber": "51209",
                    "crmvState": "SP",
                    "bio": "Medicina Felina Exclusiva (Cat Friendly). Atendimento calmo e silencioso em domicílio ou no consultório exclusivo para gatos, além de segunda opinião online.",
                    "specialties": ["Medicina Felina", "Comportamento Felino", "Nefrologia"],
                    "isVerified": True,
                    "isOnlineNow": True,
                    "responseTimeMins": 3,
                    "ratingAvg": 4.98,
                    "ratingCount": 215,
                    "whatsappPhone": "5511995556666",
                    "acceptedPaymentMethods": ["PIX", "Cartão em até 3x sem juros"],
                    "city": "São Paulo",
                    "neighborhood": "Moema",
                    "lat": -23.5991,
                    "lng": -46.6612,
                    "modalities": {
                        "CLINIC": {
                            "isActive": True,
                            "basePriceCents": 18500,
                            "clinicAddress": "Al. dos Nhambiquaras, 1120 - Moema, São Paulo - SP",
                        },
                        "HOME_VISIT": {
                            "isActive": True,
                            "basePriceCents": 23000,
                            "displacementFeeCents": 3000,
                            "coverageRadiusKm": 18,
                        },
                        "ONLINE": {"isActive": True, "basePriceCents": 11000},
                    },
                    "nextAvailableSlots": ["Agora (Online)", "Hoje às 14:30", "Amanhã às 10:00"],
                },
                {
                    "id": "01932000-0000-7000-8000-000000000204",
                    "userId": "01932000-0000-7000-8000-000000000014",
                    "name": "Dr. Henrique Costa",
                    "avatarUrl": make_svg_avatar("HC", "#2563eb"),
                    "crmvNumber": "29440",
                    "crmvState": "SP",
                    "bio": "Especialista em Animais Silvestres e Exóticos (Aves, Coelhos, Répteis e Roedores). Consultório equipado e teleorientação nutricional e de manejo.",
                    "specialties": ["Pets Exóticos e Silvestres", "Clínica Geral", "Nutrição Pet"],
                    "isVerified": True,
                    "isOnlineNow": False,
                    "responseTimeMins": 15,
                    "ratingAvg": 4.89,
                    "ratingCount": 76,
                    "whatsappPhone": "5511997778888",
                    "acceptedPaymentMethods": ["PIX", "Cartão na Maquininha", "Dinheiro"],
                    "city": "São Paulo",
                    "neighborhood": "Perdizes",
                    "lat": -23.5362,
                    "lng": -46.6744,
                    "modalities": {
                        "CLINIC": {
                            "isActive": True,
                            "basePriceCents": 17500,
                            "clinicAddress": "Rua Cardoso de Almeida, 620 - Perdizes, São Paulo - SP",
                        },
                        "HOME_VISIT": {
                            "isActive": True,
                            "basePriceCents": 24000,
                            "displacementFeeCents": 4000,
                            "coverageRadiusKm": 12,
                        },
                        "ONLINE": {"isActive": True, "basePriceCents": 9900},
                    },
                    "nextAvailableSlots": ["Hoje às 18:00", "Amanhã às 09:30", "Amanhã às 14:00"],
                },
                {
                    "id": "01932000-0000-7000-8000-000000000205",
                    "userId": "01932000-0000-7000-8000-000000000015",
                    "name": "Dra. Beatriz Almeida",
                    "avatarUrl": make_svg_avatar("BA", "#d97706"),
                    "crmvNumber": "60112",
                    "crmvState": "SP",
                    "bio": "Plantão de Telemedicina Veterinária e Triagem Rápida. Avalio exames laboratoriais, dúvidas de medicação, alergias de pele e orientação de emergência 24h.",
                    "specialties": ["Telemedicina & Triagem", "Dermatologia", "Gastroenterologia"],
                    "isVerified": True,
                    "isOnlineNow": True,
                    "responseTimeMins": 2,
                    "ratingAvg": 4.94,
                    "ratingCount": 310,
                    "whatsappPhone": "5511990001111",
                    "acceptedPaymentMethods": ["PIX", "Link de Cartão"],
                    "city": "São Paulo",
                    "neighborhood": "Itaim Bibi",
                    "lat": -23.5839,
                    "lng": -46.6784,
                    "modalities": {
                        "CLINIC": {"isActive": False, "basePriceCents": 0, "clinicAddress": ""},
                        "HOME_VISIT": {
                            "isActive": False,
                            "basePriceCents": 0,
                            "displacementFeeCents": 0,
                            "coverageRadiusKm": 0,
                        },
                        "ONLINE": {"isActive": True, "basePriceCents": 7500},
                    },
                    "nextAvailableSlots": ["Agora (Em até 5 min)", "Hoje às 15:00", "Hoje às 20:00"],
                },
                {
                    "id": "01932000-0000-7000-8000-000000000206",
                    "userId": "01932000-0000-7000-8000-000000000016",
                    "name": "Dr. Marcelo Tavares",
                    "avatarUrl": make_svg_avatar("MT", "#059669"),
                    "crmvNumber": "33918",
                    "crmvState": "SP",
                    "bio": "Cardiologia, Check-up Geriátrico e Vacinação Importada (V10, Raiva, Giárdia). Consultório completo com estacionamento e visitas agendadas.",
                    "specialties": ["Cardiologia", "Geriatria Pet", "Vacinação"],
                    "isVerified": True,
                    "isOnlineNow": False,
                    "responseTimeMins": 12,
                    "ratingAvg": 4.87,
                    "ratingCount": 64,
                    "whatsappPhone": "5511992223333",
                    "acceptedPaymentMethods": ["PIX", "Cartão na Maquininha", "Dinheiro"],
                    "city": "São Paulo",
                    "neighborhood": "Tatuapé",
                    "lat": -23.5401,
                    "lng": -46.5766,
                    "modalities": {
                        "CLINIC": {
                            "isActive": True,
                            "basePriceCents": 15000,
                            "clinicAddress": "Rua Coelho Lisboa, 450 - Tatuapé, São Paulo - SP",
                        },
                        "HOME_VISIT": {
                            "isActive": True,
                            "basePriceCents": 19000,
                            "displacementFeeCents": 2000,
                            "coverageRadiusKm": 20,
                        },
                        "ONLINE": {"isActive": True, "basePriceCents": 8500},
                    },
                    "nextAvailableSlots": ["Hoje às 16:30", "Amanhã às 08:30", "Amanhã às 11:00"],
                },
            ]

            self.service_requests: List[Dict[str, Any]] = [
                {
                    "id": "01932000-0000-7000-8000-000000000501",
                    "tutorId": TUTOR_DEMO_ID,
                    "tutorName": "Lucas Mendes",
                    "tutorPhone": "5511998765432",
                    "petId": PET_DEMO_DOG_ID,
                    "petName": "Thor",
                    "petSpecies": "DOG",
                    "vetId": "01932000-0000-7000-8000-000000000201",
                    "vetName": "Dra. Camila Soares",
                    "vetCrmv": "CRMV-SP 45892",
                    "vetWhatsapp": "5511991112222",
                    "modality": "HOME_VISIT",
                    "urgencyType": "IMMEDIATE",
                    "scheduledFor": "Agora (Plantão Domiciliar)",
                    "status": "ACCEPTED",
                    "symptomsDescription": "Thor está coçando bastante a orelha direita desde ontem e balançando a cabeça. Gostaria de consulta domiciliar + avaliação.",
                    "tutorAddress": "Rua Fradique Coutinho, 500 - Pinheiros, São Paulo - SP",
                    "estimatedPriceCents": 24500,
                    "agreedPriceCents": 24500,
                    "vetQuoteNotes": "Confirmado, Lucas! Estou a 1,2 km de você. Levo otoscópio e medicação tópica caso precise. Pagamento via PIX ou maquininha no local.",
                    "externalMeetingLink": None,
                    "hasReview": False,
                    "createdAt": (now - timedelta(minutes=35)).isoformat(),
                    "updatedAt": (now - timedelta(minutes=28)).isoformat(),
                }
            ]

            self.reviews: List[Dict[str, Any]] = [
                {
                    "id": uuidv7(),
                    "serviceRequestId": "01932000-0000-7000-8000-000000000499",
                    "tutorId": TUTOR_DEMO_ID,
                    "tutorName": "Mariana Costa",
                    "vetId": "01932000-0000-7000-8000-000000000201",
                    "rating": 5,
                    "comment": "A Dra. Camila chegou super rápido em casa, examinou meu cão com muita paciência e o preço foi exatamente o combinado!",
                    "createdAt": (now - timedelta(days=3)).isoformat(),
                },
                {
                    "id": uuidv7(),
                    "serviceRequestId": "01932000-0000-7000-8000-000000000498",
                    "tutorId": TUTOR_DEMO_ID,
                    "tutorName": "Pedro Henrique",
                    "vetId": "01932000-0000-7000-8000-000000000203",
                    "rating": 5,
                    "comment": "Minha gata sempre ficava estressada em clínicas comuns. A visita da Dra. Juliana foi impecável.",
                    "createdAt": (now - timedelta(days=5)).isoformat(),
                },
            ]


db = ConectaPetRepository()
