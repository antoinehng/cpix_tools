# -*- coding: utf8 -*-

import os, uuid, errno, base64, json
import xml.etree.ElementTree as ET
from operator import itemgetter

from . import get_drm_name, get_drm_system_id, indent
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
                pssh_data = base64.b64encode(base64.b64decode(pssh)[32:]).decode(
                    "utf-8"
                )

            # Nagra Connect
            elif system_id == get_drm_system_id("NAGRA"):
                pssh_data = base64.b64encode(base64.b64decode(pssh)[32:]).decode(
                    "utf-8"
                )

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

        # Make sure UsageRule List is ordered by video_filter['min_pixels']
        self.usage_rule_list = sorted(
            self.usage_rule_list, key=lambda k: k.video_filter["min_pixels"]
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
        with open(output_file_path, "wt", encoding="utf-8") as f:
            f.write(self.export_json())
        return output_file_path

    def export_titanfile_xml(self):
        """Create Ateme Titan File XML Common-Encryption from CPIX data

        :return: XML string
        :rtype: str
        """
        common_encryption = ET.Element("commonencryption")
        server = ET.SubElement(
            common_encryption,
            "server",
            attrib={"enabled": "false", "type": "piksel", "url": ""},
        )

        idx = 0
        drm = [{}] * len(self.drm_system_list)
        for usage_rule in self.usage_rule_list:
            # Keep the usage rues ordered by min_pixels
            for content_key in self.content_key_list:
                if content_key.kid == usage_rule.kid:
                    for drm_system in self.drm_system_list:
                        if drm_system.kid == content_key.kid:
                            # create drm elem with attributes
                            drm[idx]["element"] = ET.SubElement(
                                common_encryption,
                                "drm",
                                attrib={
                                    "idx": str(idx + 1),
                                    "system_id": str(drm_system.system_id),
                                    "scheme_value": get_drm_name(drm_system.system_id),
                                },
                            )
                            # create drm/key elem with key and kid attributes
                            drm[idx]["key"] = ET.SubElement(
                                drm[idx]["element"],
                                "key",
                                attrib={
                                    "id": str(content_key.kid),
                                    "content": str(content_key.key),
                                },
                            )
                            # create drm/data elem and set inner text
                            drm[idx]["data"] = ET.SubElement(
                                drm[idx]["element"], "data"
                            )
                            drm[idx]["data"].text = drm_system.pssh_data
                            # create drm/initialization_vector_size elem and set value
                            drm[idx]["iv"] = ET.SubElement(
                                drm[idx]["element"], "initialization_vector_size"
                            )
                            drm[idx]["iv"].text = "8_bytes"

                            # Increment idx for next iter
                            idx = idx + 1

        indent(common_encryption)
        return ET.tostring(common_encryption, encoding="utf-8", method="xml").decode()

    def export_titanfile_xml_as_file(self):
        """Write Ateme Titan File XML Common-Encryption
        
        :return: Output file path
        :rtype: str
        """
        output_file_path = os.path.splitext(self.file_path)[0] + "_titanfile.xml"
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(self.export_titanfile_xml())
        return output_file_path

    def update_titanfile_kpreset_file(self, kpreset_path):
        """Update Ateme Titan File kPreset with CPIX data
        
        :return: Output file path
        :rtype: str
        """
        output_file_path = os.path.splitext(kpreset_path)[0] + "_cpix.kpreset"

        with open(kpreset_path, "r") as f:
            source = f.read()

        updated = source
        updated = updated.replace("<commonencryption>", "</commonencryption>")
        updated = updated.split("</commonencryption>")
        updated[1] = self.export_titanfile_xml()
        updated = "".join(updated)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(updated)

        return output_file_path

