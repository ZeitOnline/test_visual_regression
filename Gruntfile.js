//Wrapper function with one parameter
module.exports = function(grunt) {

    // Monkey patch delete so it allows deleting outside the current
    // directory, which we need since the grunt binary resides in
    // work/frontend, while the sources are in work/source/zeit.frontend.
	var orig_delete = grunt.file.delete;
	grunt.file.delete = function(filepath, options) {
		options = options || {};
		options.force = true;
		orig_delete(filepath, options);
	};

	// local variables
	var project = {
		name: '<%= pkg.name %>-<%= pkg.version%>',
		binDir: './',
		codeDir: './src/zeit/frontend/',
		jqueryVersion: 'jquery-1.10.2.min.js',
		sourceDir: './',
		rubyVersion: '1.9.3'
	};

    // This is a little ugly, but if we want to run this locally we need
    // an empty binDir. Everything is than expected to be in PATH.
    project.binDir = project.binDir == '.'+'/' ? '' : 'bin/';


    // checking ruby version, printing a hint if not standard version
	var sys = require('sys');
	var exec = require('child_process').exec;
	var child;
    child = exec("ruby --version", function (error, stdout, stderr) {
		if( stdout.indexOf(project.rubyVersion) < 0 ) {
			grunt.log.writeln("You're using Ruby " + stdout);
		}
	});


	// configuration
	grunt.initConfig({

		// read from package.json
		pkg: grunt.file.readJSON('package.json'),

		// compile sass code
		compass: {
			// general options
			options: {
				binPath: project.binDir + 'compass',
				cssDir: project.codeDir + 'css',
				fontsPath: project.codeDir + 'fonts',
				httpPath: "/", // todo: adjust this later in project
				imagesPath: project.sourceDir + "src/zeit/frontend/img", // todo: adjust this later in project
				javascriptsPath: "js", // todo: map to the right path
				sassDir: project.sourceDir + 'sass',
				require: ['animation'],
				raw: 'preferred_syntax=:sass\n'
			},
			dev: {
				options: {
					debugInfo: true,
					environment: 'development',
					outputStyle: 'expanded',
				}
			},
			dist: {
				options: {
					debugInfo: false,
					environment: 'production',
					force: true,
					outputStyle: 'compressed',
				}
			}
		},

		//photobox
		photobox: {
			task: {
			options: {
				screenSizes : [ '600x900', '320x800', '1200x900' ],
				urls        : [ 'http://localhost:9090/politik/deutschland/2013-07/demo-article' ],
				useImageMagick: true
				}
			}
		},

		//copy scripts
		copy: {
			default: {
				files: [
					//copy non concatinated scripts
					{ expand: true, cwd: project.sourceDir + 'javascript', src: ['**'], dest: project.codeDir + 'js/' }
				]
			}
		},

		// project wide javascript hinting rules
		jshint: {
			options: {
				'-W015': true, //don't show indentation warnings
				browser: true, // set browser enviroment
				curly: true, // require curly braces around control structure
				eqeqeq: true, // prohibits the use of == and != in favor of === and !==
				forin: true, // requires all for in loops to filter object's items
				indent: 4, // tabsize should be 4 spaces
				jquery: true, // set jquery globals
				latedef: true, // never use vars before they are defined
				loopfunc: true, // no warnings about functions in loops
				trailing: true, // makes it an error to leave a trailing whitespace
				undef: true, // just use defined var, If your variable is defined in another file, you can use /*global ... */ directive to tell JSHint about it
				ignores: [
					project.sourceDir + 'javascript/libs/**/*',
					project.sourceDir + 'javascript/documentation'
				],
				// devel: true, // accept console etc.
				// phantom: true // phatom js globals
			},
			target: {
				src : [project.sourceDir + 'javascript/**/*.js']
			}
		},

		jsdoc: {
			dist : {
				src: [project.sourceDir + 'javascript/modules/**/*.js'], 
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
				keepBuildDir: true,
				baseUrl: project.sourceDir + 'javascript/',
				mainConfigFile: project.sourceDir + 'javascript/app.js',
				out: project.codeDir + 'js/main.js',
				name: "app",
				generateSourceMaps: true,
				preserveLicenseComments: false
			},
			dev: {
				options: {
					optimize: "none"
				}
			},
			dist: {
				options: {
					optimize: "uglify2"
				}
			}
		},

		grunticon: {
			dist: {
				files: [{
					expand: true,
					cwd: project.sourceDir + "sass/icons",
					src: ['*.svg', '*.png'],
					dest: project.codeDir + "/css/icons"
				}],
				options: {
					defaultWidth: "100px",
					defaultHeight: "100px"
				}
			}
		},

		// watch here
		watch: {
			js: {
				files: ['<%= jshint.target.src %>'],
				tasks: ['jshint', 'requirejs:dev', 'copy'],
			},
			css: {
				files: [project.sourceDir + 'sass/*.sass', project.sourceDir + 'sass/**/*.sass', project.sourceDir + 'sass/**/**/*.sass', project.sourceDir + 'sass/*.scss', project.sourceDir + 'sass/**/*.scss', project.sourceDir + 'sass/**/**/*.scss'],
				tasks: ['compass:dev']
			}
		}
	});

	// load node modules
	grunt.loadNpmTasks('grunt-contrib-compass-shabunc');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.loadNpmTasks('grunt-photobox');
	grunt.loadNpmTasks('grunt-contrib-copy');
	grunt.loadNpmTasks('grunt-grunticon');
	grunt.loadNpmTasks('grunt-jsdoc');
	grunt.loadNpmTasks('grunt-sftp-deploy');
	grunt.loadNpmTasks('grunt-contrib-requirejs');

	// register tasks here
	grunt.registerTask('default', ['jshint', 'requirejs:dist', 'compass:dev', 'copy', 'grunticon']);
	grunt.registerTask('production', ['jshint', 'requirejs:dist', 'compass:dist', 'copy', 'grunticon']);
	grunt.registerTask('docs', ['jsdoc', 'sftp-deploy']);

};
