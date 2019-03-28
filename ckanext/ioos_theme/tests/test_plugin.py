"""Tests for plugin.py."""
from unittest import TestCase
import ckanext.ioos_theme.plugin as plugin


class TestIOOSPlugin(TestCase):

    def test_split_gcmd_tags(self):
        """
        Checks that GCMD separators are split and leading/ending whitespace
        is removed from keywords.
        """
        test_kws = ['OCEANS > OCEAN TEMPERATURE > OCEAN MIXED LAYER',
                    'OCEANS > SALINITY/DENSITY > CONDUCTIVITY',
                    'OCEANS > OCEAN TEMPERATURE > THERMOCLINE',
                    'OCEANS > SALINITY/DENSITY > PYCNOCLINE']
        expected = [{'name': kw} for kw in
                    sorted(['OCEANS', 'OCEAN TEMPERATURE', 'OCEAN MIXED LAYER',
                                                           'THERMOCLINE',
                                      'SALINITY/DENSITY',  'CONDUCTIVITY',
                                                           'PYCNOCLINE'])]
        self.assertEqual(plugin.split_gcmd_tags(test_kws), expected)
        # test simple cases
        expected = [{'name': 'oceans'}]
        self.assertEqual(plugin.split_gcmd_tags([' oceans ']), expected)
        self.assertEqual(plugin.split_gcmd_tags(['oceans']), expected)
