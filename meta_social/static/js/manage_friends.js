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

function sendAjax (link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            query: $("#friends-search-input").val()
        },
        success: function (result) {
            $("#friends-list").html(result)
        }
    })
}

function addBlacklist (e, user_id) {
    let link = '/friends/add_blacklist/' + user_id + '/'
    sendAjax(link)
} 

function removeBlacklist (e, user_id) {
    let link = '/friends/remove_blacklist/' + user_id + '/'
    sendAjax(link)
}

function acceptRequest (e, user_id) {
    let link = '/friends/accept_request/' + user_id + '/'
    sendAjax(link)
    updateNav()
}

function cancelRequest (e, user_id) {
    let link = '/friends/cancel_request/' + user_id + '/'
    sendAjax(link)
    updateNav()
}

function addFriend (e, user_id) {
    let link = '/friends/send_request/' + user_id + '/'
    sendAjax(link)
}

function removeFriend (e, user_id) {
    let link = '/friends/remove_friend/' + user_id + '/'
    sendAjax(link)
} 

$(function () {
    $("#friends-search-input").on('input paste', function (e) {
        $.ajax({
            type: "POST",
            url: '',
            data: {
                csrfmiddlewaretoken: getCookie('csrftoken'),
                query: e.target.value
            },
            success: function (result) {
                $("#friends-list").html(result)
            }
        })
    })
})

function collectionHas(a, b) {
    for(var i = 0, len = a.length; i < len; i ++) {
        if(a[i] == b) return true;
    }
    return false;
}

function findParentBySelector(elm, selector) {
    var all = document.querySelectorAll(selector);
    var cur = elm.parentNode;
    while(cur && !collectionHas(all, cur)) {
        cur = cur.parentNode;
    }
    return cur;
}

function removeBlacklist2 (e, user_id) {
    let link = '/friends/remove_blacklist/' + user_id + '/'
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
        },
        success: function () {
            findParentBySelector(e.target, '.list-group-item').remove()

            let list = document.getElementById('black-list')

            if (list.children.length == 0) {
                list.innerHTML = '<p class="mb-0 text-center">В черном сиске никого нет.</p>'
            }
        }
    })
}

function acceptRequest2 (e, user_id) {
    let link = '/friends/accept_request/' + user_id + '/'
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
        },
        success: function () {
            findParentBySelector(e.target, '.list-group-item').remove()

            let list = document.getElementById('incoming-requests-list')

            if (list.children.length == 0) {
                list.innerHTML = '<p class="mb-0 text-center">Никто не хочет с вами дружить ((</p>'
            }

            updateNav()
        }
    })
}

function cancelRequest2 (e, user_id) {
    let link = '/friends/cancel_request/' + user_id + '/'
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
        },
        success: function () {
            findParentBySelector(e.target, '.list-group-item').remove()

            let list = document.getElementById('outcoming-requests-list')

            if (list.children.length == 0) {
                list.innerHTML = '<p class="mb-0 text-center">Исходящих заявок нет.</p>'
            }

            updateNav()
        }
    })
}

function updateNav () {
    $.ajax({
        type: "POST",
        url: '/ajax/update_nav/',
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
        },
        success: function (result) {
            document.getElementById('left-nav').innerHTML = result
        }
    })
}