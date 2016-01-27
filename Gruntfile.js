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
            production: [ 'clean', 'auto_install', 'bower', 'modernizr_builder', 'lint', 'requirejs:dist', 'compass:dist', 'copy', 'svg' ],
            development: [ 'clean', 'auto_install', 'bower', 'modernizr_builder', 'lint', 'requirejs:dev', 'compass:dev', 'copy', 'svg' ],
            docs: [ 'jsdoc', 'sftp-deploy' ],
            svg: [ 'clean:icons', 'clean:symbols', 'svgmin', 'grunticon', 'svgstore' ],
            icons: [ 'clean:icons', 'svgmin:magazin', 'grunticon:magazin' ],
            symbols: [ 'clean:symbols', 'svgmin:site', 'svgstore:site', 'grunticon:site' ],
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
                        '!' + project.sourceDir + 'sass/**/advertorial.*',
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
            }
        },

        // project wide javascript hinting rules
        jshint: {
            options: {
                jshintrc: project.sourceDir + '.jshintrc',
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
                config: project.sourceDir + '.jscsrc',
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
            icons: [ project.sourceDir + 'sass/web.*/icons/_minified' ],
            symbols: [ project.sourceDir + 'sass/web.*/svg*/_minified' ],
            // delete old vendor scripts
            scripts: [ project.sourceDir + 'javascript/vendor' ],
            sass: [ project.sourceDir + 'sass/vendor' ],
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
            // this is only needed for the fallback PNGs for svg4everybody
            // grunticon is not in use here
            site: {
                files: [{
                    expand: true,
                    cwd: '<%= svgmin.site.dest %>',
                    src: [ '*.svg' ],
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
            magazinAmp: {
                src: '<%= svgmin.magazinAmp.dest %>/*.svg',
                dest: project.codeDir + 'css/web.magazin/amp.svg'
            },
            siteAmp: {
                src: '<%= svgmin.siteAmp.dest %>/*.svg',
                dest: project.codeDir + 'css/web.site/amp.svg'
            },
            site: {
                src: '<%= svgmin.site.dest %>/*.svg',
                dest: project.codeDir + 'css/web.site/icons.svg'
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
                files: [ '<%= svgmin.magazin.cwd %>/*.svg' ],
                tasks: [ 'icons' ]
            },
            symbols: {
                files: [ '<%= svgmin.site.cwd %>/*.svg' ],
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
    grunt.loadNpmTasks('grunt-auto-install');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-grunticon');
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
    grunt.registerTask('icons', project.tasks.icons);
    grunt.registerTask('symbols', project.tasks.symbols);
    grunt.registerTask('css', project.tasks.css);
    grunt.registerTask('lint', project.tasks.lint);

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
