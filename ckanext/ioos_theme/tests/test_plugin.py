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

    def test_filter_tag_names(self):
        gcmd_kws = ['OCEANS > OCEAN TEMPERATURE > OCEAN MIXED LAYER',
                    'OCEANS > SALINITY/DENSITY > CONDUCTIVITY',
                    'OCEANS  > OCEAN TEMPERATURE > THERMOCLINE',
                    'OCEANS > SALINITY/DENSITY > PYCNOCLINE']

        cf_standard_names = ['sea_water_temperature',
                             'sea_water_electrical_conductivity',
                             'sea_water_density']

        def generate_tag_dict(name):
            return {'vocabulary_id': None, 'state': 'active',
                    'display_name': name, 'name': name,
                    'id': None # would not normally be None, but needs to be invariant
                   }

        other_tags = ['Glider', 'AUV', 'oceans']
        # freeform tags get GCMD keywords returned split up -- replicate this
        # behavior
        split_gcmd = list(plugin.split_gcmd_list(gcmd_kws))
        all_tags = [generate_tag_dict(name) for name in
                    split_gcmd + cf_standard_names + other_tags]
        # don't pass in CF standard names and GCMD KWs - the result should be
        # the same as the sorted list of all tags
        expected_tags_no_filter = [generate_tag_dict(name) for name in
				   set(split_gcmd + cf_standard_names +
                                       other_tags)]
        self.assertEqual(sorted(expected_tags_no_filter,
                                key=lambda d: d['display_name']),
                         plugin.filter_tag_names(all_tags, [], []))

        # now pass in the CF standard names and GCMD keywords.  "oceans"
        # should also be filtered out after splitting GCMD keywords
        self.assertEqual([generate_tag_dict(t) for t in ['AUV', 'Glider']],
                          plugin.filter_tag_names(all_tags, cf_standard_names,
                                                  gcmd_kws))
