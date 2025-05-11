// app/static/js/trending.js (Updated with better error handling)
document.addEventListener('DOMContentLoaded', function() {
    const trendingForm = document.getElementById('trending-form');
    const promptInput = document.getElementById('prompt-input');
    const loadingIndicator = document.getElementById('loading-indicator');
    const trendingResults = document.getElementById('trending-results');
    const errorMessage = document.getElementById('error-message');
    const noResults = document.getElementById('no-results');
    const videosContainer = document.getElementById('videos-container');
    const categoryTitle = document.getElementById('category-title');
    const trendDirection = document.getElementById('trend-direction');
    const trendStrength = document.getElementById('trend-strength');
    const trendSummary = document.getElementById('trend-summary');
    const trendInsights = document.getElementById('trend-insights');
    const trendRecommendations = document.getElementById('trend-recommendations');
    
    // Handle form submission
    trendingForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const prompt = promptInput.value.trim();
        if (!prompt) {
            return;
        }
        
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        trendingResults.classList.add('d-none');
        errorMessage.classList.add('d-none');
        noResults.classList.add('d-none');
        
        try {
            // Call the API
            const response = await fetch('/api/trending/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: prompt })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (!data.success) {
                noResults.textContent = data.message || 'No trending videos found for your search. Please try a different category.';
                noResults.classList.remove('d-none');
                return;
            }
            
            // Update the UI with results
            displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = error.message || 'An error occurred while analyzing trends';
            errorMessage.classList.remove('d-none');
        } finally {
            // Hide loading indicator
            loadingIndicator.classList.add('d-none');
        }
    });
    
    function displayResults(data) {
        // Clear previous results
        videosContainer.innerHTML = '';
        
        // Update category title
        categoryTitle.textContent = `Trending in "${data.category}"`;
        
        // Update trend analysis
        const analysis = data.analysis;
        trendDirection.textContent = analysis.trend_direction || 'Trending';
        trendStrength.textContent = `${analysis.trend_strength || 5}/10`;
        trendSummary.textContent = analysis.summary || '';
        trendInsights.textContent = analysis.insights || '';
        trendRecommendations.textContent = analysis.recommendations || '';
        
        // Set badge color based on trend direction
        if (analysis.trend_direction === 'growing') {
            trendDirection.className = 'badge bg-success';
        } else if (analysis.trend_direction === 'declining') {
            trendDirection.className = 'badge bg-danger';
        } else {
            trendDirection.className = 'badge bg-primary';
        }
        
        // Set strength badge color
        const strength = parseInt(analysis.trend_strength || 5);
        if (strength >= 8) {
            trendStrength.className = 'badge bg-success';
        } else if (strength >= 5) {
            trendStrength.className = 'badge bg-warning text-dark';
        } else {
            trendStrength.className = 'badge bg-danger';
        }
        
        // Display videos
        if (data.videos && data.videos.length > 0) {
            data.videos.forEach(video => {
                const videoElement = createVideoElement(video);
                videosContainer.appendChild(videoElement);
            });
        } else {
            videosContainer.innerHTML = '<p>No trending videos found for this category.</p>';
        }
        
        // Show results container
        trendingResults.classList.remove('d-none');
    }
    
    function createVideoElement(video) {
        const videoCard = document.createElement('div');
        videoCard.className = 'video-card';
        
        // Format numbers
        const viewCount = formatNumber(video.viewCount);
        const likeCount = formatNumber(video.likeCount);
        const commentCount = formatNumber(video.commentCount);
        
        videoCard.innerHTML = `
            <a href="https://www.youtube.com/watch?v=${video.id}" target="_blank" class="video-link">
                <div class="video-thumbnail">
                    <img src="${video.thumbnail || 'https://via.placeholder.com/480x360'}" alt="${video.title}">
                    <div class="video-play-button">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8 5V19L19 12L8 5Z" fill="#FF0000"/>
                        </svg>
                    </div>
                </div>
            </a>
            <div class="video-info">
                <h3 class="video-title">${video.title || 'Untitled Video'}</h3>
                <div class="video-channel">${video.channelTitle || 'Unknown Channel'}</div>
                <div class="video-stats">
                    <span>${viewCount} views</span>
                    <span>${likeCount} likes</span>
                    <span>${commentCount} comments</span>
                </div>
            </div>
        `;
        
        return videoCard;
    }
    
    function formatNumber(number) {
        number = parseInt(number, 10);
        if (isNaN(number)) return '0';
        
        if (number >= 1000000) {
            return (number / 1000000).toFixed(1) + 'M';
        } else if (number >= 1000) {
            return (number / 1000).toFixed(1) + 'K';
        } else {
            return number.toString();
        }
    }
});