from __future__ import annotations

import os
import json
from dataclasses import replace
from datetime import datetime
from typing import Optional
from uuid import uuid4

import psycopg
import requests
from .models import Facility, ValidationResult
from .trust import PATIENT_TRUST_THRESHOLD, recalculate_trust_score


def _as_tuple(value) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(str(item) for item in value if item is not None)
    if isinstance(value, tuple):
        return tuple(str(item) for item in value if item is not None)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return (text,)
        if isinstance(parsed, list):
            return tuple(str(item) for item in parsed if item is not None)
        return (str(parsed),)
    return (str(value),)


def _generate_database_credential(endpoint: str) -> str:
    from databricks.sdk.core import Config

    cfg = Config()
    headers = cfg.authenticate()
    headers["Content-Type"] = "application/json"
    response = requests.post(
        f"{cfg.host.rstrip('/')}/api/2.0/postgres/credentials",
        headers=headers,
        json={"endpoint": endpoint},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["token"]


class LakebaseStore:
    """Production store backed by Lakebase Postgres."""
    
    def __init__(self, conn_string: str):
        self._conn_string = conn_string
        self._ensure_validation_table()
    
    @classmethod
    def from_app_config(cls) -> "LakebaseStore":
        """Create store from Databricks App Lakebase configuration."""
        # Databricks Apps Lakebase resources inject standard PostgreSQL env vars.
        # Keep the LAKEBASE_* fallbacks for older local/dev configuration.
        host = os.environ.get("PGHOST") or os.environ.get("LAKEBASE_HOST")
        database = (
            os.environ.get("PGDATABASE")
            or os.environ.get("LAKEBASE_DATABASE")
            or "databricks_postgres"
        )
        user = os.environ.get("PGUSER") or os.environ.get("LAKEBASE_USER")
        password = os.environ.get("PGPASSWORD") or os.environ.get("LAKEBASE_PASSWORD")
        port = os.environ.get("PGPORT", "5432")
        endpoint = os.environ.get("LAKEBASE_ENDPOINT")

        if not password and endpoint:
            password = _generate_database_credential(endpoint)

        missing = [
            name
            for name, value in {
                "PGHOST": host,
                "PGUSER": user,
                "PGPASSWORD": password,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Lakebase connection environment missing: {', '.join(missing)}")

        conn_string = (
            f"host={host} port={port} dbname={database} "
            f"user={user} password={password} sslmode=require"
        )
        return cls(conn_string)
    
    def _get_conn(self):
        """Get a new Postgres connection."""
        return psycopg.connect(self._conn_string)
    
    def _ensure_validation_table(self):
        """Create validation table if it doesn't exist."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS public.volunteer_validations (
                        validation_id TEXT PRIMARY KEY,
                        facility_id TEXT NOT NULL,
                        volunteer_id TEXT NOT NULL,
                        claims_checked INTEGER NOT NULL,
                        claims_verified INTEGER NOT NULL,
                        claims_failed INTEGER NOT NULL,
                        old_trust_score DOUBLE PRECISION NOT NULL,
                        new_trust_score DOUBLE PRECISION NOT NULL,
                        details JSONB,
                        validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                conn.commit()
    
    def get_facility(self, facility_id: str) -> Optional[Facility]:
        """Get a single facility by ID from Lakebase."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        unique_id,
                        facility_name,
                        state,
                        city,
                        pincode,
                        latitude,
                        longitude,
                        phone_numbers,
                        "officialPhone",
                        email,
                        "officialWebsite",
                        specialties,
                        capability,
                        total_capability_claims,
                        combined_quality_confidence_score,
                        overall_reliability,
                        delivery_likelihood,
                        red_flags,
                        data_quality_status
                    FROM public.facilities
                    WHERE unique_id = %s
                """, (facility_id,))
                row = cur.fetchone()
                
                if not row:
                    return None
                
                # Count validations for this facility
                cur.execute("""
                    SELECT COUNT(*) FROM public.volunteer_validations
                    WHERE facility_id = %s
                """, (facility_id,))
                validation_count = cur.fetchone()[0]
                
                # Get last validation date
                cur.execute("""
                    SELECT MAX(validated_at) FROM public.volunteer_validations
                    WHERE facility_id = %s
                """, (facility_id,))
                last_verified = cur.fetchone()[0]
                
                return Facility(
                    unique_id=row[0],
                    facility_name=row[1],
                    state=row[2],
                    city=row[3],
                    latitude=row[5],
                    longitude=row[6],
                    phone_number=row[8] or row[7] or "",
                    plausibility_status=row[15] or "UNKNOWN",
                    freshness_status=row[18] or "UNKNOWN",
                    risk_factors=_as_tuple(row[17]) or tuple(
                        item for item in (row[15], row[16], row[18]) if item
                    ),
                    specialties=_as_tuple(row[11]),
                    capabilities=_as_tuple(row[12]),
                    official_phone=row[8],
                    email=row[9],
                    official_website=row[10],
                    trust_score=row[14] or 0.5,  # combined_quality_confidence_score
                    verification_count=validation_count,
                    last_verified_date=last_verified,
                    pincode=row[4] or "",
                    reliability_tier=row[15],
                    delivery_likelihood=row[16]
                )
    
    def list_facilities(self, limit: int = 100) -> list[Facility]:
        """List facilities from Lakebase with pagination."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        unique_id,
                        facility_name,
                        state,
                        city,
                        pincode,
                        latitude,
                        longitude,
                        combined_quality_confidence_score,
                        "officialPhone",
                        specialties,
                        capability,
                        overall_reliability,
                        delivery_likelihood,
                        data_quality_status
                    FROM public.facilities
                    ORDER BY combined_quality_confidence_score DESC
                    LIMIT %s
                """, (limit,))
                
                facilities = []
                for row in cur.fetchall():
                    facilities.append(Facility(
                        unique_id=row[0],
                        facility_name=row[1],
                        state=row[2],
                        city=row[3],
                        latitude=row[5],
                        longitude=row[6],
                        phone_number=row[8] or "",
                        trust_score=row[7] or 0.5,
                        plausibility_status=row[11] or "UNKNOWN",
                        freshness_status=row[13] or "UNKNOWN",
                        risk_factors=tuple(item for item in (row[11], row[12], row[13]) if item),
                        specialties=_as_tuple(row[9]),
                        capabilities=_as_tuple(row[10]),
                        pincode=row[4] or "",
                        official_phone=row[8] or "",
                        reliability_tier=row[11] or "",
                        delivery_likelihood=row[12] or "",
                    ))
                
                return facilities
    
    def patient_visible(self, facility_id: str) -> bool:
        """Check if facility meets patient visibility threshold."""
        facility = self.get_facility(facility_id)
        return facility and facility.trust_score >= PATIENT_TRUST_THRESHOLD
    
    def search_facilities(
        self, 
        text: str = "", 
        city: str | None = None,
        limit: int = 50
    ) -> list[Facility]:
        """Search facilities with optional text and city filters."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT 
                        unique_id,
                        facility_name,
                        state,
                        city,
                        pincode,
                        latitude,
                        longitude,
                        combined_quality_confidence_score,
                        "officialPhone",
                        specialties,
                        capability,
                        overall_reliability,
                        delivery_likelihood,
                        data_quality_status
                    FROM public.facilities
                    WHERE 1=1
                """
                params = []
                
                if city:
                    query += " AND LOWER(city) = LOWER(%s)"
                    params.append(city)
                
                if text.strip():
                    query += """ AND (
                        LOWER(facility_name) LIKE LOWER(%s) OR
                        LOWER(city) LIKE LOWER(%s) OR
                        LOWER(state) LIKE LOWER(%s) OR
                        LOWER(unique_id) LIKE LOWER(%s)
                    )"""
                    search_pattern = f"%{text.strip()}%"
                    params.extend([search_pattern] * 4)
                
                query += " ORDER BY combined_quality_confidence_score DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                
                facilities = []
                for row in cur.fetchall():
                    facilities.append(Facility(
                        unique_id=row[0],
                        facility_name=row[1],
                        state=row[2],
                        city=row[3],
                        latitude=row[5],
                        longitude=row[6],
                        trust_score=row[7] or 0.5,
                        phone_number=row[8] or "",
                        plausibility_status=row[11] or "UNKNOWN",
                        freshness_status=row[13] or "UNKNOWN",
                        risk_factors=tuple(item for item in (row[11], row[12], row[13]) if item),
                        specialties=_as_tuple(row[9]),
                        capabilities=_as_tuple(row[10]),
                        pincode=row[4] or "",
                        official_phone=row[8] or "",
                        reliability_tier=row[11] or "",
                        delivery_likelihood=row[12] or "",
                    ))
                
                return facilities
    
    def submit_validation(
        self,
        facility_id: str,
        volunteer_id: str,
        claims_checked: int,
        claims_verified: int,
        details: dict[str, bool],
    ) -> ValidationResult:
        """Submit a validation and update facility trust score."""
        facility = self.get_facility(facility_id)
        if not facility:
            raise ValueError(f"Facility {facility_id} not found")
        
        # Calculate new trust score
        new_score = recalculate_trust_score(
            old_score=facility.trust_score,
            claims_checked=claims_checked,
            claims_verified=claims_verified,
            verification_count=facility.verification_count,
        )
        
        validation = ValidationResult(
            validation_id=f"val_{uuid4().hex[:10]}",
            facility_id=facility_id,
            volunteer_id=volunteer_id,
            claims_checked=claims_checked,
            claims_verified=claims_verified,
            claims_failed=claims_checked - claims_verified,
            old_trust_score=facility.trust_score,
            new_trust_score=new_score,
            details=details,
        )
        
        # Persist validation to Postgres
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO public.volunteer_validations
                    (validation_id, facility_id, volunteer_id, claims_checked,
                     claims_verified, claims_failed, old_trust_score, 
                     new_trust_score, details, validated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    validation.validation_id,
                    validation.facility_id,
                    validation.volunteer_id,
                    validation.claims_checked,
                    validation.claims_verified,
                    validation.claims_failed,
                    validation.old_trust_score,
                    validation.new_trust_score,
                    psycopg.types.json.Json(validation.details),
                    validation.validated_at
                ))
                conn.commit()
        
        return validation
    
    def validations(self, facility_id: Optional[str] = None) -> list[ValidationResult]:
        """Get validation history, optionally filtered by facility."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                if facility_id:
                    cur.execute("""
                        SELECT validation_id, facility_id, volunteer_id,
                               claims_checked, claims_verified, claims_failed,
                               old_trust_score, new_trust_score, details, validated_at
                        FROM public.volunteer_validations
                        WHERE facility_id = %s
                        ORDER BY validated_at DESC
                    """, (facility_id,))
                else:
                    cur.execute("""
                        SELECT validation_id, facility_id, volunteer_id,
                               claims_checked, claims_verified, claims_failed,
                               old_trust_score, new_trust_score, details, validated_at
                        FROM public.volunteer_validations
                        ORDER BY validated_at DESC
                        LIMIT 100
                    """)
                
                validations = []
                for row in cur.fetchall():
                    validations.append(ValidationResult(
                        validation_id=row[0],
                        facility_id=row[1],
                        volunteer_id=row[2],
                        claims_checked=row[3],
                        claims_verified=row[4],
                        claims_failed=row[5],
                        old_trust_score=row[6],
                        new_trust_score=row[7],
                        details=row[8],
                        validated_at=row[9]
                    ))
                
                return validations
