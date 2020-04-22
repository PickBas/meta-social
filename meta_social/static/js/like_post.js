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

function likePost(e, post_id) {
    $.ajax({
        type: "POST",
        url: '/like/' + post_id + '/',
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken')
        },
        success: function (result) {
            if (result == 'liked') {
                e.target.classList.remove('btn-outline-danger')
                e.target.classList.add('btn-danger')
                e.target.innerHTML = (Number(e.target.innerHTML.split(' ')[0]) + 1) + ' ♥'
            } else {
                e.target.classList.remove('btn-danger')
                e.target.classList.add('btn-outline-danger')
                e.target.innerHTML = (Number(e.target.innerHTML.split(' ')[0]) - 1) + ' ♥'
            }
        }
    })
}