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

   var form_button = $('form[name="datetime-selection"').find('.btn.apply');
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
   var form_btn = date_form.find(".btn.apply");
   date_form.validate()
   if (date_form.valid()) {
     $('input#ext_timerange_start').val(start_val_scrub);
     $('input#ext_timerange_end').val(end_val_scrub);
     $("input#ext_min_depth").val($("input#min_depth").val())
     $("input#ext_max_depth").val($("input#max_depth").val())
     form_btn.attr('disabled', false);
   } else {
     form_btn.attr('disabled', true);
   }
}

console.log("Plz work!");
ckan.module('ioos_theme_daterange', function($) {
    return {
        initialize: function() {
  console.log("Initialized date range plugin");
  // toggle date info popover
  $('[data-toggle="popover"]').popover({placement: 'bottom', html: true});
  var form = $(".search-form");
  $(['ext_timerange_start', 'ext_timerange_end',
     'ext_min_depth', 'ext_max_depth']).each(function(index, item) {
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
    var param_min_depth = search_params.get('ext_min_depth');
    if (param_start_time !== null) {
        $('input#min_depth').val(param_min_depth);
    }
    var param_max_depth = search_params.get('ext_max_depth');
    if (param_start_time !== null) {
        $('input#max_depth').val(param_max_depth);
    }

  $('a[name="datefilter"]').daterangepicker({
    timePicker24Hour: true,
    startDate: moment().startOf('hour'),
    endDate: moment().startOf('hour').add(32, 'hour'),
    locale: {
      format: 'YYYY-MM-DDTHH:mm\\Z'
    },
    timePicker: true
  });

  // set ISO-like date on range selection
  $('a[name="datefilter"]').on('apply.daterangepicker',
                                   function(ev, picker) {
                                       $('input[name="start_time"]').val(picker.startDate.format('YYYY-MM-DDTHH:mm') + "Z");
                                       $('input[name="end_time"]').val(picker.endDate.format('YYYY-MM-DDTHH:mm') + "Z");
                                       /* setting .val doesn't fire the
                                        * on change handler, so we need to
                                        * call the function directly. */
                                       make_daterange();
                                       /* submit the form after selecting dates
                                        * to make behavior consistent with
                                        * other widgets */
                                       form.submit();
                                   });
  $.validator.setDefaults({
    debug: true,
    success: "valid"
  });

  function comparator(pred_fn) {
    return function(value, element, param) {
      var other_val = $(param).val();
      // empty values are just taken to mean open ended ranges, so are valid
      if (other_val === "" || value === "") {
       return true;
      } else {
       var i = parseFloat(value);
       var j = parseFloat($(param).val());
       return pred_fn(i, j);
      }
    }
  }

  $.validator.addMethod('lessThanEqual',
                        comparator(function(x, y) { return x <= y }),
                        "The value {0} must be less than or equal to {1}");

  $.validator.addMethod('greaterThanEqual',
                        comparator(function(x, y) { return x >= y }),
                        "The value {0} must be greater than or equal to {1}");

  $.validator.addMethod("isMomentCompatible",
      function (value, element, params) {
        if (this.optional(element) || value === null || value === "*") {
          return true;
        } else {
         // use strict ISO 8601 parsing in moment.js to avoid ambiguities
         var is_valid = moment(value, ['YYYY', moment.ISO_8601],
                               true).isValid();
         if (!is_valid) {
            var date_btn = $('form[name="datetime-selection"]').find('.btn.apply');
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
         },
         min_depth: {
             lessThanEqual: "#max_depth",
             required: false
         },
         max_depth: {
             greaterThanEqual: "#min_depth",
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

  for (name of ["start_time", "end_time", "min_depth", "max_depth"]) {
      $('input[name="' + name + '"]').on('change', make_daterange);
  }

  // submit the updated form when the Apply button is clicked
  $(this.el).find('.btn.apply').click(function() { form.submit() });
  $('form[name="datetime-selection"]').on('reset', function() {
                                           $('input#start_time').remove();
                                           $('input#end_time').remove();
                                           /* semi-hack to wait until reset
                                            * event has fired by pushing
                                            * onto the event stack */
                                           window.setTimeout(function() {
                                                              make_daterange();
                                                              form.submit();
                                                             }, 0);
                                          });
    }
  }

});
