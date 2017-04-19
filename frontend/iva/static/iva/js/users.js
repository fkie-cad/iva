function check_username() {
    if (!is_empty("username", "empty_username")) {
        user_exists()
    }
    hide_element("user_exists");
    enable_add_user_button();
}

function user_exists() {
    $.ajax({
        type: "GET",
        url: "add_user.html?option=check_user",
        data: {username: $("[name='username']").val()},
        success: function(result) {
            if (result == 'exist') {
                border_red("username");
                show_element("user_exists");
            } else {
                border_green("username");
                hide_element("user_exists");
            }
            enable_add_user_button();
        }
    });
}

function check_password() {
    if (!is_empty("password", "empty_password")) {
        check_repeat()
    }
    enable_add_user_button();
}

function check_repeat() {
    var username_input = document.getElementById("password");
    var repeat_input = document.getElementById("repeat");
    if (username_input.value != repeat_input.value) {
        border_red("repeat");
        show_element("repeat_not_equal");
    } else {
        border_green("repeat");
        hide_element("repeat_not_equal");
    }
    enable_add_user_button();
}

function enable_add_user_button() {
    if (is_element_border_green("username") && is_element_border_green("password") && is_element_border_green("repeat")) {
        show_element("add_user");
        $("#add_user").prop('disabled', false)
    } else {
        hide_element("add_user");
        $("#add_user").prop('disabled', true)
    }
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


function delete_user(username) {
    $.ajax({
        type: "POST",
        url: "users.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            username: username,
            option: 'delete'
        },
        success: function(result) {
            location.reload();
        }
    });
}