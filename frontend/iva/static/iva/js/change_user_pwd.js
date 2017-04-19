function check_old_password() {
    $.ajax({
        type: "POST",
        url: "change_user_pwd.html",
        data: {
            username: $("[name='username']").val(),
            old_pwd: $("[name='old_pwd']").val(),
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            verify_old_pwd: true
        },
        success: function(is_pwd_correct) {
            if (is_pwd_correct == 'True') {
                border_green("old_pwd");
                hide_element("wrong_pwd");
            } else {
                border_red("old_pwd");
                show_element("wrong_pwd");
            }
            enable_change_pwd_button();
        }
    });
}

function check_new_password() {
    if (!is_empty("new_pwd", "empty_pwd")) {
        check_repeat()
    }
    enable_change_pwd_button();
}

function check_repeat() {
    var pwd_input = document.getElementById("new_pwd");
    var repeat_input = document.getElementById("repeat");
    if (pwd_input.value != repeat_input.value) {
        border_red("repeat");
        show_element("repeat_not_equal");
    } else {
        border_green("repeat");
        hide_element("repeat_not_equal");
    }
    enable_change_pwd_button();
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

function enable_change_pwd_button() {
    if (is_element_border_green("old_pwd") && is_element_border_green("new_pwd") && is_element_border_green("repeat")) {
        show_element("change_pwd");
        $("#change_pwd").prop('disabled', false)
    } else {
        hide_element("change_pwd");
        $("#change_pwd").prop('disabled', true)
    }
}