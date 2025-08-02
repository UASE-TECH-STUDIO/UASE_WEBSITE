// Update scripts.js
document.addEventListener("DOMContentLoaded", () => {
    // Intersection Observer for sections to animate when they come into view
    const observerOptions = {
        root: null, // viewport
        rootMargin: "0px",
        threshold: 0.2 // Trigger when 20% of the item is visible
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__fadeInUp'); // Add your desired animation class
                observer.unobserve(entry.target); // Stop observing once animated
            }
        });
    }, observerOptions);

    // Apply observer to sections that should animate when scrolled into view
    // Exclude the hero section as its animations are applied directly in HTML
    document.querySelectorAll('section.my-5:not(.hero-section), section.call-to-action-bg').forEach(section => {
        section.classList.add('animate__animated'); // Add base animation class for observer
        observer.observe(section);
    });

    // The hero section's specific animations are already applied in its HTML
    // No need for the old .content animation if it's still there.
    // If you had it:
    // const content = document.querySelector('.content');
    // if (content) {
    //     // This specific block is now replaced by Animate.css classes on the elements themselves
    //     // You can remove this old animation logic if it was just for a general 'content' class.
    // }
});