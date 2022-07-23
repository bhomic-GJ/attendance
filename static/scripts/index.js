// document.addEventListener('DOMContentLoaded', () => {
//     let main = document.querySelector(".main");

//     let nav = document.querySelector(".nav");
//     nav.style.transform = "translateX(-100%)";

//     let l1 = document.querySelector(".l1");
//     let l2 = document.querySelector(".l2");
//     let l3 = document.querySelector(".l3");

//     l1.classList = "line";
//     l2.classList = "line";
//     l3.classList = "line";

//     let toggle = 0;

//     let navicon = document.querySelector(".navicon");

//     navicon.onclick = function () {
//         toggle = (toggle + 1) % 2;

//         if (toggle == 0) {
//             l1.classList = "line";
//             l2.classList = "line";
//             l3.classList = "line";

//             nav.style.transform = "translateX(-100%)";
//         }
//         else {
//             l1.classList = "line l1";
//             l2.classList = "line l2";
//             l3.classList = "line l3";

//             nav.style.transform = "none";
//         }
//     }
// });

document.addEventListener('DOMContentLoaded', () => {

    // Get all "navbar-burger" elements
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    // Add a click event on each of them
    $navbarBurgers.forEach(el => {
        el.addEventListener('click', () => {

            // Get the target from the "data-target" attribute
            const target = el.dataset.target;
            const $target = document.getElementById(target);

            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            el.classList.toggle('is-active');
            $target.classList.toggle('is-active');

        });
    });

});