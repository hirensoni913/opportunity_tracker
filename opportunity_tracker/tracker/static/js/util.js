function getQueryParams() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.toString();
}

// Function to generate a random RGB color
function getRandomColor() {
  var r = Math.floor(Math.random() * 256); // Random red value (0-255)
  var g = Math.floor(Math.random() * 256); // Random green value (0-255)
  var b = Math.floor(Math.random() * 256); // Random blue value (0-255)
  return `rgb(${r}, ${g}, ${b})`;
}

// Generate a random color palette with 25 colors
function generateRandomPalette() {
  var colors = [];
  for (var i = 0; i < 25; i++) {
    colors.push(getRandomColor());
  }
  return colors;
}

// Apply opacity to the generated random colors
function applyOpacityToPalette(palette, opacity) {
  return palette.map((color) => chroma(color).alpha(opacity).css());
}

// Animate numbers
function animateNumbers(element, value) {
  anime({
    targets: element[0],
    innerHTML: [0, value], // Animate from 0 to the fetched value
    easing: "easeOutExpo", // Smooth easing
    duration: 1000, // Duration of the animation in ms
    round: 1, // Round numbers to integers
    update: function (anim) {
      element[0].innerHTML = Number(element[0].innerHTML).toLocaleString(); // Format with commas
    },
  });
}
