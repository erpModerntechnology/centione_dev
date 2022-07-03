
odoo.define('portal_mission', function(require) {
    'use strict';
    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');
    var lang = utils.get_cookie('website_lang') || $('html').attr('lang') || 'en_US';
    lang = lang.substring(0,2);

    $(document).ready(function(){
        var datepicker_start_date_input = $('#datepicker-container-date-from .input-group.date input');
        var datepicker_end_date_input = $('#datepicker-container-date-to .input-group.date input');
        $(function () {
            var start_date = datepicker_start_date_input.datepicker("getDate");
            var end_date = datepicker_end_date_input.datepicker("getDate");
            if (start_date !='' && end_date !='')
            {
                var period= (end_date-start_date)/(1000*60*60*24);
                $('#input_number_of_days').val(period);
            }
        });

        $('#datepicker-container-date-from').each(function(){

            datepicker_start_date_input.datepicker({
                autoclose: true,
                enableOnReadonly: false,
                todayHighlight: true,
                language: lang,
            });
        });
        $('#datepicker-container-date-to').each(function(){

            datepicker_end_date_input.datepicker({
                autoclose: true,
                enableOnReadonly: false,
                todayHighlight: true,
                language: lang,
            });
        });
        datepicker_start_date_input.on("change", function (e) {
            var start_date = datepicker_start_date_input.datepicker("getDate");
            var end_date = datepicker_end_date_input.datepicker("getDate");
            if (start_date > end_date) {
                datepicker_end_date_input.datepicker("setDate", e.currentTarget.value);
            }
            datepicker_end_date_input.datepicker("option", "minDate", start_date);
        });
        datepicker_end_date_input.on("change", function (e) {
            var start_date = datepicker_start_date_input.datepicker("getDate");
            var end_date = datepicker_end_date_input.datepicker("getDate");
            if (start_date > end_date) {
                datepicker_start_date_input.datepicker("setDate", e.currentTarget.value);
            }
            datepicker_start_date_input.datepicker("option", "maxDate", end_date);
            var period= (end_date-start_date)/(1000*60*60*24);
//            console.log(period);
            $('#input_number_of_days').val(period);
        });

        var missions_headers = $('.o_missions_management_portal_users thead .o_list_record_selector input');
        var missions_rows = $('.o_missions_management_portal_users tbody .o_list_record_selector input');
        missions_rows .prop('checked', false);
        missions_headers .prop('checked', false);
        missions_headers.click(function () {
            if (!$(this).prop('checked')) {
                $('#button_to_remove_missions').addClass('o_hidden');
            } else {
                $('#button_to_remove_missions').removeClass('o_hidden');
            }
            missions_rows.prop('checked', $(this).prop('checked') || false);
        });
        missions_rows.click(function () {
            if (missions_headers.prop('checked') && !$(this).prop('checked')) {
                missions_headers.prop('checked', false);
            }
            var something_checked = false;
            var i;
            for (i=0; i<missions_rows.length; i++) {
                if (missions_rows[i].checked) {
                    something_checked = true;
                    break;
                }
            }
            if (something_checked) {
                $('#button_to_remove_missions').removeClass('o_hidden');
            } else {
                $('#button_to_remove_missions').addClass('o_hidden');
            }
        });
        $('#delete_form').submit(function () {
            if ( ! confirm(_t('Do you really want to remove these records?'))) {
                event.preventDefault();
            }
        });
        $('#delete_mission_id').click(function () {
            if ( ! confirm(_t('Do you really want to remove these records?'))) {
                event.preventDefault();
            } else {
                document.getElementById('to_delete_checkbox').checked = true;
            }
        });
        $('#to_confirm_checkbox').click(function () {
            document.getElementById('to_delete_checkbox').checked = false;
            $('#input_state').val('confirm');
        });
        $('#to_reset_state').click(function () {
            document.getElementById('to_delete_checkbox').checked = false;
            $('#input_state').val('draft');
        });
        $('.o_missions_management_portal_users').on('change', "select[name='start_date_half_day']", function (e) {
            var select = $("select[name='end_date_half_day']");
            select.val(e.currentTarget.value);
        });
    });

});
