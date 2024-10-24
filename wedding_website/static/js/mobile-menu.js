document.addEventListener('DOMContentLoaded', function () {
    var hamburger = document.getElementById('hamburger');
    var closeMenu = document.getElementById('closeMenu');

    function toggleMenu() {
        var menuItems = document.getElementById("mobileMenu");
        // Change mobileMenu from display: none to display: block to prevent weird loading behavior :shrug:
        var display = window.getComputedStyle(menuItems).display;
        if (display === "none") {
            menuItems.style.display = "block";
        }
        if (menuItems.classList.contains("visible")) {
            menuItems.classList.add("closing"); // Add closing class for animation
            setTimeout(() => {
                menuItems.classList.remove("visible", "closing");
            }, 500); // Timeout matches animation duration
        } else {
            menuItems.classList.remove("closing"); // Ensure closing class is removed if it was added
            menuItems.classList.add("visible");
        }
    }

    // Adding mousedown and touchstart event listeners
    if (hamburger) {
        hamburger.addEventListener('mousedown', toggleMenu);
        hamburger.addEventListener('touchstart', toggleMenu);
    }
    if (closeMenu) {
        closeMenu.addEventListener('mousedown', toggleMenu);
        closeMenu.addEventListener('touchstart', toggleMenu);
    }
});

document.querySelectorAll('.registry-link').forEach(element => {
  element.addEventListener('click', function(event) {
  fetch('/registry-click');
  });
});
