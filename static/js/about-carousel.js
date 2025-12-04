// About Page Carousel Functionality
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.about-carousel-button');
    const panels = document.querySelectorAll('.about-carousel-panel');
    const indicators = document.querySelectorAll('.about-carousel-bottom-line');
    let currentIndex = 0;
    let autoCycleInterval = null;
    const CYCLE_DURATION = 5000; // 5 seconds
    
    // Function to show a specific section
    function showSection(index) {
        // Remove active class from all buttons, panels, and indicators
        buttons.forEach(btn => btn.classList.remove('active'));
        panels.forEach(panel => panel.classList.remove('active'));
        indicators.forEach(indicator => indicator.classList.remove('active'));
        
        // Add active class to selected button, panel, and indicator
        if (buttons[index]) {
            buttons[index].classList.add('active');
        }
        if (panels[index]) {
            panels[index].classList.add('active');
        }
        if (indicators[index]) {
            indicators[index].classList.add('active');
        }
        
        currentIndex = index;
    }
    
    // Function to cycle to next section
    function cycleNext() {
        const nextIndex = (currentIndex + 1) % panels.length;
        showSection(nextIndex);
    }
    
    // Function to start auto-cycling
    function startAutoCycle() {
        // Clear any existing interval
        if (autoCycleInterval) {
            clearInterval(autoCycleInterval);
        }
        
        // Start new interval
        autoCycleInterval = setInterval(cycleNext, CYCLE_DURATION);
    }
    
    // Function to stop auto-cycling
    function stopAutoCycle() {
        if (autoCycleInterval) {
            clearInterval(autoCycleInterval);
            autoCycleInterval = null;
        }
    }
    
    // Add click handlers to buttons
    buttons.forEach((button, index) => {
        button.addEventListener('click', function() {
            showSection(index);
            // Restart auto-cycle after manual selection
            stopAutoCycle();
            startAutoCycle();
        });
    });
    
    // Pause auto-cycle on hover
    const carouselSection = document.querySelector('.about-carousel-section');
    if (carouselSection) {
        carouselSection.addEventListener('mouseenter', stopAutoCycle);
        carouselSection.addEventListener('mouseleave', startAutoCycle);
    }
    
    // Initialize: show first section and start auto-cycling
    if (panels.length > 0) {
        showSection(0);
        startAutoCycle();
    }
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        stopAutoCycle();
    });
});

