/**
 * Created by LABS on 20.12.2016.
 */

function is_element_border_green(element_id) {
    var input_element = document.getElementById(element_id);
    return input_element.style.borderColor == "green";
}

function is_element_border_red(element_id) {
    var input_element = document.getElementById(element_id);
    return input_element.style.borderColor == "red";
}

function show_element(element_id) {
    document.getElementById(element_id).style.visibility = "visible";
}

function hide_element(element_id) {
    document.getElementById(element_id).style.visibility = "hidden";
}

function border_green(element_id) {
    document.getElementById(element_id).style.borderColor = "green";
}

function border_red(element_id) {
    document.getElementById(element_id).style.borderColor = "red";
}

function open_popup() {
    var left = (screen.width/2)-(610/2);
    var top = (screen.height/2)-(520/2);
    window.open('', 'popup', 'width=610, height=520, scrollbars=yes, toolbar=no, status=no, ' +
        'resizable=yes, menubar=no, location=no, directories=no, top='+top+', left='+left+'')
}