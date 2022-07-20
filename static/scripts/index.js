document.addEventListener('DOMContentLoaded', () => {
    let main = document.querySelector(".main");

    let nav = document.querySelector(".nav");
    nav.style.transform = "translateX(-100%)";

    let l1 = document.querySelector(".l1");
    let l2 = document.querySelector(".l2");
    let l3 = document.querySelector(".l3");

    l1.classList = "line";
    l2.classList = "line";
    l3.classList = "line";

    let toggle = 0;

    let navicon = document.querySelector(".navicon");

    navicon.onclick = function () {
        toggle = (toggle + 1) % 2;

        if (toggle == 0) {
            l1.classList = "line";
            l2.classList = "line";
            l3.classList = "line";

            nav.style.transform = "translateX(-100%)";
        }
        else {
            l1.classList = "line l1";
            l2.classList = "line l2";
            l3.classList = "line l3";

            nav.style.transform = "none";
        }
    }
});