// Wrapper function with one parameter
module.exports = function(grunt) {
    'use strict';

    // Monkey patch delete so it allows deleting outside the current
    // directory, which we need since the grunt binary resides in
    // work/web, while the sources are in work/source/zeit.web.
    var origDelete = grunt.file.delete;
    grunt.file.delete = function(filepath, options) {
        options = options || {};
        options.force = true;
        origDelete(filepath, options);
    };

    // local variables
    var project = {
        name: '<%= pkg.name %>-<%= pkg.version%>',
        sourceDir: './',
        d11nDir: './../zeit.web.d11n/',
        codePath: 'src/zeit/web/static/',
        codeDir: './src/zeit/web/static/',
        rubyVersion: '1.9.3',
        tasks: {
            production: [ 'bower', 'modernizr', 'lint', 'requirejs:dist', 'compass:dist', 'copy', 'svg' ],
            development: [ 'bower', 'modernizr', 'lint', 'requirejs:dev', 'compass:dev', 'copy', 'svg' ],
            docs: [ 'jsdoc', 'sftp-deploy' ],
            svg: [ 'clean', 'svgmin', 'grunticon', 'svgstore' ],
            icons: [ 'clean:icons', 'svgmin', 'grunticon' ],
            symbols: [ 'clean:symbols', 'svgmin:symbols', 'svgstore' ],
            lint: [ 'jshint', 'jscs' ]
        }
    };

    var path = require('path');

    // checking ruby version, printing a hint if not standard version
    var sys = require('sys');
    var exec = require('child_process').exec;
    var child;
    child = exec('ruby --version', function(error, stdout, stderr) {
        if ( stdout.indexOf(project.rubyVersion) < 0 ) {
            grunt.log.writeln('You are using Ruby ' + stdout);
        }
    });

    // we need either this or the "force" option in clean task
    // grunt.file.setBase( project.sourceDir );

    // configuration
    grunt.initConfig({

        // read from package.json
        pkg: grunt.file.readJSON('package.json'),

        bower: {
            install: {
                options: {
                    targetDir: project.sourceDir,
                    layout: function(type, component, source) {
                        // type seems useless - use cheesy quickfix
                        var target = 'javascript/vendor';

                        if (/\.css$/.test(source)) {
                            target = 'sass/vendor';
                        }

                        return target;
                    },
                    install: true,
                    verbose: true,
                    cleanTargetDir: false,
                    cleanBowerDir: false,
                    bowerOptions: {
                        production: true
                    }
                }
            }
        },

        // compile sass code
        compass: {
            // general options
            options: {
                bundleExec: true,
                cssDir: project.codeDir + 'css',
                fontsPath: project.codeDir + 'fonts',
                httpPath: '/',
                imagesPath: project.codeDir + 'img',
                javascriptsPath: project.codeDir + 'js',
                sassDir: project.sourceDir + 'sass',
                sassPath: path.resolve(project.sourceDir + 'sass'),
                raw: 'preferred_syntax=:sass\n'
            },
            dev: {
                options: {
                    specify: [
                        project.sourceDir + 'sass/**/*.s{a,c}ss',
                        '!' + project.sourceDir + 'sass/**/all-old-ie.*',
                        '!' + project.sourceDir + 'sass/**/ie-navi.*'
                    ],
                    sourcemap: true,
                    environment: 'development',
                    outputStyle: 'expanded'
                }
            },
            'dev-with-ie': {
                options: {
                    sourcemap: true,
                    environment: 'development',
                    outputStyle: 'expanded'
                }
            },
            dist: {
                options: {
                    force: true,
                    environment: 'production',
                    outputStyle: 'compressed'
                }
            }
        },

        // copy files
        copy: {
            // copy plain CSS files
            css: {
                expand: true,
                cwd: project.sourceDir + 'sass',
                src: 'vendor/*.css',
                dest: project.codeDir + 'css/'
            },
            d11n: {
                expand: true,
                cwd: project.sourceDir,
                src: project.codePath,
                dest: project.d11nDir + project.codePath
            }
        },

        // project wide javascript hinting rules
        jshint: {
            options: {
                jshintrc: '.jshintrc',
                ignores: [
                    project.sourceDir + 'javascript/libs/**/*',
                    project.sourceDir + 'javascript/vendor/**/*',
                    project.sourceDir + 'javascript/documentation/**/*'
                ]
            },
            dist: {
                src: [ project.sourceDir + 'javascript/**/*.js' ]
            }
        },

        jscs: {
            // src: [ '<%= jshint.dist.src %>' ],
            // restrain to zeit.web.site for the moment
            dist: {
                src: [
                    project.sourceDir + 'javascript/*.js',
                    project.sourceDir + 'javascript/web.core/**/*.js',
                    project.sourceDir + 'javascript/web.site/**/*.js'
                ]
            },
            options: {
                config: '.jscsrc',
                excludeFiles: '<%= jshint.options.ignores %>'
            }
        },

        jsdoc: {
            dist: {
                src: [ project.sourceDir + 'javascript/modules/**/*.js' ],
                options: {
                    destination: project.sourceDir + 'javascript/documentation'
                }
            }
        },

        'sftp-deploy': {
            build: {
                auth: {
                    host: 'buildit.zeit.de',
                    port: 22,
                    authKey: 'privateKey'
                },
                src: project.sourceDir + 'javascript/documentation',
                dest: '/srv/nginx/javascript/documentation',
                server_sep: '/'
            }
        },

        requirejs: {
            options: {
                // keepBuildDir: true,
                baseUrl: project.sourceDir + 'javascript',
                mainConfigFile: project.sourceDir + 'javascript/config.js',
                preserveLicenseComments: false,
                logLevel: 1,
                dir: project.codeDir + 'js',
                modules: [
                    {
                        name: 'magazin'
                    },
                    {
                        name: 'site'
                    }
                ]
            },
            dev: {
                options: {
                    useSourceUrl: false, // true causes a bug in sjcl
                    generateSourceMaps: true,
                    optimize: 'none'
                }
            },
            dist: {
                options: {
                    useSourceUrl: false,
                    generateSourceMaps: false,
                    optimize: 'uglify2'
                }
            }
        },

        clean:{
            options: {
                // needed for grunt_runner to delete outside current working dir
                force: true
            },
            // cleanup minified SVGs, remove orphaned files
            icons: [ '<%= svgmin.magazin.dest %>', '<%= svgmin.website.dest %>' ],
            symbols: [ '<%= svgmin.symbols.dest %>' ],
            // delete unused directories
            legacy: [ project.sourceDir + 'sass/web.*/icons-minified' ]
        },

        svgmin: {
            magazin: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.magazin/icons',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.magazin/icons/_minified'
            },
            website: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.site/icons',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.site/icons/_minified'
            },
            symbols: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.site/svg',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.site/svg/_minified'
            }
        },

        grunticon: {
            options: {
                loadersnippet: 'grunticon.loader.js',
                defaultWidth: '100px',
                defaultHeight: '100px'
            },
            magazin: {
                files: [{
                    expand: true,
                    cwd: '<%= svgmin.magazin.dest %>',
                    src: [ '*.svg', '*.png' ],
                    dest: project.codeDir + 'css/icons'
                }],
                options: {
                    datasvgcss: 'magazin.data.svg.css',
                    datapngcss: 'magazin.data.png.css',
                    urlpngcss: 'magazin.fallback.css',
                    previewhtml: 'magazin.preview.html',
                    pngfolder: 'magazin'
                }
            },
            website: {
                files: [{
                    expand: true,
                    cwd: '<%= svgmin.website.dest %>',
                    src: [ '*.svg', '*.png' ],
                    dest: project.codeDir + 'css/icons'
                }],
                options: {
                    datasvgcss: 'site.data.svg.css',
                    datapngcss: 'site.data.png.css',
                    urlpngcss: 'site.fallback.css',
                    previewhtml: 'site.preview.html',
                    pngfolder: 'site'
                }
            }
        },

        svgstore: {
            options: {
                prefix : 'svg-', // This will prefix each ID
                // will add and overide the the default xmlns="http://www.w3.org/2000/svg" attribute to the resulting SVG
                // symbol: {
                //     viewBox : '0 0 100 100',
                //     xmlns: 'http://www.w3.org/2000/svg'
                // },
                cleanup: [ 'fill' ],
                includedemo: true,
                formatting: {
                    indent_size: 1,
                    indent_char: '  '
                }
            },
            website: {
                src: '<%= svgmin.symbols.dest %>/*.svg',
                dest: project.codeDir + 'css/web.site/icons.svg'
            }
        },

        modernizr: {

            dist: {
                // [REQUIRED] Path to the build you're using for development.
                'devFile': project.sourceDir + 'javascript/vendor/modernizr.js',

                // [REQUIRED] Path to save out the built file.
                'outputFile': project.sourceDir + 'javascript/libs/modernizr-custom.js',

                // Based on default settings on http://modernizr.com/download/
                'extra': {
                    'shiv': true,
                    'printshiv': false,
                    'load': false, // was true
                    'mq': false,
                    'cssclasses': true
                },

                // Based on default settings on http://modernizr.com/download/
                'extensibility': {
                    'addtest': false,
                    'prefixed': false,
                    'teststyles': false,
                    'testprop': false,
                    'testallprops': false,
                    'hasevents': false,
                    'prefixes': false,
                    'domprefixes': false
                },

                // By default, source is uglified before saving
                'uglify': true,

                // Define any tests you want to implicitly include.
                'tests': [ 'video', 'touch', 'csstransforms3d' ],

                // By default, this task will crawl your project for references to Modernizr tests.
                // Set to false to disable.
                'parseFiles': true,

                // When parseFiles = true, this task will crawl all *.js, *.css, *.scss files, except files that are in node_modules/.
                // You can override this by defining a 'files' array below.
                'files': {
                    'src': []
                },

                // When parseFiles = true, matchCommunityTests = true will attempt to
                // match user-contributed tests.
                'matchCommunityTests': false,

                // Have custom Modernizr tests? Add paths to their location here.
                'customTests': []
            }

        },

        // watch dog
        watch: {
            js: {
                files: [ '<%= jshint.dist.src %>', '<%= jshint.options.ignores %>' ],
                tasks: [ 'lint', 'requirejs:dev' ]
            },
            compass: {
                files: [ '<%= compass.options.sassDir %>' + '/**/*.s{a,c}ss' ],
                tasks: [ 'compass:dev' ]
            },
            livereload: {
                // This target doesn't run any tasks
                // But when a file in `dist/css/*` is edited it will trigger the live reload
                // So when compass compiles the files, it will only trigger live reload on
                // the css files and not on the scss files
                files: [ '<%= compass.options.cssDir %>' + '/**/*.css' ],
                options: {
                    livereload: true
                }
            },
            icons: {
                files: [ '<%= svgmin.magazin.cwd %>/*.svg', '<%= svgmin.website.cwd %>/*.svg' ],
                tasks: [ 'icons' ]
            },
            symbols: {
                files: [ '<%= svgmin.symbols.cwd %>/*.svg' ],
                tasks: [ 'symbols' ]
            },
            config: {
                files: [
                    project.sourceDir + '.jscsrc',
                    project.sourceDir + '.jshintrc',
                    project.sourceDir + 'bower.json',
                    project.sourceDir + 'Gruntfile.js'
                ],
                options: {
                    reload: true
                }
            }
        }
    });

    // on watch events configure jshint to only run on changed file
    // grunt.event.on('watch', function(action, filepath) {
    //  grunt.config('jshint.dist.src', filepath);
    // });

    // load node modules
    grunt.loadNpmTasks('grunt-bower-task');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-grunticon');
    grunt.loadNpmTasks('grunt-jscs');
    grunt.loadNpmTasks('grunt-jsdoc');
    grunt.loadNpmTasks('grunt-modernizr');
    grunt.loadNpmTasks('grunt-sftp-deploy');
    grunt.loadNpmTasks('grunt-svgmin');
    grunt.loadNpmTasks('grunt-svgstore');

    // register tasks here
    grunt.registerTask('default', project.tasks.production);
    grunt.registerTask('production', project.tasks.production);
    grunt.registerTask('dev', project.tasks.development);
    grunt.registerTask('docs', project.tasks.docs);
    grunt.registerTask('svg', project.tasks.svg);
    grunt.registerTask('icons', project.tasks.icons);
    grunt.registerTask('symbols', project.tasks.symbols);
    grunt.registerTask('lint', project.tasks.lint);

};
