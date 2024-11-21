
//Navbar toggle button
function toggler(x) {
    x.classList.toggle("change");
    var sidenav = document.getElementById("mySidenav");
    var opacity = document.getElementById("opacity");
    sidenav.classList.toggle("open");
    opacity.classList.toggle("opa");
    document.body.classList.toggle("opa");
}
//Profile button
function profile() {
    var profileMenu = document.getElementById("profileMenu");
    profileMenu.classList.toggle("active");
    var svg = document.querySelector(".profile-title svg");
    svg.classList.toggle("transform");
}

// Get the modal elements
const modal = document.getElementById('interpretation-modal');
const showModalBtn = document.getElementById('show-interpretation-btn');
const closeModal = document.getElementById('close-modal');

// Show the modal when the button is clicked
showModalBtn.addEventListener('click', () => {
    modal.style.display = 'block';
});

// Hide the modal when the close button (X) is clicked
closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Hide the modal when clicking outside of the modal content
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});


// JavaScript to handle Rhythm Interpretation modal
document.getElementById("show-rhythm-interpretation-btn").addEventListener("click", function() {
    document.getElementById("rhythm-interpretation-modal").style.display = "block";
});

document.getElementById("close-rhythm-modal").addEventListener("click", function() {
    document.getElementById("rhythm-interpretation-modal").style.display = "none";
});

// Close modal when clicking outside of the modal content
window.onclick = function(event) {
    var modal = document.getElementById("rhythm-interpretation-modal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
};
