$(document).ready(function () {
    $('.badge-right').click(function () {
        if (event.offsetX > this.offsetWidth - 36) {
            event.preventDefault()
            
            window.location.href = $(event.target).attr('second-href')
        }
    })
})

var $grid = $('.masonry-grid').masonry({
    itemSelector: '.masonry-grid-item',
    percentPosition: true,
    columnWidth: 10,
    gutter: 1
});

$grid.imagesLoaded().progress( function() {
    $grid.masonry();
});