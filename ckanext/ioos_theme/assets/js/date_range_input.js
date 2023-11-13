"use strict";

function convert_date_string(date_time_str) {
  return moment(date_time_str, moment.ISO_8601, true).isValid() ? date_time_str : null;
}

function make_daterange() {
  let date_form = $('form[name="datetime-selection"]');
  let form_btn = date_form.find(".btn.apply");

  date_form.validate();
  form_btn.attr('disabled', !date_form.valid());

  if (date_form.valid()) {
    ['ext_timerange_start', 'ext_timerange_end', 'ext_min_depth', 'ext_max_depth'].forEach((id) => {
      $(`input#${id}`).val($(`input#${id}`).val());
    });
  }
}

ckan.module('ioos_theme_daterange', function ($) {
  return {
    initialize: function () {
      function addHiddenFields(form, fields) {
        fields.forEach((field) => {
          $('<input type="hidden">').attr({ 'id': field, 'name': field }).appendTo(form);
        });
      }

      function populateFormFromUrlParams(params, keys) {
        keys.forEach((key) => {
          let param_value = params.get(key);
          if (param_value !== null) {
            $(`input#${key}`).val(param_value);
          }
        });
      }

      function registerValidator(methodName, validationFunc, messageFunc) {
        $.validator.addMethod(methodName, validationFunc, messageFunc);
      }

      function comparator(pred_fn) {
        return function (value, element, param) {
          let other_val = $(param).val();
          if (!other_val || !value) return true;
          return pred_fn(parseFloat(value), parseFloat(other_val));
        };
      }

      $('[data-toggle="popover"]').popover({ placement: 'bottom', html: true });

      let form = $(".search-form");
      addHiddenFields(form, ['ext_timerange_start', 'ext_timerange_end', 'ext_min_depth', 'ext_max_depth']);

      let search_params = new URLSearchParams(location.search);
      populateFormFromUrlParams(search_params, ['ext_timerange_start', 'ext_timerange_end', 'ext_min_depth', 'ext_max_depth']);

      $('a[name="datefilter"]').daterangepicker({
        timePicker24Hour: true,
        startDate: moment().startOf('hour'),
        endDate: moment().startOf('hour').add(32, 'hour'),
        locale: {
          format: 'YYYY-MM-DDTHH:mm\\Z'
        },
        timePicker: true
      });

      $('a[name="datefilter"]').on('apply.daterangepicker', function (ev, picker) {
        $('input[name="ext_timerange_start"]').val(picker.startDate.format('YYYY-MM-DDTHH:mm') + "Z");
        $('input[name="ext_timerange_end"]').val(picker.endDate.format('YYYY-MM-DDTHH:mm') + "Z");
        make_daterange();
      });

      $.validator.setDefaults({ debug: true, success: "valid" });

      registerValidator(
        'lessThanEqual',
        comparator((x, y) => x <= y),
        (params, element) => `The value ${$(element).attr('name')} must be less than or equal to ${$(params).attr('name')}`
      );

      registerValidator(
        'greaterThanEqual',
        comparator((x, y) => x >= y),
        (params, element) => `The value ${$(element).attr('name')} must be greater than or equal to ${$(params).attr('name')}`
      );

      registerValidator(
        'isMomentCompatible',
        function (value, element) {
          return !value || moment(value, ['YYYY', moment.ISO_8601], true).isValid();
        },
        "The time value is not valid"
      );

      let validator = $('form[name="datetime-selection"]').validate({
        rules: {
          ext_timerange_start: {
            isMomentCompatible: true,
            required: false
          },
          ext_timerange_end: {
            isMomentCompatible: true,
            required: false
          },
          ext_min_depth: {
            lessThanEqual: "#ext_max_depth",
            required: false
          },
          ext_max_depth: {
            greaterThanEqual: "#ext_min_depth",
            required: false
          }
        },
        messages: {
          ext_timerange_start: { isMomentCompatible: "Start time not valid" },
          ext_timerange_end: { isMomentCompatible: "End time not valid" }
        }
      });

      make_daterange();

      ['ext_timerange_start', 'ext_timerange_end', 'ext_min_depth', 'ext_max_depth'].forEach((name) => {
        $(`input[name="${name}"]`).on('change', make_daterange);
      });

      $(this.el).find('.btn.apply').off('click').click((event) => {
        event.preventDefault();
        form.submit();
      });

      $(this.el).find('.btn.clear').off('click').click((event) => {
        event.preventDefault();
        ['ext_timerange_start', 'ext_timerange_end', 'ext_min_depth', 'ext_max_depth'].forEach((fieldId) => {
          $(`input#${fieldId}`).val('');
        });
        make_daterange();
        form.submit();
      });
    }
  };
});