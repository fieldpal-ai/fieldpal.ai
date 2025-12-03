// Video Player with Splash Screen
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('video-wrapper');
    const splashOverlay = document.getElementById('video-splash-overlay');
    const playButton = document.getElementById('video-play-button');
    const embedContainer = document.getElementById('video-embed-container');
    const youtubeVideo = document.getElementById('youtube-video');
    
    // YouTube video ID extracted from https://youtu.be/67UUkZCNzmY
    const videoId = '67UUkZCNzmY';
    
    if (!videoWrapper || !splashOverlay || !playButton || !embedContainer || !youtubeVideo) {
        return;
    }
    
    function playVideo() {
        // Hide splash overlay
        splashOverlay.classList.add('hidden');
        
        // Show embed container
        embedContainer.style.display = 'block';
        
        // Load YouTube embed with autoplay
        const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
        youtubeVideo.src = embedUrl;
    }
    
    // Add click handlers
    playButton.addEventListener('click', playVideo);
    splashOverlay.addEventListener('click', function(e) {
        // Only trigger if clicking on overlay itself, not the button
        if (e.target === splashOverlay) {
            playVideo();
        }
    });
});


