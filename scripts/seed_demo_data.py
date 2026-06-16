from __future__ import annotations

import json
import os

from phase_2_app.agents import generate_verification_script
from phase_2_app.demo_data import heritage_hospitals


def build_sql() -> tuple[str, tuple]:
    facility = heritage_hospitals()
    script = generate_verification_script(facility)
    sql = """
INSERT INTO facilities_verified (
    unique_id, facility_name, state, city, latitude, longitude, phone_number,
    specialties, capabilities, trust_score, plausibility_status, freshness_status,
    verification_count, data_source
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (unique_id) DO UPDATE SET
    facility_name = EXCLUDED.facility_name,
    state = EXCLUDED.state,
    city = EXCLUDED.city,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    phone_number = EXCLUDED.phone_number,
    specialties = EXCLUDED.specialties,
    capabilities = EXCLUDED.capabilities,
    trust_score = EXCLUDED.trust_score,
    plausibility_status = EXCLUDED.plausibility_status,
    freshness_status = EXCLUDED.freshness_status,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO verification_queue (
    queue_id, facility_id, facility_name, city, state, phone_number,
    priority_score, risk_category, risk_factors, verification_script,
    script_generated_at, status
) VALUES (
    %s, %s, %s, %s, %s, %s, 95, 'HIGH', %s, %s::jsonb, CURRENT_TIMESTAMP, 'PENDING'
)
ON CONFLICT (queue_id) DO UPDATE SET
    priority_score = EXCLUDED.priority_score,
    risk_category = EXCLUDED.risk_category,
    risk_factors = EXCLUDED.risk_factors,
    verification_script = EXCLUDED.verification_script,
    updated_at = CURRENT_TIMESTAMP;
"""
    params = (
        facility.unique_id,
        facility.facility_name,
        facility.state,
        facility.city,
        facility.latitude,
        facility.longitude,
        facility.phone_number,
        list(facility.specialties),
        list(facility.capabilities),
        facility.trust_score,
        facility.plausibility_status,
        facility.freshness_status,
        facility.verification_count,
        "demo_seed",
        "q_heritage_hospitals_varanasi",
        facility.unique_id,
        facility.facility_name,
        facility.city,
        facility.state,
        facility.phone_number,
        list(facility.risk_factors),
        json.dumps(script),
    )
    return sql, params


def main() -> None:
    database_url = os.environ.get("LAKEBASE_DATABASE_URL")
    sql, params = build_sql()
    if not database_url:
        print("-- Set LAKEBASE_DATABASE_URL to apply this seed directly.")
        print(sql)
        print("-- Parameters:")
        print(json.dumps([str(value) for value in params], indent=2))
        return

    import psycopg2

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
    print("Seeded Heritage Hospitals demo data.")


if __name__ == "__main__":
    main()
