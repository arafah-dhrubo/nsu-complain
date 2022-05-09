function showSpinner() {
    document.getElementById('loading-display').style.visibility = "visible";
    setTimeout(removeSpinner, 2000)
}

function removeSpinner() {
  document.getElementById('loading-display').style.visibility = "hidden";
}