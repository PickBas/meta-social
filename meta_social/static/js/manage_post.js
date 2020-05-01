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

autosize(document.getElementById("updated-post-text"));

function remove_post(e, link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken')
        },
        success: function () {
            e.target.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode
                .remove();
        }
    })

}

function edit_post(e, link) {
    let edited_text = document.getElementById("updated-post-text");
    let old_text = document.getElementById("id-post-text");
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: getCookie('csrftoken'),
            text: edited_text.value
        },
        success: function () {
            old_text.innerText = edited_text.value;
        }
    })
}

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

function sendCommentInd(e) {
    let form = $(e.target)
    form = form.serializeArray().reduce(function(obj, item) {
        obj[item.name] = item.value
        return obj
    }, {})
    
    if (form['text'] && form['csrfmiddlewaretoken'] && form['post_id']) {
        $.ajax({
            type: "POST",
            url: '/post/' + form['post_id'] + '/send_comment/',
            data: {
                csrfmiddlewaretoken: form['csrfmiddlewaretoken'],
                text: form['text']
            },
            success: function (result) {
                $(e.target).children('.comment-input').val('')
                let post = findParentBySelector(e.target, '.post-item')
                post.parentNode.innerHTML = result
            }
        })
    }

    return false
}