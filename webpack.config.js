const webpack = require('webpack'); // to access built-in plugins
const path = require('path');
const production = process.env.NODE_ENV === 'production';

const plugins = [
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        'window.jQuery': 'jquery' // needed only for Velocity
    })
];

module.exports = {
    context: path.resolve(__dirname, 'javascript'),
    entry: {
        'web.campus/frame': ['./web.core/scriptPath', 'web.campus/frame.js'],
        'web.site/frame': ['./web.core/scriptPath', 'web.site/frame.js'],
        arbeit: ['./web.core/scriptPath', './arbeit.js'],
        campus: ['./web.core/scriptPath', './campus.js'],
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
            { test: require.resolve('velocity-animate/velocity.ui'), loader: 'imports-loader?Velocity=velocity' },
            { test: /jquery.inlinegallery/, loader: 'imports-loader?bxSlider' },
            { test: /jquery.clarify/, loader: 'imports-loader?define=>false' },
            { test: /jquery.inview/, loader: 'imports-loader?define=>false' },
            { test: require.resolve('masonry-layout'), loader: 'imports-loader?define=>false' },
            { test: require.resolve('requirejs/require'), loader: 'exports-loader?requirejs,require,define' },
            { test: /\.html$/, exclude: /node_modules/, loader: "mustache-loader" },
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: "eslint-loader",
                        options: { fix: true, failOnError: true }
                    // Disabled until jshint-loader > 0.8.4 to work with webpack 4
                    // @see https://github.com/webpack-contrib/jshint-loader/pull/53
                    // },
                    // {
                    //     loader: "jshint-loader",
                    //     options: { emitErrors: true, failOnHint: true }
                    }
                ]
            }
        ]
    },
    externals: {
        'modernizr': 'Modernizr'
    },
    performance: {
        maxAssetSize: 300000,
        maxEntrypointSize: 300000,
    },
    plugins: plugins,
    resolve: {
        alias: {
            'bxSlider': path.resolve(__dirname, 'javascript/web.core/plugins/jquery.bxslider.js'),
            'masonry': 'masonry-layout',
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
