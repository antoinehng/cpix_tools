# -*- coding: utf8 -*-

import uuid

DRM_LIST = [
    {
        "name": "PLAYREADY",
        "system_id": uuid.UUID("9a04f079-9840-4286-ab92-e65be0885f95"),
    },
    {
        "name": "WIDEVINE",
        "system_id": uuid.UUID("edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"),
    },
    {"name": "NAGRA", "system_id": uuid.UUID("adb41c24-2dbf-4a6d-958b-4457c0d27b95")},
]


class DrmSystem(object):
    """This class defines a DRMSystem CPIX element"""

    def __init__(
        self, kid, system_id, pssh, content_protection_data=None, pssh_data=None
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

    def get_system_id_name(self):
        for DRM in DRM_LIST:
            if DRM["system_id"] == self.system_id:
                return DRM["name"]
        return "Undefined"

    def __str__(self):
        """Display the DRM System basic values

        :return: human readable DRM System basic values
        :rtype: str
        """
        return f"kid:{self.kid}, drm:{self.get_system_id_name()}, system_id:{self.system_id}"
