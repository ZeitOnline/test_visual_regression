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
            production: [ 'clean', 'auto_install', 'bower', 'modernizr_builder', 'lint', 'requirejs:dist', 'css', 'copy:css', 'svg' ],
            development: [ 'clean', 'auto_install', 'bower', 'modernizr_builder', 'lint', 'requirejs:dev', 'compass:dev', 'copy:css', 'svg' ],
            docs: [ 'jsdoc', 'sftp-deploy' ],
            svg: [ 'clean:svg', 'svgmin', 'svgstore', 'copy:svg_campus', 'copy:svg_magazin', 'copy:svg_site' ],
            css: [ 'compass:dist', 'compass:amp' ],
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

    // configuration
    grunt.initConfig({

        // read from package.json
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
        compass: {
            // general options
            options: {
                assetCacheBuster: false,
                bundleExec: false,
                cssDir: project.codeDir + 'css',
                fontsDir: project.codeDir + 'fonts',
                httpFontsPath: '../../../latest/fonts',
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
                        // there is still ongoing work pls don't put it in again (as)
                        // '!' + project.sourceDir + 'sass/**/advertorial.*',
                        '!' + project.sourceDir + 'sass/**/unresponsive.*',
                        '!' + project.sourceDir + 'sass/**/all-old-ie.*',
                        '!' + project.sourceDir + 'sass/**/ie-navi.*'
                    ],
                    sourcemap: true,
                    environment: 'development',
                    outputStyle: 'expanded'
                }
            },
            'dev-all': {
                options: {
                    sourcemap: true,
                    environment: 'development',
                    outputStyle: 'expanded'
                }
            },
            'dev-basic': {
                options: {
                    specify: [
                        project.sourceDir + 'sass/**/screen.sass'
                    ],
                    sourcemap: true,
                    environment: 'development',
                    outputStyle: 'expanded'
                }
            },
            amp: {
                options: {
                    specify: [
                        project.sourceDir + 'sass/**/amp.s{a,c}ss'
                    ],
                    force: true,
                    environment: 'production',
                    outputStyle: 'compact'
                }
            },
            dist: {
                options: {
                    specify: [
                        project.sourceDir + 'sass/**/*.s{a,c}ss',
                        '!' + project.sourceDir + 'sass/**/amp.s{a,c}ss'
                    ],
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
            compass: {
                files: [ '<%= compass.options.sassDir %>' + '/**/*.s{a,c}ss' ],
                tasks: [ 'compass:dev' ],
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
                // So when compass compiles the files, it will only trigger live reload on
                // the css files and not on the scss files
                files: [ '<%= compass.options.cssDir %>' + '/**/*.css' ],
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
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-jscs');
    grunt.loadNpmTasks('grunt-jsdoc');
    grunt.loadNpmTasks('grunt-modernizr-builder');
    grunt.loadNpmTasks('grunt-sftp-deploy');
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

        if ( target in config.compass ) {
            grunt.log.writeln('Using task compass:' + target);
            config.watch.compass.tasks = [ 'compass:dev-basic' ];
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
