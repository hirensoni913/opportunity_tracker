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
