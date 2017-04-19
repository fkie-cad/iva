/**
 * Created by LABS on 19.01.2017.
 */


function update_task_status(task_name, option) {
    $.ajax({
        type: "POST",
        url: "local_repositories.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            name: task_name,
            option: option
        },
        success: function(result) { location.reload(); }
    });
}


function populate_db() {
    $.ajax({
        type: "POST",
        url: "local_repositories.html",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            name: 'populate_db',
            option: 'populate_db'
        },
        success: function(result) { location.reload(); }
    });
}


function repopulate_db() {
    var is_confirmed = confirm("are you sure you want to repopulate the database? This action may take a couple of hours.");
    if (is_confirmed == true) {
        $.ajax({
            type: "POST",
            url: "local_repositories.html",
            data: {
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                name: 'repopulate_db',
                option: 'repopulate_db'
            },
            success: function (result) {
                location.reload();
            }
        });
    }
}