"use strict";

function convert_date_string(date_time_str) {
  // use strict ISO 8601 parsing in moment.js to avoid ambiguities
  var moment_obj =  moment(date_time_str, moment.ISO_8601, true);
  if (moment_obj.isValid) {
    return date_time_str;
  } else {
    return null;
  }
}

function make_daterange() {
   // converts the time range inputs to a format that can be
   // used by solr
   var start_val = $('input#start_time').val();
   var end_val = $('input#end_time').val();
   // TODO: add input verification on server side

   var form_button = $('form[name="datetime-selection"').find('.btn');
   var btn_disabled;
   if (!start_val && !end_val) {
     var set_val = '';
     start_val_scrub = end_val_scrub = null;
       btn_disabled = true;
   } else {
     var start_val_scrub = start_val;
     var end_val_scrub = end_val;
   }

   var date_form = $('form[name="datetime-selection"]');
   var form_btn = date_form.find('.btn');
   date_form.validate()
   if (date_form.valid()) {
     $('input#ext_timerange_start').val(start_val_scrub);
     $('input#ext_timerange_end').val(end_val_scrub);
     form_btn.attr('disabled', false);
   } else {
     form_btn.attr('disabled', true);
   }
}

ckan.module('ioos_theme_daterange', function($) {
    return {
        initialize: function() {
  // toggle date info popover
  $('[data-toggle="popover"]').popover({placement: 'bottom', html: true});
  var form = $(".search-form");
  $(['ext_timerange_start', 'ext_timerange_end']).each(function(index, item){
    var time_elem = $("#" + item);
    if (time_elem.length === 0) {
      $('<input type="hidden" />').attr({'id': item,
                                         'name': item}).appendTo(form);
     }
    });
    var search_params = new URLSearchParams(location.search);
    var param_start_time = search_params.get('ext_timerange_start');
    if (param_start_time !== null) {
        $('input#start_time').val(param_start_time);
    }
    var param_end_time = search_params.get('ext_timerange_end');
    if (param_end_time !== null) {
        $('input#end_time').val(param_end_time);
    }

  $('a[name="datefilter"]').daterangepicker({
    timePicker24Hour: true,
    startDate: moment().startOf('hour'),
    endDate: moment().startOf('hour').add(32, 'hour'),
    locale: {
      format: 'YYYY-MM-DDTHH:mm\\Z'
    }
  });

  // set ISO-like date on range selection
  $('a[name="datefilter"]').on('apply.daterangepicker',
                                   function(ev, picker) {
                                       $('input[name="start_time"]').val(picker.startDate.format('YYYY-MM-DDTHH:mm') + "Z");
                                       $('input[name="end_time"]').val(picker.endDate.format('YYYY-MM-DDTHH:mm') + "Z");
                                       // setting .val doesn't fire the
                                       // on change handler, so we need to
                                       // call the function directly.
                                       make_daterange();
                                   });
  $.validator.setDefaults({
    debug: true,
    success: "valid"
  });

  $.validator.addMethod("isMomentCompatible",
      function (value, element, params) {
        if (this.optional(element) || value === null || value === "*") {
          return true;
        } else {
          var is_valid = moment(value).isValid();
          if (!is_valid) {
            var date_btn = $('form[name="datetime-selection"]').find('.btn');
            date_btn.attr('disabled', true);
          }
          return is_valid;
        }
      });

  var validator = $('form[name="datetime-selection"]').validate({
      rules: {
         start_time: {
             isMomentCompatible: true,
             required: false
         },
         end_time: {
             isMomentCompatible: true,
             required: false
         }
      },
     messages: {
        start_time: { isMomentCompatible: "Start time not valid" },
        end_time: { isMomentCompatible: "End time not valid" }
     }
  });

  make_daterange();

  // clear data selection on cancel
  $('a[name="datefilter"]').on('cancel.daterangepicker',
                                   function(ev, picker) {
                                       $('input[name="start_time"]').val('');
                                       $('input[name="end_time"]').val('');
                                       make_daterange();
                                   });

  $('input[name="start_time"]').on('change', make_daterange);
  $('input[name="end_time"]').on('change', make_daterange);

  // submit the updated form when the Apply button is clicked
  $(this.el).find('.btn').click(function() { form.submit() });


    }
  }

 });
