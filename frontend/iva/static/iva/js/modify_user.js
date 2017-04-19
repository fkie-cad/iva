/**
 * Created by LABS on 20.12.2016.
 */

function check_new_username() {
    var old_username = document.getElementById('old_username');
    var new_username = document.getElementById('username');
    if (old_username.value != new_username.value) {
        if (!is_empty("username", "empty_username")) {
            new_user_exists()
        }
    } else {
        border_green('username');
        hide_element('empty_username');
    }
    hide_element("user_exists");
    enable_modify_user_button();
}

function new_user_exists() {
    $.ajax({
        type: "GET",
        url: "modify_user.html?option=check_user",
        data: {username: $("[name='username']").val()},
        success: function(result) {
            if (result == 'exist') {
                border_red("username");
                show_element("user_exists");
            } else {
                border_green("username");
                hide_element("user_exists");
            }
            enable_modify_user_button();
        }
    });
}

function is_empty(input_element_id, empty_msg_element_id) {
    var input_element = document.getElementById(input_element_id);
    if (input_element.value == '') {
        border_red(input_element_id);
        show_element(empty_msg_element_id);
        return true;
    }
    border_green(input_element_id);
    hide_element(empty_msg_element_id);
    return false;
}

function enable_modify_user_button() {
    if (is_element_border_red("username")) {
        hide_element("modify_user");
        $("#modify_user").prop('disabled', true)
    } else {
        show_element("modify_user");
        $("#modify_user").prop('disabled', false)
    }
}