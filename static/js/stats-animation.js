// Stats Counter Animation
document.addEventListener('DOMContentLoaded', function() {
    // Counter animation function
    function animateCounter(element, start, end, suffix = '', finalText = null) {
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
                // Use finalText if provided (for cases like "3-4"), otherwise use end + suffix
                element.textContent = finalText !== null ? finalText : (end + suffix);
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
    
    // Handle section stats (existing stats on character image)
    const statsContainers = document.querySelectorAll('.section-stats-container');
    
    const sectionObserver = new IntersectionObserver(function(entries) {
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
                
                sectionObserver.unobserve(container);
            }
        });
    }, {
        threshold: 0.3,
        rootMargin: '0px'
    });
    
    statsContainers.forEach(container => {
        sectionObserver.observe(container);
    });
    
    // Handle stats row (new stats under video) - use same approach as character stats
    const statsRowContainer = document.querySelector('.stats-row-container');
    
    if (statsRowContainer) {
        // Function to animate the stats
        function animateStatsRow(container) {
            const statNumbers = container.querySelectorAll('.stats-number');
            
            statNumbers.forEach(statNumber => {
                if (statNumber.dataset.animated) return;
                
                const targetText = statNumber.textContent.trim();
                
                // Skip animation for "3-4" format (Months to ROI)
                if (targetText.includes('-')) {
                    statNumber.dataset.animated = 'true';
                    return; // Don't animate, just mark as processed
                }
                
                // Handle percentage numbers
                const targetValue = parseFloat(targetText.replace('%', ''));
                if (!isNaN(targetValue)) {
                    statNumber.dataset.animated = 'true';
                    const suffix = targetText.includes('%') ? '%' : '';
                    animateCounter(statNumber, 0, targetValue, suffix);
                }
            });
        }
        
        const statsRowObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStatsRow(entry.target);
                    statsRowObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.3,
            rootMargin: '0px'
        });
        
        statsRowObserver.observe(statsRowContainer);
        
        // Check if already visible on page load
        setTimeout(() => {
            const rect = statsRowContainer.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
            if (isVisible) {
                const firstStat = statsRowContainer.querySelector('.stats-number');
                if (firstStat && !firstStat.dataset.animated) {
                    animateStatsRow(statsRowContainer);
                }
            }
        }, 100);
    }
});

