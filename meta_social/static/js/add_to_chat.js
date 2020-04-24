function addToChat(e, link) {
    $.ajax({
        type: "POST",
        url: link,
        data: {
            csrfmiddlewaretoken: csr_token,
        },
        success: function () {
            let to_add = e.target.parentNode.parentNode.parentNode;
            if (to_add.tagName === 'DIV') {
                to_add.remove();
            } else {
                to_add = e.target.parentNode.parentNode;
                to_add.remove();
            }
            const amount_to_invite = document.getElementById('friend-list-modal').getElementsByTagName('div').length;
            if (amount_to_invite == 0) {
                $('#AddToConvModal').modal('hide');
            }
        }
    })
}