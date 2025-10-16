from app.serializers.farm import (
    FarmReadSerializer,
    FarmWriteSerializer,
    FarmUpdateSerializer,
    FarmSerializer,
)
from app.serializers.agrodealer import (
    AgrodealerReadSerializer,
    AgrodealerWriteSerializer,
    AgrodealerUpdateSerializer,
)
from app.serializers.e_extension import (
    EExtensionOfficerReadSerializer,
    EExtensionOfficerWriteSerializer,
    EExtensionOfficerUpdateSerializer,
)
from app.serializers.super_extension import (
    SuperExtensionOfficerReadSerializer,
    SuperExtensionOfficerWriteSerializer,
    SuperExtensionOfficerUpdateSerializer,
)
from app.serializers.farmer_work_request import (
    FarmerWorkRequestReadSerializer,
    FarmerWorkRequestCreateSerializer
)
from app.serializers.eextension_work_request import (
    EExtensionWorkRequestReadSerializer,
    EExtensionWorkRequestCreateSerializer
)

__all__ = [
    'FarmReadSerializer',
    'FarmWriteSerializer',
    'FarmUpdateSerializer',
    'FarmSerializer',
    'AgrodealerReadSerializer',
    'AgrodealerWriteSerializer',
    'AgrodealerUpdateSerializer',
    'EExtensionOfficerReadSerializer',
    'EExtensionOfficerWriteSerializer',
    'EExtensionOfficerUpdateSerializer',
    'SuperExtensionOfficerReadSerializer',
    'SuperExtensionOfficerWriteSerializer',
    'SuperExtensionOfficerUpdateSerializer',
    'FarmerWorkRequestReadSerializer',
    'FarmerWorkRequestCreateSerializer',
    'EExtensionWorkRequestReadSerializer',
    'EExtensionWorkRequestCreateSerializer',
    'AcceptRejectRequestSerializer',
]
