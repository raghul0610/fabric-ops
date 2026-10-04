from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        actor_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID,
        metadata: dict,
    ) -> None:
        self.db.execute(
            text("""
                INSERT INTO public.audit_logs
                    (actor_id, action, entity_type, entity_id, metadata)
                VALUES
                    (:actor_id, :action, :entity_type, :entity_id, CAST(:metadata AS jsonb))
            """),
            {
                "actor_id": str(actor_id),
                "action": action,
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "metadata": __import__("json").dumps(metadata),
            },
        )
        self.db.commit()
