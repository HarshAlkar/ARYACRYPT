# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.file import File  # noqa
from app.models.activity import CryptoActivity  # noqa
from app.models.refresh_revocation import RefreshTokenRevocation  # noqa
