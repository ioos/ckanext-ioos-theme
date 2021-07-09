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

      /* highlight any ancestor elements in the GCMD keyword hierarchy
       * when hovered over */
      $('ul.tree').find('a.tag').hover(
                  function() { $(this).parentsUntil('ul.tree', 'ul').prev().
                                          addClass('highlight-ancestor') },
                  function() { $(this).parentsUntil('ul.tree', 'ul').prev().
                                          removeClass('highlight-ancestor') });
    }
  }
});

