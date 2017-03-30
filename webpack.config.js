const webpack = require('webpack'); // to access built-in plugins
const path = require('path');
const production = process.env.NODE_ENV === 'production';

let plugins = [
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        'window.jQuery': 'jquery'
    })
];

if ( false ) {
    plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            output: {
                comments: false
            }
        })
    );
}

module.exports = {
    context: path.resolve(__dirname, 'javascript'),
    entry: {
        'web.campus/frame': 'web.campus/frame.js',
        'web.site/frame': 'web.site/frame.js',
        campus: './campus.js',
        magazin: ['./web.core/scriptPath', './magazin.js'],
        site: ['./web.core/scriptPath', './site.js'],
    },
    output: {
        // publicPath: '/static/latest/js/',
        filename: '[name].js',
        path: __dirname + '/src/zeit/web/static/js'
    },
    module: {
        rules: [
            { test: /velocity.ui/, loader: 'imports-loader?Velocity=velocity' },
            { test: /jquery.inlinegallery/, loader: 'imports-loader?bxSlider' },
            { test: /jquery.clarify/, loader: 'imports-loader?define=>false' },
            { test: /jquery.inview/, loader: 'imports-loader?define=>false' },
            { test: /requirejs/, loader: 'script-loader' },
            { test: require.resolve('masonry-layout'), loader: 'imports-loader?define=>false' },
        ]
    },
    externals: {
        'modernizr': 'Modernizr'
    },
    plugins: plugins,
    resolve: {
        alias: {
            'bxSlider': path.resolve(__dirname, 'javascript/web.core/plugins/jquery.bxslider.js'),
            'masonry': 'masonry-layout',
            'requirejs': 'requirejs/require',
            'velocity': 'velocity-animate',
            'velocity.ui': 'velocity-animate/velocity.ui',
            'jquery.clarify': path.resolve(__dirname, 'javascript/web.core/plugins/jquery.clarify.js'),
            'jquery.inview': 'jquery-inview'
        },
        modules: [
            path.resolve(__dirname, 'javascript'),
            'node_modules'
        ]
    },
    watchOptions: {
        ignored: /node_modules/
    }
};
