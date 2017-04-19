/**
 * Created by LABS on 03.08.2016.
 */

$('document').ready(function(){
    verify_if_cpe_assigned_already();
    $('#cpe_matches').jplist({
        itemsBox: '.list'
        ,itemPath: '.list-item'
        ,panelPath: '.jplist-panel'
    });

    var previous_selected_cpe = $(this);
    $("body").on('click', '.cpe', function () {
        var selected_cpe = $(this);
        var cpe_str = selected_cpe.attr('value').replace(/'/g, '"');
        var cpe_json = JSON.parse(cpe_str);
        if (selected_cpe.css('color') == 'rgb(0, 0, 0)') {
            selected_cpe.css('color','green');
            previous_selected_cpe.css('color', 'black');
            previous_selected_cpe = selected_cpe;
            $("[name='vendor']").val(cpe_json.vendor);
            $("[name='product']").val(cpe_json.product);
            $("[name='version']").val(cpe_json.version);
            $("[name='update']").val(cpe_json.update);
            $("[name='edition']").val(cpe_json.edition);
            $("[name='sw_edition']").val(cpe_json.sw_edition);
            $("[name='target_sw']").val(cpe_json.target_sw);
            $("[name='target_hw']").val(cpe_json.target_hw);
            $("[name='other']").val(cpe_json.other);
            $("[name='language']").val(cpe_json.language);
            verify_if_cpe_assigned_already();
        }
    });

});

function verify_if_cpe_assigned_already() {
    $.ajax({
        type: "POST",
        url: "assign_cpe.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            part: $("[name='part']").val(),
            vendor: $("[name='vendor']").val(),
            product: $("[name='product']").val(),
            version: $("[name='version']").val(),
            update: $("[name='update']").val(),
            edition: $("[name='edition']").val(),
            sw_edition: $("[name='sw_edition']").val(),
            target_sw: $("[name='target_sw']").val(),
            target_hw: $("[name='target_hw']").val(),
            other: $("[name='other']").val(),
            language: $("[name='language']").val(),
            check: true
        },
        success: function(result) {
            var uri_element = document.getElementById('uri_binding');
            var check_element = document.getElementById('check');
            $("#uri_binding").html(result.uri_binding);
            if (result.result == 'exist') {
                $("#check").html('<div class="error-msg">CPE was already assigned to other software product</div>');
                check_element.style.visibility = "visible";
                uri_element.style.color = "red"
            }
            else {
                uri_element.style.color = "#5e5e5e";
                check_element.style.visibility = "hidden";
            }
        }
    });
}
