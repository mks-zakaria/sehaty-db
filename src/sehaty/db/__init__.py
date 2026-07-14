"""Re-export every domain module.

CRITICAL: every ORM domain must be imported here so that
`SehatyBase.metadata` sees all tables. If a module is missing, Alembic
autogenerate will not see its tables — or will emit DROP for them.
(See senior-dev reference/data.md.)
"""

from sehaty.db.admin_config import (  # noqa: F401
    AdminConfig,
    FeatureFlag,
    RankingWeights,
)
from sehaty.db.base import SehatyBase, TimestampMixin, utcnow  # noqa: F401
from sehaty.db.billing import (  # noqa: F401
    CreditLedger,
    Invoice,
    InvoiceStatus,
    Payment,
    Plan,
    Subscription,
    SubscriptionStatus,
)
from sehaty.db.clinical import (  # noqa: F401
    AuditLog,
    Dispense,
    DispenseItem,
    DrugInteraction,
    InteractionSeverity,
    Medication,
    Notification,
    Prescription,
    PrescriptionItem,
    PrescriptionStatus,
    RenewalRequest,
    RenewalStatus,
)
from sehaty.db.referral import Referral, ReferralStatus  # noqa: F401
from sehaty.db.reputation import (  # noqa: F401
    ReputationScore,
    Review,
    ReviewDirection,
    ReviewStatus,
)
from sehaty.db.scheduling import (  # noqa: F401
    Appointment,
    AppointmentStatus,
    Availability,
)
from sehaty.db.specialties import DoctorSpecialty, Specialty  # noqa: F401
from sehaty.db.users import (  # noqa: F401
    DoctorProfile,
    PatientProfile,
    User,
    UserRole,
    VerificationStatus,
)

# Every domain added under sehaty/db/<domain>.py gets one import block here.
