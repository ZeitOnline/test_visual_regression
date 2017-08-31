/*
 *
 * Special javascript for brightcove video-player
 *
*/

// Removing focus
function handleFirstTab(e) {
  if (e.keyCode === 9) {
    document.body.classList.add('user-tabbing');
    window.removeEventListener('keydown', handleFirstTab);
  }
}

window.addEventListener('keydown', handleFirstTab);
