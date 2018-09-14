# -*- coding: utf8 -*-

import uuid

# Init constant list of DRM System Id
DRM_SYSTEMID_LIST = [
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


def get_drm_name(system_id):
    """Get the DRM Name from System ID

    :param system_id: DRM System ID
    :type system_id: uuid
    :return: DRM Name
    :rtype: str
    """
    system_id = system_id if isinstance(system_id, uuid.UUID) else uuid.UUID(system_id)
    return next(
        (DRM["name"] for DRM in DRM_SYSTEMID_LIST if DRM["system_id"] == system_id),
        "Unknown",
    )


def get_drm_system_id(name):
    """Get the DRM System ID from Name

    :param name: DRM Name
    :type name: str
    :return: DRM System ID
    :rtype: uuid
    """
    name = str(name).upper()
    return next(
        (DRM["system_id"] for DRM in DRM_SYSTEMID_LIST if DRM["name"] == name), None
    )


def indent(elem, level=0):
    i = "\n" + level * "  "
    j = "\n" + (level - 1) * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem
