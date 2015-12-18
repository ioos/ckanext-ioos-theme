/*
 * ckanext-ioos_theme/ckanext/ioos_theme/fanstatic/dataset_tabs.js
 */
"use strict";

ckan.module('dataset_tabs', function($, _) {
  return {
    initialize: function() {
      $('#dataset-meta').click(function(e) {
        e.preventDefault();
        $(this).tab('show');
      });
      $('#dataset-meta-pane').show();
    }
  }
});

