// Selectors for the recommendation slider
const recommendationContainer = document.querySelector('.recommendation-container');
const songCards = document.querySelectorAll('.song-card');
const itemsPerSlide = 3; // Adjust to control how many items are visible in each slide
let currentSlide = 0;

// Function to update visible cards based on the current slide
function updateSlider() {
    const start = currentSlide * itemsPerSlide;
    const end = start + itemsPerSlide;

    songCards.forEach((card, index) => {
        card.style.display = (index >= start && index < end) ? 'block' : 'none';
    });
}

// Slide left function
function slideLeft() {
    currentSlide = (currentSlide > 0) ? currentSlide - 1 : Math.ceil(songCards.length / itemsPerSlide) - 1;
    updateSlider();
}

// Slide right function
function slideRight() {
    currentSlide = (currentSlide < Math.ceil(songCards.length / itemsPerSlide) - 1) ? currentSlide + 1 : 0;
    updateSlider();
}

// Initialize the slider by displaying the first set of items
updateSlider();

// Function to play a song
function playSong(filePath, songTitle, albumArt) {
    console.log("Play button clicked for:", songTitle, "with file path:", filePath);

    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById("audio-source");
    const trackTitle = document.getElementById('track-title');
    const albumArtImg = document.getElementById('album-art');

    if (audioPlayer && audioSource) {
        // Set new source
        audioSource.src = filePath;
        console.log("Setting audio source to:", filePath);

        // Reload and attempt to play
        audioPlayer.load();  // Necessary to reload the updated source
        audioPlayer.play()
            .then(() => {
                console.log("Playback started for:", songTitle);
                audioPlayer.currentTime = 0; // Ensure playback starts from the beginning
            })
            .catch(error => {
                console.warn("Playback failed, possibly due to browser auto-play policies:", error);
                alert("Playback failed. Please interact with the page first to allow playback.");
            });

        // Update UI with track info
        if (trackTitle) trackTitle.textContent = songTitle || "Unknown Track";
        if (albumArtImg) {
            albumArtImg.src = albumArt || "/static/images/default_album_art.png";
            albumArtImg.style.display = "block"; // Ensure album art is visible
        }
    } else {
        console.error("Audio player or source element not found.");
    }
}

// Add event listeners to each play button in the recommendation section
document.addEventListener('DOMContentLoaded', function () {
    // Ensure buttons are available in the DOM
    const playButtons = document.querySelectorAll('.play-button');
    if (playButtons.length === 0) {
        console.error("No play buttons found. Check if recommendation songs are loaded correctly.");
        return;
    }

    playButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Get the file path, title, and album art from the data attributes
            const filePath = this.getAttribute('data-file-path');
            const songTitle = this.getAttribute('data-song-title');
            const albumArt = this.getAttribute('data-album-art');

            // Check if filePath is valid
            if (!filePath) {
                console.error("File path is missing for the selected song.");
                alert("Audio file not available.");
                return;
            }

            // Call playSong directly on button click
            playSong(filePath, songTitle, albumArt);
        });
    });
});
