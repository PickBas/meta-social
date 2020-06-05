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

var $grid2 = $('.masonry-files').masonry({
    itemSelector: '.masonry-files-item',
    percentPosition: true,
    columnWidth: 9,
    gutter: 1
});

$grid2.imagesLoaded().progress( function() {
    $grid2.masonry();
});