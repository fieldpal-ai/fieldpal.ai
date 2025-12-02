// FAQ Expandable Section
document.addEventListener('DOMContentLoaded', function() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        if (!question) return;
        
        question.addEventListener('click', function(e) {
            e.preventDefault();
            const isActive = item.classList.contains('active');
            
            // Toggle the clicked item
            if (isActive) {
                item.classList.remove('active');
            } else {
                // Close all items first
                faqItems.forEach(faqItem => {
                    faqItem.classList.remove('active');
                });
                // Then open the clicked item
                item.classList.add('active');
            }
        });
        
    });
});

