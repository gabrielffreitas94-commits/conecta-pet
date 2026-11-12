-- =============================================================================
-- CONECTA PET - Arquitetura de Banco de Dados para Grande Escala (Python Backend)
-- Compatível com PostgreSQL 16 (Ubuntu 24.04) e PostGIS opcional
-- =============================================================================

-- 1. Tabela de Usuários (Tutores, Veterinários e Admins)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY, -- UUIDv7 (Time-ordered para alta performance em B-Tree)
    role VARCHAR(16) NOT NULL CHECK (role IN ('TUTOR', 'VET', 'ADMIN')),
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) UNIQUE,
    phone VARCHAR(32) NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- 2. Tabela de Pets (Vinculados ao Tutor)
CREATE TABLE IF NOT EXISTS pets (
    id UUID PRIMARY KEY,
    tutor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(80) NOT NULL,
    species VARCHAR(24) NOT NULL CHECK (species IN ('DOG', 'CAT', 'EXOTIC', 'OTHER')),
    breed VARCHAR(80),
    age_years NUMERIC(4,1),
    weight_kg NUMERIC(5,2),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pets_tutor_id ON pets(tutor_id);

-- 3. Perfis Profissionais de Veterinários
CREATE TABLE IF NOT EXISTS vet_profiles (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    crmv_number VARCHAR(32) NOT NULL,
    crmv_state CHAR(2) NOT NULL,
    bio TEXT,
    specialties TEXT[] NOT NULL DEFAULT '{}',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_online_now BOOLEAN NOT NULL DEFAULT FALSE,
    response_time_mins INTEGER NOT NULL DEFAULT 10,
    rating_avg NUMERIC(3,2) NOT NULL DEFAULT 5.00,
    rating_count INTEGER NOT NULL DEFAULT 0,
    whatsapp_phone VARCHAR(32) NOT NULL,
    accepted_payment_methods TEXT[] NOT NULL DEFAULT ARRAY['PIX', 'Cartão na Maquininha', 'Dinheiro'],
    city VARCHAR(80) NOT NULL,
    neighborhood VARCHAR(80) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (crmv_number, crmv_state)
);

CREATE INDEX IF NOT EXISTS idx_vet_profiles_coords ON vet_profiles (lat, lng);
CREATE INDEX IF NOT EXISTS idx_vet_profiles_online_rating ON vet_profiles (is_online_now DESC, rating_avg DESC);

-- 4. Modalidades e Preços por Veterinário (Consultório, Domicílio, Online)
CREATE TABLE IF NOT EXISTS vet_service_modalities (
    id UUID PRIMARY KEY,
    vet_id UUID NOT NULL REFERENCES vet_profiles(id) ON DELETE CASCADE,
    modality VARCHAR(20) NOT NULL CHECK (modality IN ('CLINIC', 'HOME_VISIT', 'ONLINE')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    base_price_cents INTEGER NOT NULL CHECK (base_price_cents >= 0),
    displacement_fee_cents INTEGER DEFAULT 0,
    coverage_radius_km INTEGER DEFAULT 15,
    clinic_address TEXT,
    UNIQUE (vet_id, modality)
);

CREATE INDEX IF NOT EXISTS idx_vet_modalities_active ON vet_service_modalities (modality, is_active, base_price_cents);

-- 5. Solicitações de Atendimento / Pré-Orçamentos
CREATE TABLE IF NOT EXISTS service_requests (
    id UUID PRIMARY KEY,
    tutor_id UUID NOT NULL REFERENCES users(id),
    pet_id UUID NOT NULL REFERENCES pets(id),
    vet_id UUID NOT NULL REFERENCES vet_profiles(id),
    modality VARCHAR(20) NOT NULL CHECK (modality IN ('CLINIC', 'HOME_VISIT', 'ONLINE')),
    urgency_type VARCHAR(20) NOT NULL CHECK (urgency_type IN ('IMMEDIATE', 'SCHEDULED')),
    scheduled_for TIMESTAMPTZ,
    status VARCHAR(24) NOT NULL CHECK (status IN ('PENDING_QUOTE', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'CANCELLED')),
    symptoms_description TEXT NOT NULL,
    tutor_address TEXT,
    tutor_lat DOUBLE PRECISION,
    tutor_lng DOUBLE PRECISION,
    estimated_price_cents INTEGER NOT NULL,
    agreed_price_cents INTEGER,
    vet_quote_notes TEXT,
    external_meeting_link TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_service_requests_tutor ON service_requests (tutor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_service_requests_vet ON service_requests (vet_id, status, created_at DESC);

-- 6. Avaliações Pós-Atendimento
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY,
    service_request_id UUID NOT NULL UNIQUE REFERENCES service_requests(id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES users(id),
    vet_id UUID NOT NULL REFERENCES vet_profiles(id),
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reviews_vet ON reviews (vet_id, created_at DESC);
