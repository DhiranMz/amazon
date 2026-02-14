document.addEventListener('DOMContentLoaded', function() {

    // --- 1. Message Fading Logic ---
    // Finds the Django messages container and fades it out after 3 seconds
    const messages = document.querySelector('.messages-container');
    if (messages) {
        setTimeout(() => {
            messages.style.transition = "opacity 0.5s ease";
            messages.style.opacity = "0";
            // Wait for the 0.5s transition to finish before removing from DOM
            setTimeout(() => messages.remove(), 500);
        }, 3000);
    }

    // --- 2. Back to Top Logic ---
    const topBtn = document.getElementById("backToTop");

    // Show the button when user scrolls down 300px from the top
    window.onscroll = function() {
        if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
            topBtn.style.display = "block";
        } else {
            topBtn.style.display = "none";
        }
    };

    // Smooth scroll back to top when clicked
    topBtn.onclick = function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
// --- 3. Cart Preview Logic ---
    const cartNav = document.querySelector('.cart-container');
    const preview = document.getElementById('cart-preview');

    if (cartNav && preview) {
        cartNav.addEventListener('mouseenter', () => {
            preview.style.opacity = "1";
        });
    }
    // Get the button
let mybutton = document.getElementById("backToTop");

// When the user scrolls down 400px from the top, show the button
window.onscroll = function() {
    if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
};

// When the user clicks, scroll to the top
mybutton.onclick = function() {
    window.scrollTo({top: 0, behavior: 'smooth'});
};
});