#!/usr/bin/env python
"""Unit tests for geocoder.py"""

# Based on original Java code:
#     java/test/com/google/i18n/phonenumbers/geocoding/PhoneNumberOfflineGeocoderTest.java
# Copyright (C) 2011 The Libphonenumber Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from phonenumbers import PhoneNumber, FrozenPhoneNumber
from phonenumbers import geocoder
from phonenumbers import description_for_number, country_name_for_number
from phonenumbers import description_for_valid_number, area_description_for_number

# Allow override library geocoding metadata with the test metadata.
REAL_GEOCODE_DATA = geocoder.GEOCODE_DATA
REAL_GEOCODE_LONGEST_PREFIX = geocoder.GEOCODE_LONGEST_PREFIX
from .testgeodata import GEOCODE_DATA as TEST_GEOCODE_DATA
from .testgeodata import GEOCODE_LONGEST_PREFIX as TEST_GEOCODE_LONGEST_PREFIX


def reinstate_real_geodata():
    """Reinstate real phone number geocoding metadata"""
    geocoder.GEOCODE_DATA = REAL_GEOCODE_DATA
    geocoder.GEOCODE_LONGEST_PREFIX = REAL_GEOCODE_LONGEST_PREFIX


def insert_test_geodata():
    """Insert test geocoding metadata into library"""
    geocoder.GEOCODE_DATA = TEST_GEOCODE_DATA
    geocoder.GEOCODE_LONGEST_PREFIX = TEST_GEOCODE_LONGEST_PREFIX


# Set up some test numbers to re-use.
KO_NUMBER1 = FrozenPhoneNumber(country_code=82, national_number=22123456L)
KO_NUMBER2 = FrozenPhoneNumber(country_code=82, national_number=322123456L)
KO_NUMBER3 = FrozenPhoneNumber(country_code=82, national_number=6421234567L)
KO_INVALID_NUMBER = FrozenPhoneNumber(country_code=82, national_number=1234L)
US_NUMBER1 = FrozenPhoneNumber(country_code=1, national_number=6502530000L)
US_NUMBER2 = FrozenPhoneNumber(country_code=1, national_number=6509600000L)
US_NUMBER3 = FrozenPhoneNumber(country_code=1, national_number=2128120000L)
US_NUMBER4 = FrozenPhoneNumber(country_code=1, national_number=6174240000L)
US_INVALID_NUMBER = FrozenPhoneNumber(country_code=1, national_number=123456789L)
BS_NUMBER1 = FrozenPhoneNumber(country_code=1, national_number=2423651234L)
AU_NUMBER = FrozenPhoneNumber(country_code=61, national_number=236618300L)
NUMBER_WITH_INVALID_COUNTRY_CODE = FrozenPhoneNumber(country_code=999, national_number=2423651234L)
INTERNATIONAL_TOLL_FREE = FrozenPhoneNumber(country_code=800, national_number=12345678L)

# Language/country codes
_CHINA = "CN"
_CHINESE = "zh"
_ITALIAN = "it"
_ENGLISH = "en"
_KOREAN = "ko"
_GERMAN = "de"
_FRENCH = "fr"
_SPANISH = "es"
_USA = "US"


class PhoneNumberGeocoderTest(unittest.TestCase):
    """Unit tests for PhoneNumberGeocoder"""

    def setUp(self):
        insert_test_geodata()

    def tearDown(self):
        reinstate_real_geodata()

    def testGetDescriptionForNumberWithNoDataFile(self):
        # No data file containing mappings for US numbers is available in Chinese for the unittests. As
        # a result, the country name of United States in simplified Chinese is returned.
        self.assertEqual(u"\u7F8E\u56FD",
                          description_for_number(US_NUMBER1, _CHINESE, region=_CHINA))
        self.assertEqual("Bahamas",
                          description_for_number(BS_NUMBER1, _ENGLISH, region=_USA))
        self.assertEqual("Australia",
                          description_for_number(AU_NUMBER, _ENGLISH, region=_USA))
        self.assertEqual("",
                          description_for_number(NUMBER_WITH_INVALID_COUNTRY_CODE, _ENGLISH, region=_USA))
        self.assertEqual("",
                          description_for_number(INTERNATIONAL_TOLL_FREE, _ENGLISH, region=_USA))

    def testGetDescriptionForNumberWithMissingPrefix(self):
        # Test that the name of the country is returned when the number passed in
        # is valid but not covered by the geocoding data file.
        self.assertEqual("United States",
                          description_for_number(US_NUMBER4, _ENGLISH, region=_USA))

    def testGetDescriptionForNumber_en_US(self):
        self.assertEqual("CA",
                          description_for_number(US_NUMBER1, _ENGLISH, region=_USA))
        self.assertEqual("Mountain View, CA",
                          description_for_number(US_NUMBER2, _ENGLISH, region=_USA))
        self.assertEqual("New York, NY",
                          description_for_number(US_NUMBER3, _ENGLISH, region=_USA))

    def testGetDescriptionForKoreanNumber(self):
        self.assertEqual("Seoul",
                          description_for_number(KO_NUMBER1, _ENGLISH))
        self.assertEqual("Incheon",
                          description_for_number(KO_NUMBER2, _ENGLISH))
        self.assertEqual("Jeju",
                          description_for_number(KO_NUMBER3, _ENGLISH))
        self.assertEqual(u"\uC11C\uC6B8",
                          description_for_number(KO_NUMBER1, _KOREAN))
        self.assertEqual(u"\uC778\uCC9C",
                          description_for_number(KO_NUMBER2, _KOREAN))

    def testGetDescriptionForFallBack(self):
        # No fallback, as the location name for the given phone number is
        # available in the requested language.
        self.assertEqual("Kalifornien",
                          description_for_number(US_NUMBER1, _GERMAN))
        # German falls back to English.
        self.assertEqual("New York, NY",
                          description_for_number(US_NUMBER3, _GERMAN))
        # Italian falls back to English.
        self.assertEqual("CA",
                          description_for_number(US_NUMBER1, _ITALIAN))
        # Korean doesn't fall back to English.
        self.assertEqual(u"\uB300\uD55C\uBBFC\uAD6D",
                          description_for_number(KO_NUMBER3, _KOREAN))

    def testGetDescriptionForNumberWithUserRegion(self):
        # User in Italy, American number. We should just show United States, in
        # Spanish, and not more detailed information.
        self.assertEqual("Estados Unidos",
                         description_for_number(US_NUMBER1, _SPANISH, region="IT"))
        # Unknown region - should just show country name.
        self.assertEqual("Estados Unidos",
                         description_for_number(US_NUMBER1, _SPANISH, region="ZZ"))
        # User in the States, language German, should show detailed data.
        self.assertEqual("Kalifornien",
                         description_for_number(US_NUMBER1, _GERMAN, region="US"))
        # User in the States, language French, no data for French, so we fallback
        # to English detailed data.
        self.assertEqual("CA",
                         description_for_number(US_NUMBER1, _FRENCH, region="US"))
        # Invalid number - return an empty string.
        self.assertEqual("", description_for_number(US_INVALID_NUMBER, _ENGLISH, region="US"))

    def testGetDescriptionForInvalidNumber(self):
        self.assertEqual("", description_for_number(KO_INVALID_NUMBER, _ENGLISH))
        self.assertEqual("", description_for_number(US_INVALID_NUMBER, _ENGLISH))

    def testCoverage(self):
        # Python version extra tests
        invalid_number = PhoneNumber(country_code=210, national_number=123456L)
        self.assertEqual("", country_name_for_number(invalid_number, "en"))
        # Ensure we exercise all public entrypoints directly
        self.assertEqual("CA", area_description_for_number(US_NUMBER1, "en"))
        self.assertEqual("CA", description_for_valid_number(US_NUMBER1, "en"))
        self.assertEqual("", description_for_valid_number(US_INVALID_NUMBER, "en"))
        # Add in some script and region specific fictional names
        TEST_GEOCODE_DATA['1650960'] = {'en': u'Mountain View, CA',
                                        "en_GB": u'Mountain View California',
                                        "en_US": u'Mountain View, Sunny California',
                                        "en_Latn": u'MountainView'}
        # The following test might one day return "Mountain View California"
        self.assertEqual("United States",
                         description_for_number(US_NUMBER2, _ENGLISH, region="GB"))
        self.assertEqual("Mountain View, Sunny California",
                         description_for_number(US_NUMBER2, _ENGLISH, region="US"))
        self.assertEqual("MountainView",
                         description_for_number(US_NUMBER2, _ENGLISH, script="Latn"))
        self.assertEqual("United States",
                         description_for_number(US_NUMBER2, _ENGLISH, script="Latn", region="GB"))
        # Get a different result when there is a script-specific variant
        self.assertEqual("MountainView",
                         description_for_number(US_NUMBER2, _ENGLISH, script="Latn", region="US"))
        TEST_GEOCODE_DATA['1650960'] = {'en': u'Mountain View, CA'}
