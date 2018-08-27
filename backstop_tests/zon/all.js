// import all zmo files
const article = require( `./article.js` );
const centerpage = require( `./centerpage.js` );
const cpContent = require( `./cp-content.js` );
const gallery = require( `./gallery.js` );
const liveblog = require( `./liveblog.js` );
const quiz = require( `./quiz.js` );
const storystream = require( `./storystream.js` );
const video = require( `./video.js` );
const base = require( `./base.js` );

module.exports = [].concat(
  base,
  article,
  centerpage,
  cpContent,
  gallery,
  liveblog,
  quiz,
  storystream,
  video
);