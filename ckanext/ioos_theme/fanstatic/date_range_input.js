"use strict";

// this won't work
//ckan.module('ioos_theme_daterange', function($, _) {
//    return {
//        initialize: function() {

$(function() {
  console.log("work plz kekekeke");
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
                                       //$(this).val(picker.startDate.format('YYYY-MM-DDTHH:mm') + "Z - "
                                       //            + picker.endDate.format('YYYY-MM-DDTHH:mm') + "Z")
                                   });

  // clear data selection on cancel
  $('a[name="datefilter"]').on('cancel.daterangepicker',
                                   function(ev, picker) {
                                       $('input[name="start_time"]').val('');
                                       $('input[name="end_time"]').val('');
                                   });
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
