// import all podcast files
const sso = require('./test-sso.js');
const ssoInteraction = require('./test-sso-interaction.js');

module.exports = [].concat(sso, ssoInteraction);
