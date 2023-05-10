'use strict';


var tl = gsap.timeline();

function animateElements() {
    tl.from('.img_container', {y: 100, duration: 1, ease: "power2.outIn"})
    .from('img', {scale: 1.3, opacity: 0, duration: 1, ease: "power2.outIn"}, "<");
}



$(document).ready(function() {
    $(".animate-name").addClass("show-image");
     $(".animate-name").css({transform: 'scale(0.5) rotate(5deg)'});
});

const text = document.querySelector(".typewriter-code");
const letters = text.innerHTML.split("");
text.innerHTML = "";

TweenMax.to(text, letters.length * 0.1, {
  text: letters.join(""),
  ease: Linear.easeNone,
  onComplete: function() {
    text.style.width = "auto";
  }
});






