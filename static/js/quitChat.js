function quitChat(e, link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: csr_token,
        },
        success: function () {
            let to_remove = e.target.parentNode.parentNode.parentNode;
            if (to_remove.tagName === 'DIV') {
                to_remove.remove();
            } else {
                to_remove = e.target.parentNode.parentNode;
                to_remove.remove();
            }
            const amount_to_invite = document.getElementById('chat-list').getElementsByTagName('div').length;
            if (amount_to_invite == 0) {
                document.getElementById('chat-list').innerHTML = '<p class="mb-0 text-center">Список чатов пуст</p>'
            }
        }
    })
}