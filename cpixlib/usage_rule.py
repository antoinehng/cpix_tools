# -*- coding: utf8 -*-

import uuid


class UsageRule(object):
    """This class defines a ContentKeyUsageRule CPIX element"""

    def __init__(
        self, kid, video_filter_min_pixels, video_filter_max_pixels, audio_filter
    ):
        """Init a Usage Rule element

        :param kid: Content Key ID
        :type kid: uuid
        :param video_filter_min_pixels: Video Filter Min Pixels Value
        :type video_filter_min_pixels: int
        :param video_filter_max_pixels: Video Filter Max Pixels Value
        :type video_filter_max_pixels: int
        :param audio_filter: Audio Filter Value
        :type audio_filter: bool
        """
        self.kid = kid if isinstance(kid, uuid.UUID) else uuid.UUID(kid)
        self.video_filter = {}
        self.video_filter["min_pixels"] = int(
            video_filter_min_pixels
            if video_filter_min_pixels is not None
            else 1  # Min value is 1
        )
        self.video_filter["max_pixels"] = int(
            video_filter_max_pixels
            if video_filter_max_pixels is not None
            else 34041601  # Max value is 8K+1
        )
        self.audio_filter = bool(audio_filter)

    def __str__(self):
        """Display the Usage Rule values

        :return: human readable Usage Rule values
        :rtype: str
        """
        return (
            f"kid:{self.kid},"
            f"video_filter_min_pixels:{self.video_filter['min_pixels']},"
            f"video_filter_max_pixels:{self.video_filter['max_pixels']},"
            f"audio_filter:{self.audio_filter}"
        )
