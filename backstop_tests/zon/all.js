// import all zmo files
const article = require('./article.js')
const centerpage = require('./centerpage.js')
const cpContent = require('./cp-content.js')
const feedback = require('./feedback.js')
const parquetFeeds = require('./parquet-feeds.js')
const gallery = require('./gallery.js')
const liveblog = require('./liveblog.js')
const quiz = require('./quiz.js')
const storystream = require('./storystream.js')
const video = require('./video.js')
const base = require('./base.js')
const authorbox = require('./authorbox.js')
const rebrush2019 = require('./rebrush2019.js')

module.exports = [].concat(
  base,
  article,
  centerpage,
  cpContent,
  feedback,
  parquetFeeds,
  gallery,
  liveblog,
  quiz,
  storystream,
  video,
  authorbox,
  rebrush2019
)
