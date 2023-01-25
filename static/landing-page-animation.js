'use strict';


var tl = gsap.timeline();

function animateElements() {
    tl.from('.img_container', {y: 100, duration: 1, ease: "power2.outIn"})
    .from('img', {scale: 1.3, opacity: 0, duration: 1, ease: "power2.outIn"}, "<");
}



$(document).ready(function() {
    $(".animate-name").addClass("show-image");
     $(".animate-name").css({transform: 'scale(0.33) rotate(5deg)'});
});


