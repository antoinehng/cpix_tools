# -*- coding: utf8 -*-

import os, uuid, errno, base64, json
import xml.etree.ElementTree as ET

from . import get_drm_name, get_drm_system_id
from .content_key import ContentKey
from .drm_system import DrmSystem
from .usage_rule import UsageRule


class Cpix(object):
    """This class parsing a CPIX document"""

    def __init__(self, path):
        """Init a Cpix element

        :param path: CPIX file path
        :type path: str
        """
        # Check if file exists and is accessible
        if os.path.isfile(path) and os.access(path, os.R_OK):
            self.file_path = path
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

        # Init lists for accessing parsed data
        self.content_key_list = []
        self.drm_system_list = []
        self.usage_rule_list = []

        # Parse CPIX document
        self._parse_document()

    def __str__(self):
        """Return the CPIX file path

        :return: cpix_file_path
        :rtype: str
        """
        return f"{self.file_path}"

    def _parse_document(self):
        """Parse the CPIX XML document"""
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        for child in root:
            if "ContentKeyList" in child.tag:
                self._parse_content_key_list(child)

            elif "DRMSystemList" in child.tag:
                self._parse_drm_system_list(child)

            elif "ContentKeyUsageRuleList" in child.tag:
                self._parse_usage_rule_list(child)

    def _parse_content_key_list(self, content_key_list):
        """Parse ContentKey element"""
        for content_key in content_key_list:
            # Retrieve Content Key data
            kid = content_key.get("kid")
            key = base64.b64decode(
                content_key.find("{urn:dashif:org:cpix}Data")
                .find("{urn:ietf:params:xml:ns:keyprov:pskc}Secret")
                .find("{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue")
                .text
            ).hex()

            # Add new ContentKey object to the list
            self.content_key_list.append(ContentKey(kid, key))

    def _parse_drm_system_list(self, drm_system_list):
        """Parse DRMSystem element"""
        for drm_system in drm_system_list:
            # Retrieve DRM System data
            kid = drm_system.get("kid")
            system_id = uuid.UUID(drm_system.get("systemId"))
            pssh = drm_system.find("{urn:dashif:org:cpix}PSSH").text
            content_protection_data = drm_system.find(
                "{urn:dashif:org:cpix}ContentProtectionData"
            ).text

            # We want to find the pssh data without the pssh box headers
            system_data = None

            # Microsoft PlayReady
            if system_id == get_drm_system_id("PLAYREADY"):
                pssh_data = (
                    base64.b64decode(content_protection_data)
                    .decode("utf-8")
                    .split("<mspr:pro>")[1]
                    .replace("</mspr:pro>", "")
                )

            # Google Widevine
            elif system_id == get_drm_system_id("WIDEVINE"):
                pssh_data = pssh.encode("utf-8")[32:].decode("utf-8")

            # Nagra Connect
            elif system_id == get_drm_system_id("NAGRA"):
                pssh_data = pssh.encode("utf-8")[32:].decode("utf-8")

            # Add new DrmSystem object to the list
            self.drm_system_list.append(
                DrmSystem(kid, system_id, pssh, pssh_data, content_protection_data)
            )

    def _parse_usage_rule_list(self, usage_rule_list):
        """Parse ContentKeyUsageRule element"""
        for usage_rule in usage_rule_list:
            # Retrieve Usage Rule data
            kid = usage_rule.get("kid")

            video_filter_min_pixels = usage_rule.find(
                "{urn:dashif:org:cpix}VideoFilter"
            ).get("minPixels")

            video_filter_max_pixels = usage_rule.find(
                "{urn:dashif:org:cpix}VideoFilter"
            ).get("maxPixels")

            audio_filter = (
                True
                if usage_rule.find("{urn:dashif:org:cpix}AudioFilter") is not None
                else False
            )

            # Add new UsageRule object to the list
            self.usage_rule_list.append(
                UsageRule(
                    kid, video_filter_min_pixels, video_filter_max_pixels, audio_filter
                )
            )

    def export_json(self):
        """Create JSON string from CPIX data

        :return: JSON string
        :rtype: str
        """
        data = {}
        data["cpix_file_path"] = self.file_path
        data["content_key_list"] = []

        for content_key in self.content_key_list:
            key = {}
            key["kid"] = str(content_key.kid)
            key["key"] = str(content_key.key)

            key["drm_system_list"] = []
            for drm_system in self.drm_system_list:
                if drm_system.kid == content_key.kid:
                    drm = {}
                    drm["name"] = get_drm_name(drm_system.system_id)
                    drm["system_id"] = str(drm_system.system_id)
                    drm["pssh"] = drm_system.pssh
                    drm["pssh_data"] = drm_system.pssh_data
                    drm["content_protection_data"] = drm_system.content_protection_data
                    key["drm_system_list"].append(drm)

            key["usage_rule"] = None
            for usage_rule in self.usage_rule_list:
                if usage_rule.kid == content_key.kid:
                    rule = {}
                    rule["video_filter"] = usage_rule.video_filter
                    rule["audio_filter"] = usage_rule.audio_filter
                    key["usage_rule"] = rule

            data["content_key_list"].append(key)

        return json.dumps(data)

    def export_json_as_file(self):
        """Write JSON file with CPIX data
        
        :return: Output file path
        :rtype: str
        """
        output_file_path = os.path.splitext(self.file_path)[0] + ".json"
        f = open(output_file_path, "wt", encoding="utf-8")
        f.write(self.export_json())
        f.close()
        return output_file_path
