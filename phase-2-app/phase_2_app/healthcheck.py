from __future__ import annotations

import json
import os

from .lakebase_store import LakebaseStore
from .store import create_store


def main() -> None:
    store = create_store()
    facilities = store.list_facilities(limit=1)
    if not facilities:
        raise RuntimeError("Lakebase healthcheck failed: no facilities returned")

    result_payload = {
        "facilities_checked": len(facilities),
        "top_facility": facilities[0].facility_name,
        "top_score": facilities[0].trust_score,
        "write_check": "skipped",
    }

    if os.environ.get("HEALTHVERIFY_HEALTHCHECK_WRITE", "false").lower() == "true":
        validation = store.submit_validation(
            facility_id=facilities[0].unique_id,
            volunteer_id="healthcheck",
            claims_checked=1,
            claims_verified=1,
            details={"healthcheck": True},
        )
        result_payload["write_check"] = "inserted"
        result_payload["validation_id"] = validation.validation_id

        if isinstance(store, LakebaseStore):
            with store._get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM public.volunteer_validations WHERE validation_id = %s",
                        (validation.validation_id,),
                    )
                    result_payload["write_check"] = f"inserted_deleted_{cur.rowcount}"
                    conn.commit()

    print("HEALTHVERIFY_HEALTHCHECK " + json.dumps(result_payload, sort_keys=True))


if __name__ == "__main__":
    main()
