({
    baseUrl: '.',
    mainConfigFile: 'config.js',
    dir: '../src/zeit/web/static/js',
    preserveLicenseComments: false,
    logLevel: 1,
    useSourceUrl: false,
    generateSourceMaps: false,
    optimize: 'uglify2',
    modules: [
        {
            name: 'web.campus/frame'
        },
        {
            name: 'campus'
        },
        {
            name: 'magazin'
        },
        {
            name: 'web.site/frame'
        },
        {
            name: 'site'
        }
    ]
})
