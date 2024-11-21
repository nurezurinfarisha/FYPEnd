document.addEventListener("DOMContentLoaded", function () {
    const audioPlayer = document.getElementById("audio-player");
    const trackTitle = document.getElementById("track-title");
    const albumArt = document.getElementById("album-art");
    const playPauseBtn = document.querySelector(".play-pause-btn");
    const progressBar = document.querySelector(".progress-bar");
    const progressBarFill = document.querySelector(".progress-bar-fill");
    const volumeControl = document.querySelector(".volume-control input[type='range']");
    let currentTrackId = null; // To keep track of the current track

    let recommendedSongs = []; // Array to store recommended songs
    let currentTrackIndex = 0; // Index to track current song in the recommendations list

    // Load and play the selected track
    function loadTrack(title, filePath, albumArtPath, trackId) {
        if (trackId === currentTrackId) return; // Only load if it's a new track

        currentTrackId = trackId; // Update the current track ID
        const audioSource = document.getElementById("audio-source"); // Get the <source> element
    
        trackTitle.textContent = title || "Unknown Track"; // Fallback if no title provided
        albumArt.src = albumArtPath || "/static/images/default_album_art.png"; // Default album art
    
        // Set the source path on the <source> element and load the audio
        audioSource.src = filePath;
        audioPlayer.load(); // Load the new source into the audio element
        audioPlayer.play().catch(error => {
            console.warn("Auto-play failed. User interaction might be required.", error);
        });
    
        // Set button to pause icon after loading
        playPauseBtn.textContent = "⏸️"; 
    }

    // Function to load track based on the index in the recommendedSongs array
    function loadTrackFromIndex(index) {
        const track = recommendedSongs[index];
        if (track) {
            loadTrack(track.song_title, track.file_path, track.image, track.song_id);
        }
    }

    // Fetch recommended songs from server
    fetch("/recommended-songs")
        .then(response => response.json())
        .then(data => {
            recommendedSongs = data;
            if (recommendedSongs.length > 0) {
                loadTrackFromIndex(currentTrackIndex); // Load the first recommended song
            }
        })
        .catch(error => {
            console.error("Failed to load recommended songs:", error);
        });

    // Play/Pause button functionality
    playPauseBtn.addEventListener("click", function () {
        if (audioPlayer.paused) {
            audioPlayer.play();
            playPauseBtn.textContent = "⏸️"; // Change icon to pause
        } else {
            audioPlayer.pause();
            playPauseBtn.textContent = "▶️"; // Change icon to play
        }
    });

    // Next button functionality
    document.querySelector(".next-btn").addEventListener("click", function () {
        if (recommendedSongs.length > 0) {
            currentTrackIndex = (currentTrackIndex + 1) % recommendedSongs.length;
            loadTrackFromIndex(currentTrackIndex);
        }
    });

    // Previous button functionality
    document.querySelector(".previous-btn").addEventListener("click", function () {
        if (recommendedSongs.length > 0) {
            currentTrackIndex = (currentTrackIndex - 1 + recommendedSongs.length) % recommendedSongs.length;
            loadTrackFromIndex(currentTrackIndex);
        }
    });

    // Update progress bar as audio plays
    audioPlayer.addEventListener("timeupdate", function () {
        const currentTime = formatTime(audioPlayer.currentTime);
        const duration = formatTime(audioPlayer.duration);
    
        document.getElementById("current-time").textContent = currentTime;
        document.getElementById("total-duration").textContent = duration;
    
        const progressPercentage = (audioPlayer.currentTime / audioPlayer.duration) * 100;
        progressBarFill.style.width = progressPercentage + "%";
    });

    // Format time in minutes and seconds
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
        return `${minutes}:${secs}`;
    }

    // Allow seeking in the audio by clicking the progress bar
    progressBar.addEventListener("click", function (e) {
        const clickPosition = e.offsetX / progressBar.offsetWidth;
        audioPlayer.currentTime = clickPosition * audioPlayer.duration;
    });

    // Volume control
    volumeControl.addEventListener("input", function () {
        audioPlayer.volume = volumeControl.value / 100;
    });

    // Reset play/pause button icon when audio ends
    audioPlayer.addEventListener("ended", function () {
        playPauseBtn.textContent = "▶️"; // Reset to play icon
        progressBarFill.style.width = "0%"; // Reset progress bar
    });
});
