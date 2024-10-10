
from .element_id import (
    # internal IDs for countries, terrains, and units
    MAIN_TERR,
    MAIN_CTRY,
    MAIN_UNIT,
    MAIN_TERR_CAT,

    #
    AWS_TERR,
    AWS_UNIT,

    # AWBW IDs for countries, terrains, and units
    AWBW_TERR,
    AWBW_UNIT_CODE,
    AWBW_COUNTRY_CODE,
    AWBW_AWARENESS,

    #
    main_terr_to_awbw,
    main_terr_to_aws,
    main_unit_to_aws
)

from .bitmap import (
    BITMAP_PALETTE,
    BITMAP_SPEC,

    STATIC_ID_TO_SPEC,
    UNIT_ID_TO_SPEC,
    ANIM_ID_TO_SPEC
)
