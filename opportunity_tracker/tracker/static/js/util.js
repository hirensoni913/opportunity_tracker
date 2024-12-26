function getQueryParams() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.toString();
}
