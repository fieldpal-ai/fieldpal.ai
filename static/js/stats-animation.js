// Stats Counter Animation
document.addEventListener('DOMContentLoaded', function() {
    const statsContainers = document.querySelectorAll('.section-stats-container');
    
    // Intersection Observer to detect when stats come into view
    const observerOptions = {
        threshold: 0.3, // Trigger when 30% of the element is visible
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const container = entry.target;
                const statNumbers = container.querySelectorAll('.section-stat-number');
                
                statNumbers.forEach(statNumber => {
                    const targetText = statNumber.textContent.trim();
                    const targetValue = parseFloat(targetText.replace('%', ''));
                    
                    if (!isNaN(targetValue) && !statNumber.dataset.animated) {
                        statNumber.dataset.animated = 'true';
                        animateCounter(statNumber, 0, targetValue, targetText.includes('%') ? '%' : '');
                    }
                });
                
                // Stop observing once animated
                observer.unobserve(container);
            }
        });
    }, observerOptions);
    
    // Observe all stats containers
    statsContainers.forEach(container => {
        observer.observe(container);
    });
    
    // Counter animation function
    function animateCounter(element, start, end, suffix = '') {
        const duration = 2000; // 2 seconds
        const startTime = performance.now();
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(start + (end - start) * easeOutQuart);
            
            element.textContent = currentValue + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = end + suffix;
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
});

