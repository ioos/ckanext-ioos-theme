"use strict";

// Utility function to convert date strings to a valid format or return null
function convert_date_string(date_time_str) {
  return moment(date_time_str, moment.ISO_8601, true).isValid() ? date_time_str : null;
}

// Disable hidden fields with no value in a given form
// Empty fields are disabled to exclude them from URL params
function disableEmptyHiddenFields(form) {
  form.find('input[type="hidden"]').each(function () {
    if ($(this).val() === '') {
      $(this).prop('disabled', true);
    }
  });
}

// Validate the form fields and enable/disable the apply button accordingly
function validateFields() {
  const date_form = $('form[name="datetime-selection"]');
  const form_btn = date_form.find(".btn.apply");

  date_form.validate();
  form_btn.attr('disabled', !date_form.valid());
}

ckan.module('ioos_theme_daterange', function ($) {
  return {
    initialize: function () {
      const fieldIds = ['ext_timerange_start', 'ext_timerange_end', 'ext_min_depth', 'ext_max_depth']

      function addHiddenFields(form, fields) {
        fields.forEach((field) => {
          $('<input type="hidden">').attr({ 'id': field, 'name': field }).appendTo(form);
        });
      }

      // Populate form fields from URL parameters
      function populateFormFromUrlParams(params, keys) {
        keys.forEach((key) => {
          let param_value = params.get(key);
          if (param_value !== null) {
            $(`input#${key}`).val(param_value);
          }
        });
      }

      // Register a new validator with a custom comparison function
      function registerValidator(methodName, validationFunc, messageFunc) {
        $.validator.addMethod(methodName, validationFunc, messageFunc);
      }

      // Comparator function for validation
      function comparator(pred_fn) {
        return function (value, element, param) {
          let other_val = $(param).val();
          if (!other_val || !value) return true;
          return pred_fn(parseFloat(value), parseFloat(other_val));
        };
      }

      // Initialization code
      const form = $(".search-form");
      const search_params = new URLSearchParams(location.search);
      addHiddenFields(form, fieldIds);
      populateFormFromUrlParams(search_params, fieldIds);
      $('[data-toggle="popover"]').popover({ placement: 'bottom', html: true });

      // Date range picker initialization
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
        validateFields();
      });

      $.validator.setDefaults({ debug: true, success: "valid" });

      registerValidator('lessThanEqual', 
        comparator((x, y) => x <= y),
        (params, element) => `The value ${$(element).attr('name')} must be less than or equal to ${$(params).attr('name')}`
      );

      registerValidator('greaterThanEqual',
        comparator((x, y) => x >= y),
        (params, element) => `The value ${$(element).attr('name')} must be greater than or equal to ${$(params).attr('name')}`
      );

      registerValidator('isMomentCompatible',
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

      fieldIds.forEach((name) => {
        $(`input[name="${name}"]`).on('input', validateFields);
      });

      $(this.el).find('.btn.apply').click((event) => {
        event.preventDefault();

        const form = $(".search-form");
        const date_form = $('form[name="datetime-selection"]');
      
        fieldIds.forEach((id) => {
          const dateFormField = date_form.find(`input[name="${id}"]`);
          const searchFormField = form.find(`input[name="${id}"]`);
          // Copy the value from visible form to hidden (search) form for submission
          searchFormField.val(dateFormField.val());
        });

        disableEmptyHiddenFields(form);
        form.submit();
      });

      $(this.el).find('.btn.clear').click((event) => {
        event.preventDefault();
        fieldIds.forEach((fieldId) => {
          $(`input#${fieldId}`).val('');
        });
      });
    }
  };
});