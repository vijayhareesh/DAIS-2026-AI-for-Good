-- Lakebase operational schema for HealthVerify India.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS facilities_verified (
    unique_id TEXT PRIMARY KEY,
    facility_name TEXT NOT NULL,
    state TEXT,
    city TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    address_line3 TEXT,
    zip_code TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    phone_number TEXT,
    email TEXT,
    website TEXT,
    social_media_links JSONB DEFAULT '{}'::JSONB,
    specialties TEXT[] DEFAULT ARRAY[]::TEXT[],
    capabilities TEXT[] DEFAULT ARRAY[]::TEXT[],
    equipment TEXT[] DEFAULT ARRAY[]::TEXT[],
    procedures TEXT[] DEFAULT ARRAY[]::TEXT[],
    bed_capacity INTEGER,
    icu_capacity INTEGER,
    doctor_count INTEGER,
    trust_score NUMERIC(6,3) NOT NULL DEFAULT 0.500,
    plausibility_status TEXT NOT NULL DEFAULT 'UNVERIFIED',
    freshness_status TEXT NOT NULL DEFAULT 'NO_DATE',
    last_verified_date TIMESTAMPTZ,
    verification_count INTEGER NOT NULL DEFAULT 0,
    total_claims_checked INTEGER NOT NULL DEFAULT 0,
    total_claims_verified INTEGER NOT NULL DEFAULT 0,
    data_source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_facilities_location_gist
    ON facilities_verified
    USING GIST (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326))
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_facilities_city ON facilities_verified(city, state);
CREATE INDEX IF NOT EXISTS idx_facilities_trust ON facilities_verified(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_facilities_status ON facilities_verified(plausibility_status, freshness_status);

CREATE TABLE IF NOT EXISTS verification_queue (
    queue_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL REFERENCES facilities_verified(unique_id),
    facility_name TEXT NOT NULL,
    city TEXT,
    state TEXT,
    phone_number TEXT,
    priority_score INTEGER NOT NULL,
    risk_category TEXT NOT NULL,
    risk_factors TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    verification_script JSONB NOT NULL,
    script_version INTEGER NOT NULL DEFAULT 1,
    script_generated_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'PENDING',
    assigned_volunteer_id TEXT,
    assigned_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_queue_priority ON verification_queue(priority_score DESC, created_at);
CREATE INDEX IF NOT EXISTS idx_queue_status ON verification_queue(status);
CREATE INDEX IF NOT EXISTS idx_queue_facility ON verification_queue(facility_id);

CREATE TABLE IF NOT EXISTS volunteer_validations (
    validation_id TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL REFERENCES facilities_verified(unique_id),
    volunteer_id TEXT NOT NULL,
    queue_id TEXT REFERENCES verification_queue(queue_id),
    claims_checked INTEGER NOT NULL,
    claims_verified INTEGER NOT NULL,
    claims_failed INTEGER NOT NULL,
    validation_details JSONB NOT NULL DEFAULT '{}'::JSONB,
    old_trust_score NUMERIC(6,3),
    new_trust_score NUMERIC(6,3),
    score_change NUMERIC(6,3),
    volunteer_notes TEXT,
    call_duration_seconds INTEGER,
    phone_answered BOOLEAN,
    validated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_validations_facility ON volunteer_validations(facility_id, validated_at DESC);
CREATE INDEX IF NOT EXISTS idx_validations_volunteer ON volunteer_validations(volunteer_id, validated_at DESC);
CREATE INDEX IF NOT EXISTS idx_validations_date ON volunteer_validations(validated_at DESC);
