# -*- coding: utf8 -*-

import uuid

from . import get_drm_name


class DrmSystem(object):
    """This class defines a DRMSystem CPIX element"""

    def __init__(
        self, kid, system_id, pssh, pssh_data=None, content_protection_data=None
    ):
        """Init a DRM System element

        :param kid: Content Key ID
        :type kid: uuid
        :param system_id: DRM System ID
        :type system_id: uuid
        :param pssh: PSSH base64 string
        :type pssh: str
        :param content_protection_data: Content Protection Data base64 string
        :type content_protection_data: str
        :param pssh_data: DRM System Data
        :type pssh_data: str
        """
        self.kid = kid if isinstance(kid, uuid.UUID) else uuid.UUID(kid)
        self.system_id = (
            system_id if isinstance(system_id, uuid.UUID) else uuid.UUID(system_id)
        )
        self.pssh = pssh
        self.pssh_data = pssh_data
        self.content_protection_data = content_protection_data

    def __str__(self):
        """Display the DRM System basic values

        :return: human readable DRM System basic values
        :rtype: str
        """
        return f"kid:{self.kid}, drm:{get_drm_name(self.system_id)}, system_id:{self.system_id}"
