#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
catalog-ckan/ckanext/ioos_theme/controllers/csw.py
'''


from ckan.lib.base import BaseController, render, _
from ckan.lib import helpers as h
from pylons import config
import os


class CswController(BaseController):
    def index(self):
        return render('csw/admin.html')

    def clear(self):
        config_path = config.get('ckan.ioos_theme.pycsw_config')
        if os.path.exists(config_path):
            try:
                self._clear_pycsw(config_path)
                h.flash_success(_('PyCSW has been cleared'))
            except Exception:
                h.flash_error('Unable to clear PyCSW, see logs for details')
        else:
            h.flash_error('Config for PyCSW doesn\'t exist')
        h.redirect_to(controller='ckanext.ioos_theme.controllers.csw:CswController', action='index')
        return

    def sync(self):
        config_path = config.get('ckan.ioos_theme.pycsw_config')
        if os.path.exists(config_path):
            try:
                self._sync_pycsw(config_path)
                h.flash_success(_('PyCSW has been synchronized'))
            except Exception:
                h.flash_error('Unable to synchronize PyCSW, see logs for details')
        else:
            h.flash_error('Config for PyCSW doesn\'t exist')
        h.redirect_to(controller='ckanext.ioos_theme.controllers.csw:CswController', action='index')
        return

    def _clear_pycsw(self, config_path):
        from bin import ckan_pycsw
        pycsw_config = ckan_pycsw._load_config(config_path)
        ckan_pycsw.clear(pycsw_config)

    def _sync_pycsw(self, config_path):
        from bin import ckan_pycsw
        pycsw_config = ckan_pycsw._load_config(config_path)
        ckan_url = pycsw_config.get('ckan', 'url')
        ckan_pycsw.load(pycsw_config, ckan_url)
