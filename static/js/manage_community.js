function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function give_permissions(link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
        },
        success: function (result) {
            update_community_subscribers_list(result)
        }
    })
}

function remove_permissions(link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
        },
        success: function (result) {
            update_community_subscribers_list(result)
        }
    })
}

function update_community_subscribers_list(result) {
    $("#community_subscribers_list").html(result)
}