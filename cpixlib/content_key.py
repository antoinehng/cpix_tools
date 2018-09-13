# -*- coding: utf8 -*-

import uuid


class ContentKey(object):
    """This class defines a ContentKey CPIX element"""

    def __init__(self, kid, key):
        """Init a Content Key element

        :param kid: Content Key ID
        :type kid: uuid
        :param key: Content Key Value
        :type key: uuid
        """
        self.kid = kid if isinstance(kid, uuid.UUID) else uuid.UUID(kid)
        self.key = key if isinstance(key, uuid.UUID) else uuid.UUID(key)

    def __str__(self):
        """Display the Content Key values

        :return: kid:{self.kid}, key:{self.key}
        :rtype: str
        """
        return f"kid:{self.kid}, key:{self.key}"
