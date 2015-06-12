
$(function() {
  $('a[href*=#]:not([href=#])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');


      if (target.length) {
        diff = Math.abs($(document).scrollTop() - target.offset().top);
        if (diff > 10000) {
            // no animation
            return true;
        }else {
            time = Math.min (diff / 10, 200);

            $('html,body').animate({
              scrollTop: target.offset().top
            }, 200);
            return false;
        }
      }
    }
  });
});