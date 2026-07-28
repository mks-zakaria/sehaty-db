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
from sehaty.db.auth import PhoneOtp, RefreshToken  # noqa: F401
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
from sehaty.db.cabinets import Cabinet, CabinetSession  # noqa: F401
from sehaty.db.clinical import (  # noqa: F401
    AuditLog,
    Diagnosis,
    Dispense,
    DispenseItem,
    DrugInteraction,
    InteractionSeverity,
    Medication,
    Notification,
    PharmacyStock,
    PracticeProfile,
    Prescription,
    PrescriptionItem,
    PrescriptionStatus,
    PrescriptionTemplate,
    RenewalRequest,
    RenewalStatus,
    TreatmentFeedback,
    TreatmentOutcome,
)
from sehaty.db.confirmations import (  # noqa: F401
    ConfirmationChannel,
    ConfirmationStatus,
    OutboundMessage,
    OutboundStatus,
)
from sehaty.db.landing_events import LandingEvent, LandingEventType  # noqa: F401
from sehaty.db.landing_pages import DoctorLanding  # noqa: F401
from sehaty.db.messaging import Message, MessageThread  # noqa: F401
from sehaty.db.patient_ledger import (  # noqa: F401
    PatientCharge,
    PatientPayment,
    PaymentMethod,
)
from sehaty.db.patients import ClinicPatient  # noqa: F401
from sehaty.db.pharmacy_products import (  # noqa: F401
    PharmacyProduct,
    ProductKind,
    Sale,
    SaleItem,
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
    AvailabilityException,
    AvailabilityExceptionKind,
)
from sehaty.db.specialties import DoctorSpecialty, Specialty  # noqa: F401
from sehaty.db.staff import DoctorAssistant  # noqa: F401
from sehaty.db.users import (  # noqa: F401
    ClaimStatus,
    DoctorProfile,
    GeoPrecision,
    PatientProfile,
    ProfileSource,
    User,
    UserRole,
    VerificationStatus,
)
from sehaty.db.waitlist import WaitlistEntry, WaitlistStatus  # noqa: F401

# Every domain added under sehaty/db/<domain>.py gets one import block here.
