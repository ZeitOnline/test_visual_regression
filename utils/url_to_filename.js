module.exports = function (url) {
  var concatStr = ''
  var urlParts = url.split('/')
  for (var i = 3; i < urlParts.length; i++) {
    concatStr += '_' + urlParts[i]
  }
  return concatStr
}
