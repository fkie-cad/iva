/**
 * Created by LABS on 30.08.2016.
 */

$('document').ready(function(){

    $('#alerts').jplist({
	    itemsBox: '.list'
        ,itemPath: '.list-item'
		,panelPath: '.jplist-panel'
	});

});

function send_ajax_post_request(cve_id, software_id, option) {
    $.ajax({
        type: "POST",
        url: "alerts.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            cve_id: cve_id,
            software_id: software_id,
            option: option
        },
        success: function (result) { location.reload(); }
    });
}
function set_cve_as_negative(cve_id, software_id) {
    send_ajax_post_request(cve_id, software_id, 'set_cve_as_negative');
}


function notify(cve_id, sw_id, sw) {
    show_element('sending');
    hide_element('sent_email_failed');
    hide_element('sent_email_ok');
    $('#sending').html('<div class="info-msg">sending alert for ' + sw +  '</div>');
    $.ajax({
        type: "POST",
        url: "alerts.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            software_id: sw_id,
            option: 'notify'
        },
        success: function (result) {
            if (result == 'failed') {
                show_element('sent_email_failed');
                $("#sent_email_failed").html('<div class="error-msg">failed to sent alert for '  + sw + '</div>');
            } else {
                location.reload();
            }
            hide_element('sending')
        }
    });
}

