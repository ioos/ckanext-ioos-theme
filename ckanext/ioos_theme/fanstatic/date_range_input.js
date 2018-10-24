"use strict";

// this won't work
//ckan.module('ioos_theme_daterange', function($, _) {
//    return {
//        initialize: function() {

// $(function() {
//ckan.module('ioos_theme_daterange', function($, _) {

function make_daterange() {
   // converts the time range inputs to a format that can be
   // used by solr
   var start_val = $('input[name="start_time"]').val();
   var end_val = $('input[name="end_time"]').val();
   // TODO: add input verification on server side

   // TODO: moment.js verfication
   // if both the start and end values are empty, send no time value
   //
   //if (start_val === '' && end_val === '') {
   if (!start_val && !end_val) {
     var set_val = '';
     start_val_scrub = end_val_scrub = null;
   } else {
     var start_val_scrub = !start_val ? '*' : start_val;
     var end_val_scrub = !end_val ? '*' : end_val; 
     /* var set_val = encodeURIComponent("[" + start_val_scrub + " TO " +
                                      end_val_scrub + "]"); */
   }

   $('input#ext_timerange_start').val(start_val_scrub);
   $('input#ext_timerange_end').val(end_val_scrub);
}

ckan.module('ioos_theme_daterange', function($) {
    return {
        initialize: function() {
  var form = $(".search-form");
  $(['ext_timerange_start', 'ext_timerange_end']).each(function(index, item){
    if ($("#ext_timerange").length === 0) {
      $('<input type="hidden" />').attr({'id': item,
                                         'name': item}).appendTo(form);
    }
    });
    make_daterange();

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
                                       //$(this).val(picker.startDate.format('YYYY-MM-DDTHH:mm') + "Z - "
                                       //            + picker.endDate.format('YYYY-MM-DDTHH:mm') + "Z")
                                   });

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
  $(this.el).find('.btn').click(function() { form.submit(); })
  
  
    }
  }

 });

    /*
    $('input[name="datefilter"]').daterangepicker({
       timepicker: true,
       autoUpdateInput: false,
       startDate: moment().startOf('hour'),
       endDate: moment().startOf('hour').add(32, 'hour'),
       locale: {
          cancelLabel: 'Clear',
          format: 'M/DD hh:mm A'
       } 
    });
    */


    // set ISO-like date on range selection
    /*$('input[name="datefilter"]').on('apply.daterangepicker',
                                     function(ev, picker) {
                                         $(this).val(picker.startDate.format('YYYY-MM-DD') + "Z - "
                                                     + picker.endDate.format('YYYY-MM-DD') + "Z")
                                     });

    // clear data selection on cancel
    $('input[name="datefilter"]').on('cancel.daterangepicker',
                                     function(ev, picker) {
                                         $(this).val('')
                                     });
});

*/

/*
$(function() {

  $('input[name="datefilter"]').daterangepicker({
        autoUpdateInput: false,
        locale: {
                  cancelLabel: 'Clear'
              }
    });

  $('input[name="datefilter"]').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
    });

  $('input[name="datefilter"]').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

});
*/
