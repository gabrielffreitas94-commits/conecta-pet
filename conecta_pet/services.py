import copy
from datetime import datetime, timezone
import random
import re
from typing import Any, Dict, List, Optional, Tuple
import urllib.parse

from conecta_pet.db.repository import db, make_svg_avatar
from conecta_pet.infra.cache import cache
from conecta_pet.infra.geo import calculate_distance_km, get_geo_cell_key
from conecta_pet.infra.queue import job_queue
from conecta_pet.infra.uuidv7 import uuidv7

INSTANCE_ID = f"py-api-node-{uuidv7()[:8]}"


# ============================================================================
# REGISTRO DE WORKERS ASSÍNCRONOS (Padrão Grande Escala)
# ============================================================================

def _worker_recalculate_vet_rating(payload: Dict[str, Any]) -> None:
    vet_id = payload.get("vetId")
    new_rating = float(payload.get("newRating", 5.0))
    with db.lock:
        vet = next((v for v in db.vet_profiles if v["id"] == vet_id), None)
        if not vet:
            return
        old_total = float(vet["ratingAvg"]) * int(vet["ratingCount"])
        vet["ratingCount"] = int(vet["ratingCount"]) + 1
        vet["ratingAvg"] = round((old_total + new_rating) / vet["ratingCount"], 2)
    cache.invalidate_prefix("catalog:")


def _worker_notify_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"delivered": True, **payload}


job_queue.register_worker("RECALCULATE_VET_RATING", _worker_recalculate_vet_rating)
job_queue.register_worker("NOTIFY_EVENT", _worker_notify_event)


def build_whatsapp_url(phone: str, text: str) -> str:
    clean_phone = re.sub(r"\D", "", str(phone or ""))
    return f"https://wa.me/{clean_phone}?text={urllib.parse.quote(text)}"


# ============================================================================
# SERVIÇOS DE DOMÍNIO
# ============================================================================

def get_system_metrics() -> Dict[str, Any]:
    with db.lock:
        return {
            "status": "healthy",
            "instanceId": INSTANCE_ID,
            "runtime": "Python 3 (Stateless Modular Architecture)",
            "architecture": {
                "pattern": "Stateless Modular Monolith (Microservices-Ready)",
                "database": "PostgreSQL 16 (UUIDv7 + Spatial Coordinates Index)",
                "cacheLayer": "Thread-Safe Geo-Cell TTL Cache (Redis-compatible)",
                "asyncQueue": "Event-Driven Background Worker Queue",
                "monetizationModel": "100% Free for Tutors & Vets (Direct Payment, Future Ads)",
            },
            "cacheMetrics": cache.get_metrics(),
            "queueMetrics": job_queue.get_metrics(),
            "counts": {
                "vets": len(db.vet_profiles),
                "onlineVets": sum(1 for v in db.vet_profiles if v.get("isOnlineNow")),
                "tutors": sum(1 for u in db.users if u.get("role") == "TUTOR"),
                "pets": len(db.pets),
                "serviceRequests": len(db.service_requests),
                "reviews": len(db.reviews),
            },
        }


def search_vets(
    modality: str = "ALL",
    online_now: bool = False,
    specialty: str = "",
    search: str = "",
    sort_by: str = "RECOMMENDED",
    lat: float = -23.5615,
    lng: float = -46.6858,
) -> Tuple[Dict[str, Any], str]:
    modality = (modality or "ALL").upper()
    specialty_clean = (specialty or "").strip()
    if specialty_clean.lower() == "todas":
        specialty_clean = ""
    search_clean = (search or "").strip().lower()
    sort_by = (sort_by or "RECOMMENDED").upper()

    geo_cell = get_geo_cell_key(lat, lng, precision=2)
    cache_key = f"catalog:{geo_cell}:{modality}:{online_now}:{specialty_clean.lower()}:{search_clean}:{sort_by}"

    cached = cache.get(cache_key)
    if cached is not None:
        return copy.deepcopy(cached), "HIT"

    with db.lock:
        raw_vets = copy.deepcopy(db.vet_profiles)

    enriched: List[Dict[str, Any]] = []
    for vet in raw_vets:
        dist_km = calculate_distance_km(lat, lng, vet.get("lat"), vet.get("lng"))
        modalities_cfg = vet.get("modalities", {})
        active_modalities = [
            mod_key for mod_key, cfg in modalities_cfg.items() if cfg and cfg.get("isActive")
        ]

        if modality != "ALL" and modalities_cfg.get(modality, {}).get("isActive"):
            display_price = int(modalities_cfg[modality].get("basePriceCents", 0))
        else:
            prices = [
                int(modalities_cfg[m].get("basePriceCents", 0))
                for m in active_modalities
                if int(modalities_cfg[m].get("basePriceCents", 0)) > 0
            ]
            display_price = min(prices) if prices else 0

        home_cfg = modalities_cfg.get("HOME_VISIT", {})
        covers_home_visit = bool(
            home_cfg.get("isActive")
            and (dist_km is None or dist_km <= float(home_cfg.get("coverageRadiusKm", 15)))
        )

        vet_item = {
            **vet,
            "distanceKm": dist_km,
            "activeModalities": active_modalities,
            "displayPriceCents": display_price,
            "coversHomeVisitAtLocation": covers_home_visit,
        }

        # Filtros
        if modality != "ALL":
            if not modalities_cfg.get(modality, {}).get("isActive"):
                continue
            if modality == "HOME_VISIT" and not covers_home_visit:
                continue

        if online_now and not vet_item.get("isOnlineNow"):
            continue

        if specialty_clean:
            if not any(
                specialty_clean.lower() in s.lower() for s in vet_item.get("specialties", [])
            ):
                continue

        if search_clean:
            haystack = " ".join(
                [
                    str(vet_item.get("name", "")),
                    str(vet_item.get("neighborhood", "")),
                    str(vet_item.get("city", "")),
                    str(vet_item.get("crmvNumber", "")),
                    " ".join(vet_item.get("specialties", [])),
                    str(vet_item.get("bio", "")),
                ]
            ).lower()
            if search_clean not in haystack:
                continue

        enriched.append(vet_item)

    # Ordenação estilo iFood
    if sort_by == "PRICE_ASC":
        enriched.sort(key=lambda v: v["displayPriceCents"])
    elif sort_by == "DISTANCE":
        enriched.sort(key=lambda v: v["distanceKm"] if v["distanceKm"] is not None else 999.0)
    elif sort_by == "RATING_DESC":
        enriched.sort(key=lambda v: float(v["ratingAvg"]), reverse=True)
    else:
        # RECOMMENDED: Plantão Ativo primeiro, depois Score (Nota * 20 - Distância)
        enriched.sort(
            key=lambda v: (
                1 if v.get("isOnlineNow") else 0,
                float(v.get("ratingAvg", 5.0)) * 20.0 - float(v.get("distanceKm") or 5.0),
            ),
            reverse=True,
        )

    payload = {
        "meta": {
            "total": len(enriched),
            "geoCell": geo_cell,
            "tutorCoordinates": {"lat": lat, "lng": lng},
            "filtersApplied": {
                "modality": modality,
                "onlineNow": online_now,
                "specialty": specialty_clean,
                "search": search_clean,
                "sortBy": sort_by,
            },
        },
        "items": enriched,
    }

    cache.set(cache_key, payload, ttl_seconds=30.0)
    return copy.deepcopy(payload), "MISS"


def get_vet_detail(vet_id: str) -> Optional[Dict[str, Any]]:
    with db.lock:
        vet = next((copy.deepcopy(v) for v in db.vet_profiles if v["id"] == vet_id), None)
        if not vet:
            return None
        reviews = [copy.deepcopy(r) for r in db.reviews if r["vetId"] == vet_id]
        return {**vet, "reviews": reviews}


def register_vet(data: Dict[str, Any]) -> Dict[str, Any]:
    name = str(data.get("name") or "").strip()
    crmv_number = str(data.get("crmvNumber") or "").strip()
    whatsapp_phone = re.sub(r"\D", "", str(data.get("whatsappPhone") or ""))

    if not name or not crmv_number or not whatsapp_phone:
        raise ValueError("Campos obrigatórios: Nome, Número do CRMV e WhatsApp.")

    user_id = uuidv7()
    vet_id = uuidv7()
    initials = "".join(part[0].upper() for part in name.split()[:2] if part) or "VT"
    avatar_url = data.get("avatarUrl") or make_svg_avatar(initials, "#0d9488")
    crmv_state = str(data.get("crmvState") or "SP").strip().upper()[:2]
    city = str(data.get("city") or "São Paulo").strip()
    neighborhood = str(data.get("neighborhood") or "Pinheiros").strip()

    raw_specs = data.get("specialties")
    if isinstance(raw_specs, str):
        specialties = [s.strip() for s in raw_specs.split(",") if s.strip()]
    elif isinstance(raw_specs, list) and raw_specs:
        specialties = [str(s).strip() for s in raw_specs if str(s).strip()]
    else:
        specialties = ["Clínica Geral"]

    mod_in = data.get("modalities") or {}
    clinic_in = mod_in.get("CLINIC") or {}
    home_in = mod_in.get("HOME_VISIT") or {}
    online_in = mod_in.get("ONLINE") or {}

    new_user = {
        "id": user_id,
        "role": "VET",
        "name": name,
        "email": data.get("email") or f"{user_id[:8]}@conectapet.vet",
        "phone": whatsapp_phone,
        "avatarUrl": avatar_url,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    new_vet = {
        "id": vet_id,
        "userId": user_id,
        "name": name,
        "avatarUrl": avatar_url,
        "crmvNumber": crmv_number,
        "crmvState": crmv_state,
        "bio": str(
            data.get("bio")
            or "Médico(a) Veterinário(a) parceiro(a) do Conecta Pet. Atendimento dedicado e transparente."
        ),
        "specialties": specialties,
        "isVerified": True,
        "isOnlineNow": True,
        "responseTimeMins": 5,
        "ratingAvg": 5.0,
        "ratingCount": 1,
        "whatsappPhone": whatsapp_phone,
        "acceptedPaymentMethods": data.get("acceptedPaymentMethods")
        or ["PIX", "Cartão na Maquininha", "Dinheiro"],
        "city": city,
        "neighborhood": neighborhood,
        "lat": float(data.get("lat", -23.5615 + (random.random() - 0.5) * 0.03)),
        "lng": float(data.get("lng", -46.6858 + (random.random() - 0.5) * 0.03)),
        "modalities": {
            "CLINIC": {
                "isActive": bool(clinic_in.get("isActive", True)),
                "basePriceCents": int(clinic_in.get("basePriceCents", 15000)),
                "clinicAddress": str(
                    clinic_in.get("clinicAddress") or f"{neighborhood}, {city} - {crmv_state}"
                ),
            },
            "HOME_VISIT": {
                "isActive": bool(home_in.get("isActive", True)),
                "basePriceCents": int(home_in.get("basePriceCents", 20000)),
                "displacementFeeCents": int(home_in.get("displacementFeeCents", 3000)),
                "coverageRadiusKm": int(home_in.get("coverageRadiusKm", 15)),
            },
            "ONLINE": {
                "isActive": bool(online_in.get("isActive", True)),
                "basePriceCents": int(online_in.get("basePriceCents", 9000)),
            },
        },
        "nextAvailableSlots": ["Agora (Plantão)", "Hoje às 16:00", "Amanhã às 10:00"],
    }

    with db.lock:
        db.users.append(new_user)
        db.vet_profiles.insert(0, new_vet)

    cache.invalidate_prefix("catalog:")
    job_queue.enqueue(
        "NOTIFY_EVENT",
        {
            "summary": f"Novo veterinário cadastrado: {new_vet['name']} (CRMV-{crmv_state} {crmv_number})"
        },
    )

    return {"user": new_user, "vetProfile": new_vet}


def toggle_vet_availability(vet_id: str, is_online_now: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    with db.lock:
        vet = next((v for v in db.vet_profiles if v["id"] == vet_id), None)
        if not vet:
            return None
        if isinstance(is_online_now, bool):
            vet["isOnlineNow"] = is_online_now
        else:
            vet["isOnlineNow"] = not bool(vet.get("isOnlineNow"))
        result = {
            "id": vet["id"],
            "name": vet["name"],
            "isOnlineNow": vet["isOnlineNow"],
        }

    cache.invalidate_prefix("catalog:")
    job_queue.enqueue(
        "NOTIFY_EVENT",
        {
            "summary": f"Plantão de {result['name']} alterado para {'ONLINE' if result['isOnlineNow'] else 'OFFLINE'}"
        },
    )
    return result


def get_tutor_session() -> Dict[str, Any]:
    with db.lock:
        tutor = next((copy.deepcopy(u) for u in db.users if u["role"] == "TUTOR"), None)
        pets = [copy.deepcopy(p) for p in db.pets if tutor and p["tutorId"] == tutor["id"]]
        return {"tutor": tutor, "pets": pets}


def create_pet(data: Dict[str, Any]) -> Dict[str, Any]:
    name = str(data.get("name") or "").strip()
    if not name:
        raise ValueError("Informe o nome do pet.")

    with db.lock:
        tutor = next((u for u in db.users if u["role"] == "TUTOR"), db.users[0])
        new_pet = {
            "id": uuidv7(),
            "tutorId": tutor["id"],
            "name": name,
            "species": str(data.get("species") or "DOG").upper(),
            "breed": str(data.get("breed") or "SRD (Sem Raça Definida)"),
            "ageYears": float(data.get("ageYears") or 1.0),
            "weightKg": float(data.get("weightKg") or 8.0),
            "notes": str(data.get("notes") or ""),
        }
        db.pets.append(new_pet)
        return copy.deepcopy(new_pet)


def list_requests(tutor_id: Optional[str] = None, vet_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with db.lock:
        items = copy.deepcopy(db.service_requests)
    if tutor_id:
        items = [r for r in items if r["tutorId"] == tutor_id]
    if vet_id:
        items = [r for r in items if r["vetId"] == vet_id]
    items.sort(key=lambda r: r.get("createdAt", ""), reverse=True)
    return items


def create_service_request(data: Dict[str, Any]) -> Dict[str, Any]:
    vet_id = str(data.get("vetId") or "")
    modality = str(data.get("modality") or "HOME_VISIT").upper()

    with db.lock:
        vet = next((v for v in db.vet_profiles if v["id"] == vet_id), None)
        if not vet:
            raise LookupError("Veterinário não encontrado.")

        mod_cfg = vet.get("modalities", {}).get(modality)
        if not mod_cfg or not mod_cfg.get("isActive"):
            raise ValueError("Esta modalidade não está ativa para este veterinário.")

        tutor = next((u for u in db.users if u["role"] == "TUTOR"), db.users[0])
        pet_id = data.get("petId")
        pet = next((p for p in db.pets if p["id"] == pet_id), None)

        new_pet_name = str(data.get("newPetName") or "").strip()
        if not pet and new_pet_name:
            pet = {
                "id": uuidv7(),
                "tutorId": tutor["id"],
                "name": new_pet_name,
                "species": str(data.get("newPetSpecies") or "DOG").upper(),
                "breed": str(data.get("newPetBreed") or "SRD"),
                "ageYears": 2,
                "weightKg": 10.0,
                "notes": "",
            }
            db.pets.append(pet)
        elif not pet:
            pet = db.pets[0]

        estimated_cents = int(mod_cfg.get("basePriceCents", 0)) + (
            int(mod_cfg.get("displacementFeeCents", 0)) if modality == "HOME_VISIT" else 0
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        scheduled_for = str(data.get("scheduledFor") or "Agora (Atendimento Imediato)")
        symptoms = str(
            data.get("symptomsDescription")
            or "Gostaria de realizar uma avaliação veterinária para meu pet."
        ).strip()

        if modality == "HOME_VISIT":
            tutor_address = str(
                data.get("tutorAddress") or "Rua Fradique Coutinho, 500 - Pinheiros, São Paulo - SP"
            )
        elif modality == "CLINIC":
            tutor_address = str(mod_cfg.get("clinicAddress") or vet.get("neighborhood", ""))
        else:
            tutor_address = "Atendimento Online (Telemedicina)"

        new_req = {
            "id": uuidv7(),
            "tutorId": tutor["id"],
            "tutorName": tutor["name"],
            "tutorPhone": tutor["phone"],
            "petId": pet["id"],
            "petName": pet["name"],
            "petSpecies": pet["species"],
            "vetId": vet["id"],
            "vetName": vet["name"],
            "vetCrmv": f"CRMV-{vet['crmvState']} {vet['crmvNumber']}",
            "vetWhatsapp": vet["whatsappPhone"],
            "modality": modality,
            "urgencyType": str(data.get("urgencyType") or "IMMEDIATE"),
            "scheduledFor": scheduled_for,
            "status": "PENDING_QUOTE",
            "symptomsDescription": symptoms,
            "tutorAddress": tutor_address,
            "estimatedPriceCents": estimated_cents,
            "agreedPriceCents": None,
            "vetQuoteNotes": None,
            "externalMeetingLink": None,
            "hasReview": False,
            "createdAt": now_iso,
            "updatedAt": now_iso,
        }
        db.service_requests.insert(0, new_req)

    modality_pt = (
        "Visita Domiciliar"
        if modality == "HOME_VISIT"
        else "Consulta no Consultório"
        if modality == "CLINIC"
        else "Consulta Online"
    )
    whatsapp_text = (
        f"Olá {new_req['vetName']}! Vi seu perfil no *Conecta Pet* e enviei uma solicitação de "
        f"atendimento ({modality_pt}) para meu pet *{new_req['petName']}* ({scheduled_for}).\n\n"
        f"Sintomas/Motivo: {symptoms}\n\n"
        f"Podemos confirmar disponibilidade e o pagamento direto?"
    )

    job_queue.enqueue(
        "NOTIFY_EVENT",
        {
            "requestId": new_req["id"],
            "summary": f"Novo pedido ({modality}) de {new_req['tutorName']} (Pet: {new_req['petName']}) para {new_req['vetName']}",
        },
    )

    return {
        "request": copy.deepcopy(new_req),
        "handoff": {
            "whatsappUrl": build_whatsapp_url(new_req["vetWhatsapp"], whatsapp_text),
            "paymentInfo": "Pagamento 100% direto ao veterinário (Zero taxas no app)",
        },
    }


def update_request_status(req_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with db.lock:
        req = next((r for r in db.service_requests if r["id"] == req_id), None)
        if not req:
            return None

        if data.get("status"):
            req["status"] = str(data["status"]).upper()

        if data.get("agreedPriceCents") is not None:
            req["agreedPriceCents"] = int(data["agreedPriceCents"])
        elif req["status"] == "ACCEPTED" and not req.get("agreedPriceCents"):
            req["agreedPriceCents"] = req["estimatedPriceCents"]

        if "vetQuoteNotes" in data and data["vetQuoteNotes"] is not None:
            req["vetQuoteNotes"] = str(data["vetQuoteNotes"])

        if "externalMeetingLink" in data and data["externalMeetingLink"] is not None:
            req["externalMeetingLink"] = str(data["externalMeetingLink"])

        if (
            req["modality"] == "ONLINE"
            and req["status"] == "ACCEPTED"
            and not req.get("externalMeetingLink")
        ):
            req["externalMeetingLink"] = f"https://meet.google.com/pet-{req['id'][:4]}-{req['id'][4:8]}"

        req["updatedAt"] = datetime.now(timezone.utc).isoformat()
        updated = copy.deepcopy(req)

    job_queue.enqueue(
        "NOTIFY_EVENT",
        {
            "summary": f"Pedido #{updated['id'][-6:]} atualizado para {updated['status']} por {updated['vetName']}"
        },
    )
    return updated


def create_review(data: Dict[str, Any]) -> Dict[str, Any]:
    req_id = str(data.get("serviceRequestId") or "")
    rating = max(1, min(5, int(data.get("rating") or 5)))
    comment = str(data.get("comment") or "Ótimo atendimento!").strip()

    with db.lock:
        req = next((r for r in db.service_requests if r["id"] == req_id), None)
        if not req:
            raise LookupError("Solicitação de atendimento não encontrada.")
        if req.get("hasReview"):
            raise ValueError("Este atendimento já foi avaliado.")

        review = {
            "id": uuidv7(),
            "serviceRequestId": req["id"],
            "tutorId": req["tutorId"],
            "tutorName": req["tutorName"],
            "vetId": req["vetId"],
            "rating": rating,
            "comment": comment,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        db.reviews.insert(0, review)
        req["hasReview"] = True
        vet_id = req["vetId"]
        vet_name = req["vetName"]

    job_queue.enqueue(
        "RECALCULATE_VET_RATING",
        {
            "vetId": vet_id,
            "newRating": rating,
            "summary": f"Recálculo assíncrono de nota média para {vet_name} (+{rating}★)",
        },
    )
    return copy.deepcopy(review)
