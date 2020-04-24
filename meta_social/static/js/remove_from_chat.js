function removeFromChat(e, link) {
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
            console.log(to_remove);
        }
    })
}