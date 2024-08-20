const zonEslintConfig = require('@zeitonline/eslint-config');

module.exports = [
    ...zonEslintConfig,
    {
        // Add project-specific overrides here, e.g. ignore certain files
        ignores: ['backstop-settings.js', '**/index_bundle.js', 'data/html_report/*']
    }
];