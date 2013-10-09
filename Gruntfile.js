//Wrapper function with one parameter
module.exports = function(grunt) {
	// local variables
	var bannerContent = '/*! <%= pkg.name %> <%= pkg.version %> - ' +
						'<%= grunt.template.today("yyyy-mm-dd") %> \n' +
						' *  License: <%= pkg.license %> */\n',
		name = '<%= pkg.name %>-<%= pkg.version%>',
		codeDir = 'src/zeit/frontend/';
	// configuration
	grunt.initConfig({
		// read from package.json
		pkg: grunt.file.readJSON('package.json'),
		// compile sass code
		compass: {
			dev: {
				options: {
					cssDir: codeDir + 'css',
					debugInfo: true,
					environment: 'development',
					fontsPath: "fonts", // todo: map to the right path
					httpPath: "/", // todp: adjust this later in project
					imagesPath: "img", // todo: adjust this later in project
					javascriptsPath: "js", // todo: map to the right path
					outputStyle: 'expanded',
					sassDir: 'sass',
					raw: 'preferred_syntax=:sass\n'
				}
			}
		},
		concat: {
			options: {
				banner: bannerContent
			},
			target: {
				src: ['<%= jshint.target.src %>'],
				dest: codeDir + 'js/' + name + '.js'
			}
		},
		// project wide javascript hinting rules
		jshint: {
			options: {
				browser: true, // set browser enviroment
				curly: true, // require curly braces around control structure
				// devel: true, // accept console etc. 
				eqeqeq: true, // prohibits the use of == and != in favor of === and !==
				forin: true, // requires all for in loops to filter object's items
				indent: 4, // tabsize should be 4 spaces
				jquery: true, // set jquery globals
				latedef: true, // never use vars before they are defined
				loopfunc: true, // no warnings about functions in loops
				// phantom: true // phatom js globals
				trailing: true, // makes it an error to leave a trailing whitespace
				undef: true // just use defined var, If your variable is defined in another file, you can use /*global ... */ directive to tell JSHint about it
			},
			target: {
				src : ['javascript/**/*.js']
			}
		},
		// watch here
		watch: {
			js: {
				files: ['<%= jshint.target.src %>'],
				tasks: ['jshint', 'concat'],
			},
			css: {
				files: ['sass/**/*.sass'],
				tasks: ['compass:dev']
			}
		}
	});
	// load node modules
	grunt.loadNpmTasks('grunt-contrib-compass');
	grunt.loadNpmTasks('grunt-contrib-concat');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-watch');

	// register tasks here
	grunt.registerTask('default', ['jshint', 'compass:dev', 'concat']);
};