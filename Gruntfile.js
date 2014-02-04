//Wrapper function with one parameter
module.exports = function(grunt) {

    // Monkey patch delete so it allows deleting outside the current
    // directory, which we need since the grunt binary resides in
    // work/frontend, while the sources are in work/source/zeit.frontend.
	var orig_delete = grunt.file.delete;
	grunt.file.delete = function(filepath, options) {
		options = options || {};
		options['force'] = true;
		orig_delete(filepath, options);
	}

	// local variables
	var project = {
		bannerContent: '/*! <%= pkg.name %> <%= pkg.version %> - ' + '<%= grunt.template.today("yyyy-mm-dd") %> \n' + ' *  License: <%= pkg.license %> */\n',
		name: '<%= pkg.name %>-<%= pkg.version%>',
        binDir: './',
		codeDir: './src/zeit/frontend/',
		jqueryVersion: 'jquery-1.10.2.min.js',
		concatJs: '<%= pkg.name %>.js'
	};
    
    // This is a little ugly, but if we want to run this locally we need
    // an empty binDir. Everything is than expected to be in PATH.
    project.binDir = project.binDir == '.'+'/' ? '' : 'bin/';
    grunt.log.writeln(project.binDir);

	// configuration
	grunt.initConfig({

		// read from package.json
		pkg: grunt.file.readJSON('package.json'),

		// compile sass code
		compass: {
			dev: {
				options: {
					binPath: project.binDir + 'compass',
					cssDir: project.codeDir + 'css',
					debugInfo: true,
					environment: 'development',
					fontsPath: project.codeDir + 'fonts',
					httpPath: "/", // todo: adjust this later in project
					imagesPath: "./src/zeit/frontend/img", // todo: adjust this later in project
					javascriptsPath: "js", // todo: map to the right path
					outputStyle: 'expanded',
					sassDir: './sass',
					require: ['animation'],
					raw: 'preferred_syntax=:sass\n'
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

		//concat files
		concat: {
			options: {
				banner: project.bannerContent
			},
			target: {
				src: ['javascript/modules/*.js'],
				ignores: [],
				dest: project.codeDir + 'js/' + project.concatJs
			}
		},

		//copy scripts
		copy: {
			default: {
				files: [
					//copy non concatinated scripts
					{ expand: true, cwd: './javascript', src: ['**'], dest: project.codeDir + 'js/' }
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
					'javascript/libs/chai.js',
					'javascript/libs/jquery-1.10.2.min.js',
					'javascript/libs/jquery.visible.min.js',
					'javascript/libs/modernizr.custom.42776.js',
					'javascript/libs/require.js',
					'javascript/libs/sasmobile.js',
					'javascript/libs/sjcl.js',
					'javascript/libs/postscribe.min.js',
					'javascript/libs/jquery.bxslider.js',
					'javascript/libs/jquery.easing.1.3.js',
					'javascript/libs/jquery.fitvids.js',
					'javascript/libs/underscore-min.js'
				],
				// devel: true, // accept console etc.
				// phantom: true // phatom js globals
			},
			target: {
				src : ['javascript/**/*.js']
			}
		},

		grunticon: {
			dist: {
				options: {
				src: "./sass/icons",
				dest: project.codeDir + "/css/icons"
			}
		}
    },

		// watch here
		watch: {
			js: {
				files: ['<%= jshint.target.src %>'],
				tasks: ['jshint', 'copy'],
			},
			css: {
				files: ['./sass/*.sass', './sass/**/*.sass', './sass/**/**/*.sass', './sass/*.scss', './sass/**/*.scss', './sass/**/**/*.scss'],
				tasks: ['compass:dev']
			}
		}
	});

	// load node modules
	grunt.loadNpmTasks('grunt-contrib-compass-shabunc');
	grunt.loadNpmTasks('grunt-contrib-concat');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.loadNpmTasks('grunt-photobox');
	grunt.loadNpmTasks('grunt-contrib-copy');
	grunt.loadNpmTasks('grunt-grunticon');

	// register tasks here
	grunt.registerTask('default', ['jshint', 'compass:dev', 'copy', 'grunticon']);
};
