// Wrapper function with one parameter
module.exports = function(grunt) {
    'use strict';

    // local variables
    var project = {
        name: '<%= pkg.name %>-<%= pkg.version%>',
        sourceDir: __dirname + '/',
        codeDir: __dirname + '/src/zeit/web/static/',
        rubyVersion: '1.9.3',
        tasks: {
            production: [ 'clean', 'auto_install', 'bower', 'modernizr_builder', 'lint', 'requirejs:dist', 'css', 'svg' ],
            development: [ 'clean', 'auto_install', 'bower', 'modernizr_builder', 'lint', 'requirejs:dev', 'sass:dev-all', 'postcss:dist', 'postcss:old-ie', 'copy:css', 'svg' ],
            docs: [ 'jsdoc', 'sftp-deploy' ],
            svg: [ 'clean:svg', 'svgmin', 'svgstore', 'copy:svg_campus', 'copy:svg_magazin', 'copy:svg_site' ],
            css: [ 'sass:dist', 'postcss:dist', 'postcss:old-ie', 'copy:css' ],
            lint: [ 'jshint', 'jscs' ]
        }
    };

    var path = require('path');

    // Autoprefixer
    var autoprefixer = require('autoprefixer')({
        remove: false,
        browsers: [
            'Chrome >= 35',
            'Firefox >= 30',
            'Edge >= 12',
            'Explorer >= 9',
            'iOS >= 7',
            'Safari >= 8',
            'Android 2.3',
            'Android >= 4',
            'Opera >= 12'
        ]
    });
    var autoprefixerOldIe = require('autoprefixer')({
        remove: false,
        browsers: [
            'Explorer <= 8'
        ]
    });

    // configuration
    grunt.initConfig({

        // read from package.json
        project: project,
        pkg: grunt.file.readJSON('package.json'),

        auto_install: {
            all: {
                options: {
                    cwd: project.sourceDir,
                    bower: '--production',
                    npm: false
                }
            }
        },

        bower: {
            js: {
                dest: project.sourceDir + 'javascript/vendor',
                options: {
                    filter: '**/*.js',
                    paths: project.sourceDir
                }
            },
            css: {
                dest: project.sourceDir + 'sass/vendor',
                options: {
                    filter: '**/*.css',
                    paths: project.sourceDir
                }
            }
        },

        // compile sass code
        sass: {
            options: {
                sourceComments: true,
                outputStyle: 'expanded',
                includePaths: [
                    path.resolve(project.sourceDir + 'sass')
                ]
            },
            'dev-minimal': {
                files: [{
                    expand: true,
                    cwd: project.sourceDir + 'sass',
                    src: [ '**/screen.sass' ],
                    dest: project.codeDir + 'css',
                    ext: '.css'
                }]
            },
            'dev-basic': {
                files: [{
                    expand: true,
                    cwd: project.sourceDir + 'sass',
                    src: [
                        '**/screen.sass',
                        '**/amp.sass'
                    ],
                    dest: project.codeDir + 'css',
                    ext: '.css'
                }]
            },
            'dev-all': {
                files: [{
                    expand: true,
                    cwd: project.sourceDir + 'sass',
                    src: [ '**/*.s{a,c}ss' ],
                    dest: project.codeDir + 'css',
                    ext: '.css'
                }]
            },
            // this was needed in the beginning of AMP
            // because the CSS with output style 'compressed' damaged the @font-face declarations somehow
            // this seems to be fixed now
            'amp': {
                options: {
                    sourceComments: false,
                    outputStyle: 'compact'
                },
                files: [{
                    expand: true,
                    cwd: project.sourceDir + 'sass',
                    src: [ '**/amp.sass' ],
                    dest: project.codeDir + 'css',
                    ext: '.css'
                }]
            },
            'dist': {
                options: {
                    sourceComments: false,
                    outputStyle: 'compressed'
                },
                files: [{
                    expand: true,
                    cwd: project.sourceDir + 'sass',
                    src: [ '**/*.s{a,c}ss' ], // , '!**/amp.sass' @see comment above
                    dest: project.codeDir + 'css',
                    ext: '.css'
                }]
            }
        },

        // PostCSS
        postcss: {
            dist: {
                options: {
                    processors: [autoprefixer]
                },
                src: [
                    '<%= project.codeDir %>css/**/*.css',
                    '!<%= project.codeDir %>css/**/all-old-ie.css',
                    '!<%= project.codeDir %>css/**/ie-navi.css'
                ]
            },
            'old-ie': {
                options: {
                    processors: [autoprefixerOldIe]
                },
                src: [
                    '<%= project.codeDir %>css/**/all-old-ie.css',
                    '<%= project.codeDir %>css/**/ie-navi.css'
                ]
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
            svg_campus: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.campus/svg/_minified',
                src: [ '*.svg' ],
                dest: project.codeDir + 'css/svg/web.campus/'
            },
            svg_magazin: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.magazin/svg/_minified',
                src: [ '*.svg' ],
                dest: project.codeDir + 'css/svg/web.magazin/'
            },
            svg_site: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.site/svg/_minified',
                src: [ '*.svg' ],
                dest: project.codeDir + 'css/svg/web.site/'
            }
        },

        // project wide javascript hinting rules
        jshint: {
            options: {
                jshintrc: project.sourceDir + '.jshintrc',
                ignores: [
                    project.sourceDir + 'javascript/libs/**/*',
                    project.sourceDir + 'javascript/vendor/**/*'
                ]
            },
            dist: {
                src: [ project.sourceDir + 'javascript/**/*.js' ]
            }
        },

        jscs: {
            dist: {
                src: [ project.sourceDir + 'javascript/**/*.js' ]
            },
            options: {
                config: project.sourceDir + '.jscsrc',
                excludeFiles: [
                    // omit zeit.web.magazin plugins for the moment
                    project.sourceDir + 'javascript/web.magazin/**/*.js',
                    project.sourceDir + 'javascript/libs/**/*',
                    project.sourceDir + 'javascript/vendor/**/*'
                ]
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
                        name: 'campus'
                    },
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
                    useSourceUrl: true,
                    generateSourceMaps: false,
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
            svg: [ project.sourceDir + 'sass/web.*/**/_minified' ],
            // delete old vendor scripts
            scripts: [ project.sourceDir + 'javascript/vendor' ],
            sass: [ project.sourceDir + 'sass/vendor' ],
            // delete unused directories
            legacy: [
                project.sourceDir + 'sass/web.*/icons',
                project.sourceDir + 'sass/web.*/icons-minified'
            ]
        },

        svgmin: {
            campus: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.campus/svg',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.campus/svg/_minified'
            },
            campusAmp: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.campus/svg-amp',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.campus/svg-amp/_minified'
            },
            magazin: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.magazin/svg',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.magazin/svg/_minified'
            },
            magazinAmp: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.magazin/svg-amp',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.magazin/svg-amp/_minified'
            },
            site: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.site/svg',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.site/svg/_minified'
            },
            siteAmp: {
                expand: true,
                cwd: project.sourceDir + 'sass/web.site/svg-amp',
                src: [ '*.svg' ],
                dest: project.sourceDir + 'sass/web.site/svg-amp/_minified'
            }
        },

        svgstore: {
            options: {
                prefix: 'svg-', // This will prefix each ID
                // will add and overide the the default xmlns="http://www.w3.org/2000/svg" attribute to the resulting SVG
                // symbol: {
                //     viewBox : '0 0 100 100',
                //     xmlns: 'http://www.w3.org/2000/svg'
                // },
                cleanup: [ 'fill', 'fill-opacity', 'stroke', 'stroke-width' ],
                includedemo: true,
                formatting: {
                    indent_size: 1,
                    indent_char: '  '
                }
            },
            campusAmp: {
                src: '<%= svgmin.campusAmp.dest %>/*.svg',
                dest: project.codeDir + 'css/web.campus/amp.svg'
            },
            magazinAmp: {
                src: '<%= svgmin.magazinAmp.dest %>/*.svg',
                dest: project.codeDir + 'css/web.magazin/amp.svg'
            },
            siteAmp: {
                src: '<%= svgmin.siteAmp.dest %>/*.svg',
                dest: project.codeDir + 'css/web.site/amp.svg'
            }
        },

        modernizr_builder: {
            build: {
                options: {
                    config: project.sourceDir + 'modernizr-config.json',
                    dest: project.sourceDir + 'javascript/vendor/modernizr-custom.js'
                }
            }
        },

        // watch dog
        watch: {
            js: {
                files: [ '<%= jshint.dist.src %>', '<%= jshint.options.ignores %>' ],
                tasks: [ 'lint', 'requirejs:dev' ],
                options: {
                    interrupt: true,
                    // needed to call `grunt watch` from outside zeit.web
                    // the watch task runs child processes for each triggered task
                    cwd: {
                        files: __dirname,
                        spawn: __dirname
                    }
                }
            },
            sass: {
                files: [ 'sass/**/*.s{a,c}ss' ],
                tasks: [ 'sass:dev-basic', 'newer:postcss:dist' ],
                options: {
                    interrupt: true,
                    // needed to call `grunt watch` from outside zeit.web
                    // the watch task runs child processes for each triggered task
                    cwd: {
                        files: __dirname,
                        spawn: __dirname
                    }
                },
            },
            svg: {
                files: [ '<%= svgmin.magazin.cwd %>/*.svg', '<%= svgmin.site.cwd %>/*.svg' ],
                tasks: [ 'svg' ],
                options: {
                    // needed to call `grunt watch` from outside zeit.web
                    // the watch task runs child processes for each triggered task
                    cwd: {
                        files: __dirname,
                        spawn: __dirname
                    }
                }
            },
            livereload: {
                // This target doesn't run any tasks
                // But when a file in `dist/css/*` is edited it will trigger the live reload
                // So when sass compiles the files, it will only trigger live reload on
                // the css files and not on the scss files
                files: [ 'src/zeit/web/static/css/**/*.css' ],
                options: {
                    livereload: true
                }
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
    grunt.loadNpmTasks('grunt-auto-install');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-jscs');
    grunt.loadNpmTasks('grunt-jsdoc');
    grunt.loadNpmTasks('grunt-modernizr-builder');
    grunt.loadNpmTasks('grunt-newer');
    grunt.loadNpmTasks('grunt-postcss');
    grunt.loadNpmTasks('grunt-sftp-deploy');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-svgmin');
    grunt.loadNpmTasks('grunt-svgstore');
    grunt.loadNpmTasks('main-bower-files');

    // register tasks here
    grunt.registerTask('default', project.tasks.production);
    grunt.registerTask('production', project.tasks.production);
    grunt.registerTask('dev', project.tasks.development);
    grunt.registerTask('docs', project.tasks.docs);
    grunt.registerTask('svg', project.tasks.svg);
    grunt.registerTask('css', project.tasks.css);
    grunt.registerTask('lint', project.tasks.lint);

    // Change watch task configuration on the fly
    // Grunt runs tasks in a series, meaning a next task won't start until the previous has finished.
    // Since the watch task doesn't ever finish by design, any task after the watch task won't be ran,
    // which is why the watch task isn't a multitask.
    grunt.registerTask('monitor', function(target) {
        var config = grunt.config();

        if ( target in config.sass ) {
            grunt.log.writeln('Using task sass:' + target);
            config.watch.sass.tasks = [ 'sass:' + target ];
        }

        // grunt.log.writeflags(config);
        grunt.config('watch', config.watch);
        grunt.task.run('watch');
    });

/*
 * Nice to have. Keep for later use.
 *
    grunt.registerTask('build', 'Build all, or parts of, the site', function(target) {
        var tasks = {
            css: ['sass', 'autoprefixer'],
            js: ['wrap', 'jshint'],
            default: [
                'clean:build',
                'build:css',
                'build:js',
                'copy:build'
            ]
        };

        grunt.task.run(tasks[target] || tasks['default']);
    });
*/

};
