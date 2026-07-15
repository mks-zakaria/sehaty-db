"""Practice staffing links (doctor_assistants).

A doctor's assistant/secretary is an app user (role ASSISTANT) who logs in to help
run a doctor's practice: manage the schedule and the patient register, call patients
to confirm appointments, etc. This table links an assistant user to the doctor(s)
they work for. One assistant can serve several doctors and a doctor can have several
assistants, so it's a plain many-to-many association with an activation flag.
"""

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from sehaty.db.base import SehatyBase, TimestampMixin


class DoctorAssistant(SehatyBase, TimestampMixin):
    __tablename__ = "doctor_assistants"
    __table_args__ = (
        # One membership row per (doctor, assistant) pair. Portable plain unique
        # constraint (works on both SQLite tests and Postgres prod).
        UniqueConstraint("doctor_id", "assistant_id", name="uq_doctor_assistants_pair"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # The doctor being assisted. Link disappears if the doctor account is deleted.
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # The assistant (an ASSISTANT-role user). Link disappears if their account is deleted.
    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # Soft on/off toggle so access can be revoked without deleting history.
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"), default=True
    )
