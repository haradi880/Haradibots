// Initialize AOS (Animate On Scroll) library
AOS.init();

// Menu Toggle functionality
const menuToggle = document.querySelector('.menu-toggle');
const navbar = document.querySelector('.navbar');

menuToggle.addEventListener('click', () => {
    navbar.classList.toggle('active');
    menuToggle.classList.toggle('rotated'); // Trigger the rotation effect for the menu button
});

// Mouse move event for the star crackle effect
const heroSection = document.querySelector('.hero');

heroSection.addEventListener('mousemove', (e) => {
    createStar(e);
});

function createStar(e) {
    const star = document.createElement('div');
    star.classList.add('star');
    star.textContent = '*';  // Using asterisk as the "star"

    // Position the star exactly where the cursor is
    const xPos = e.clientX;
    const yPos = e.clientY;

    star.style.left = `${xPos + randomOffset()}px`;  // Stars closer to cursor (random offset)
    star.style.top = `${yPos + randomOffset()}px`;   // Keep stars within a small range

    // Randomize the size and animation duration for each star
    const size = randomSize();
    const duration = randomDuration();

    star.style.fontSize = `${size}px`;
    star.style.animationDuration = `${duration}s`;

    // Add random colors for each star (crackling effect colors)
    star.style.color = getRandomColor();

    heroSection.appendChild(star);

    // Remove the star after animation ends
    setTimeout(() => {
        star.remove();
    }, duration * 1000); // Remove based on the star's animation duration
}

// Function to generate random color for crackling effect (brighter colors)
function getRandomColor() {
    const colors = ['#FF0000', '#F08000', '#D90000', '#900000', '#580000'];
    return colors[Math.floor(Math.random() * colors.length)]; // Choose from crackling colors
}

// Function to generate random size for stars
function randomSize() {
    return Math.random() * 2 + 10; // Star size between 10px and 16px
}

// Function to generate random animation duration
function randomDuration() {
    return Math.random() * 1.5 + 0.5; // Duration between 0.5s and 2s
}

// Function to generate a random offset for stars to appear close to the cursor
function randomOffset() {
    return Math.random() * 6 - 3; // Random offset between -3px and 3px (smaller distance)
}

// Read more functionality for long descriptions
document.getElementById("read-more-btn").addEventListener("click", function() {
    var longDescription = document.querySelector(".long-description");
    var btn = document.getElementById("read-more-btn");

    if (longDescription.style.display === "none") {
        longDescription.style.display = "block";
        btn.textContent = "Read Less";
    } else {
        longDescription.style.display = "none";
        btn.textContent = "Read More";
    }
});

// Show the refresh message
function showRefreshMessage() {
    const message = document.getElementById('refresh-message');
    message.style.display = 'block';  // Show the message
    message.style.opacity = 1; // Fade in the message

    // Hide the message after 4 seconds (adjust as needed)
    setTimeout(() => {
        message.style.opacity = 0;  // Fade out the message
        setTimeout(() => {
            message.style.display = 'none'; // Hide the message completely
        }, 300); // Wait for the fade-out transition to complete
    }, 4000); // Message stays visible for 4 seconds
}

window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        navbar.classList.remove('active');
        menuToggle.classList.remove('rotated');
    }
});

// window.onload = function() {
//     // Retrieve logged-in user from sessionStorage
//     const loggedInUser = JSON.parse(sessionStorage.getItem('loggedInUser'));
//     const userNameDisplay = document.getElementById('userName');
//     const userIdDisplay = document.getElementById('userIdDisplay');
//     const userEmailDisplay = document.getElementById('userEmailDisplay');
//     const logoutBtn = document.getElementById('logoutBtn');

//     console.log("Checking loggedInUser on page load:", loggedInUser); // Log loggedInUser for debugging

//     if (loggedInUser) {
//         // User is logged in, display user details
//         userNameDisplay.textContent = 'Welcome, ' + loggedInUser.name; // Show the user's name
//         userIdDisplay.textContent = 'User ID: ' + loggedInUser.id; // Show the user ID
//         userEmailDisplay.textContent = 'Email: ' + loggedInUser.email; // Show the email

//         // Hide email and ID by default and show them on hover
//         userIdDisplay.style.display = 'none';
//         userEmailDisplay.style.display = 'none';

//         // Show logout button
//         logoutBtn.style.display = 'inline-block'; 

//         // Add hover effect to show ID and email
//         userNameDisplay.addEventListener('mouseenter', () => {
//             userIdDisplay.style.display = 'block';
//             userEmailDisplay.style.display = 'block';
//         });

//         userNameDisplay.addEventListener('mouseleave', () => {
//             userIdDisplay.style.display = 'none';
//             userEmailDisplay.style.display = 'none';
//         });

//     } else {
//         // If no user is logged in, redirect to login page
//         alert('Please log in to continue.');
//         window.location.href = 'login.html'; // Redirect to login page
//     }

//     showRefreshMessage(); // Show the refresh message on load
// };

// document.getElementById('logoutBtn').addEventListener('click', () => {
//     // Remove user session from sessionStorage
//     sessionStorage.removeItem('loggedInUser'); // Use sessionStorage here for consistency
    
//     // Redirect to login page after logout
//     window.location.href = 'login.html'; 
// });
