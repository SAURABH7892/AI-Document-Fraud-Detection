"""Database schema initialization and seeding."""
import logging
from sqlalchemy.orm import Session
from backend.app.db.session import engine, Base
from backend.app.models.entities import VerificationSource, User
from backend.app.security.password import get_password_hash

logger = logging.getLogger(__name__)

def init_db(db: Session = None):
    """Create all database tables and seed baseline system records."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified or created.")

    if db:
        # Seed DigiLocker verification source status
        source = db.query(VerificationSource).filter(VerificationSource.source_name == "DigiLocker / National Academic Depository").first()
        if not source:
            source = VerificationSource(
                source_name="DigiLocker / National Academic Depository",
                is_available=False,
                status_details="Official API integration not configured (requires government issuer credentials)"
            )
            db.add(source)
            db.commit()
            logger.info("Verification source seeded: DigiLocker / NAD (Unavailable/Not configured).")

        # Seed default demo reviewer user if none exists
        demo_user = db.query(User).filter(User.email == "demo@docshield.ai").first()
        if not demo_user:
            demo_user = User(
                email="demo@docshield.ai",
                hashed_password=get_password_hash("DemoPass123!"),
                full_name="Dr. Alok Verma",
                role="reviewer"
            )
            db.add(demo_user)
            db.commit()
            logger.info("Demo reviewer user seeded: demo@docshield.ai")
