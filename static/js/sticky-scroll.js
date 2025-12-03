// Sticky Scroll Animation for Challenges Features Section
document.addEventListener('DOMContentLoaded', function() {
    const section = document.querySelector('.challenges-features-section');
    const rows = document.querySelectorAll('.challenges-features-row');
    
    if (!section || rows.length === 0) return;
    
    // Add scroll-triggered animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: [0, 0.1, 0.5, 1]
    };
    
    const rowObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const row = entry.target;
            const textContent = row.querySelector('.challenges-features-hero-copy');
            const imageContainer = row.querySelector('.challenges-features-image-container');
            
            if (entry.isIntersecting) {
                const ratio = entry.intersectionRatio;
                
                // Fade in text as it enters viewport
                if (textContent) {
                    const opacity = Math.min(1, ratio * 2);
                    const translateY = (1 - ratio) * 30;
                    textContent.style.opacity = opacity;
                    textContent.style.transform = `translateY(${translateY}px)`;
                }
                
                // Fade in image with slight delay
                if (imageContainer) {
                    const imageOpacity = Math.min(1, Math.max(0, (ratio - 0.2) * 1.25));
                    const imageTranslateX = row.classList.contains('reverse') 
                        ? (1 - ratio) * -30 
                        : (1 - ratio) * 30;
                    imageContainer.style.opacity = imageOpacity;
                    imageContainer.style.transform = `translateX(${imageTranslateX}px)`;
                }
                
                // Add active class when fully visible
                if (ratio > 0.5) {
                    row.classList.add('active');
                } else {
                    row.classList.remove('active');
                }
            } else {
                // Reset when out of view
                if (textContent) {
                    textContent.style.opacity = '0';
                    textContent.style.transform = 'translateY(30px)';
                }
                if (imageContainer) {
                    imageContainer.style.opacity = '0';
                    imageContainer.style.transform = 'translateX(0px)';
                }
                row.classList.remove('active');
            }
        });
    }, observerOptions);
    
    // Observe each row
    rows.forEach(row => {
        rowObserver.observe(row);
        
        // Initialize styles
        const textContent = row.querySelector('.challenges-features-hero-copy');
        const imageContainer = row.querySelector('.challenges-features-image-container');
        
        if (textContent) {
            textContent.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            textContent.style.opacity = '0';
            textContent.style.transform = 'translateY(30px)';
        }
        
        if (imageContainer) {
            imageContainer.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
            imageContainer.style.opacity = '0';
            imageContainer.style.transform = 'translateX(0px)';
        }
    });
    
    // Check initial visibility
    setTimeout(() => {
        rows.forEach(row => {
            const rect = row.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
            
            if (isVisible) {
                const textContent = row.querySelector('.challenges-features-hero-copy');
                const imageContainer = row.querySelector('.challenges-features-image-container');
                
                if (textContent) {
                    textContent.style.opacity = '1';
                    textContent.style.transform = 'translateY(0)';
                }
                
                if (imageContainer) {
                    imageContainer.style.opacity = '1';
                    imageContainer.style.transform = 'translateX(0)';
                }
            }
        });
    }, 100);
});


