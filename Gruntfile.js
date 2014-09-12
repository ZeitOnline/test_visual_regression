// Wrapper function with one parameter
module.exports = function(grunt) {
	"use strict";

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
		name: "<%= pkg.name %>-<%= pkg.version%>",
		sourceDir: "./",
		codeDir: "./src/zeit/frontend/",
		rubyVersion: "1.9.3",
		tasks: {
			production: ["bower", "modernizr", "jshint", "requirejs:dist", "compass:dist", "copy", "icons"],
			development: ["bower", "modernizr", "jshint", "requirejs:dev", "compass:dev", "copy", "icons"],
			docs: ["jsdoc", "sftp-deploy"],
			icons: ["svgmin", "grunticon"],
		}
	};

	// checking ruby version, printing a hint if not standard version
	var sys = require("sys");
	var exec = require("child_process").exec;
	var child;
	child = exec("ruby --version", function (error, stdout, stderr) {
		if ( stdout.indexOf(project.rubyVersion) < 0 ) {
			grunt.log.writeln("You're using Ruby " + stdout);
		}
	});

	// configuration
	grunt.initConfig({

		// read from package.json
		pkg: grunt.file.readJSON("package.json"),

		bower: {
			install: {
				options: {
					targetDir: ".",
					// layout: "byType",
					layout: function(type, component, source) {
						var target = "javascript/vendor";

						if (/\.css$/.test(source)) {
							target = "sass/vendor";
						}

						return target;
					},
					install: true,
					verbose: true,
					cleanTargetDir: false,
					cleanBowerDir: false,
					bowerOptions: {
						production: true,
					}
				}
			}
		},

		// compile sass code
		compass: {
			// general options
			options: {
				cssDir: project.codeDir + "css",
				fontsPath: project.codeDir + "fonts",
				httpPath: "/",
				imagesPath: project.codeDir + "img",
				javascriptsPath: project.codeDir + "js",
				sassDir: project.sourceDir + "sass",
				raw: "preferred_syntax=:sass\n"
			},
			dev: {
				options: {
					sourcemap: true,
					environment: "development",
					outputStyle: "expanded",
				}
			},
			dist: {
				options: {
					force: true,
					environment: "production",
					outputStyle: "compressed",
				}
			}
		},

		// copy files
		copy: {
			// copy plain CSS files
			css: {
				expand: true,
				cwd: project.sourceDir + "sass",
				src: "vendor/*.css",
				dest: project.codeDir + "css/"
			},
			// copy non concatenated scripts, exclude app.js
			scripts: {
				expand: true,
				cwd: project.sourceDir + "javascript",
				src: ["**", "!app.js"],
				dest: project.codeDir + "js/"
			}
		},

		// project wide javascript hinting rules
		jshint: {
			options: {
				jshintrc: ".jshintrc",
				ignores: [
					project.sourceDir + "javascript/libs/**/*",
					project.sourceDir + "javascript/vendor/**/*",
					project.sourceDir + "javascript/documentation/**/*"
				]
			},
			dist: {
				src: [project.sourceDir + "javascript/**/*.js"]
			}
		},

		jsdoc: {
			dist: {
				src: [project.sourceDir + "javascript/modules/**/*.js"],
				options: {
					destination: project.sourceDir + "javascript/documentation"
				}
			}
		},

		"sftp-deploy": {
			build: {
				auth: {
					host: "buildit.zeit.de",
					port: 22,
					authKey: "privateKey"
				},
				src: project.sourceDir + "javascript/documentation",
				dest: "/srv/nginx/javascript/documentation",
				server_sep: "/"
			}
		},

		requirejs: {
			options: {
				keepBuildDir: true,
				baseUrl: project.sourceDir + "javascript/",
				mainConfigFile: project.sourceDir + "javascript/app.js",
				out: project.codeDir + "js/main.js",
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

		svgmin: {
			magazin: {
				expand: true,
				cwd: project.sourceDir + "sass/web.magazin/icons",
				src: ["*.svg"],
				dest: project.sourceDir + "sass/web.magazin/icons-minified"
			},
			website: {
				expand: true,
				cwd: project.sourceDir + "sass/web.site/icons",
				src: ["*.svg"],
				dest: project.sourceDir + "sass/web.site/icons-minified"
			}
		},

		grunticon: {
			options: {
				defaultWidth: "100px",
				defaultHeight: "100px"
			},
			magazin: {
				files: [{
					expand: true,
					cwd: "<%= svgmin.magazin.dest %>",
					src: ["*.svg", "*.png"],
					dest: project.codeDir + "/css/icons"
				}],
				options: {
					datasvgcss: "magazin.data.svg.css",
					datapngcss: "magazin.data.png.css",
					urlpngcss: "magazin.fallback.css",
					previewhtml: "magazin.preview.html",
					loadersnippet: "magazin.loader.js",
					pngfolder: "magazin"
				}
			},
			website: {
				files: [{
					expand: true,
					cwd: "<%= svgmin.website.dest %>",
					src: ["*.svg", "*.png"],
					dest: project.codeDir + "/css/icons"
				}],
				options: {
					datasvgcss: "site.data.svg.css",
					datapngcss: "site.data.png.css",
					urlpngcss: "site.fallback.css",
					previewhtml: "site.preview.html",
					loadersnippet: "site.loader.js",
					pngfolder: "site"
				}
			}
		},

		modernizr: {

			dist: {
				// [REQUIRED] Path to the build you're using for development.
				"devFile": project.sourceDir + "javascript/vendor/modernizr.js",

				// [REQUIRED] Path to save out the built file.
				"outputFile": project.sourceDir + "javascript/libs/modernizr-custom.js",

				// Based on default settings on http://modernizr.com/download/
				"extra": {
					"shiv": true,
					"printshiv": false,
					"load": false, // was true
					"mq": false,
					"cssclasses": true
				},

				// Based on default settings on http://modernizr.com/download/
				"extensibility": {
					"addtest": false,
					"prefixed": false,
					"teststyles": false,
					"testprop": false,
					"testallprops": false,
					"hasevents": false,
					"prefixes": false,
					"domprefixes": false
				},

				// By default, source is uglified before saving
				"uglify": true,

				// Define any tests you want to implicitly include.
				"tests": ["video", "touch"],

				// By default, this task will crawl your project for references to Modernizr tests.
				// Set to false to disable.
				"parseFiles": true,

				// When parseFiles = true, this task will crawl all *.js, *.css, *.scss files, except files that are in node_modules/.
				// You can override this by defining a "files" array below.
				"files": {
					"src": []
				},

				// When parseFiles = true, matchCommunityTests = true will attempt to
				// match user-contributed tests.
				"matchCommunityTests": false,

				// Have custom Modernizr tests? Add paths to their location here.
				"customTests": []
			}

		},

		// watch dog
		watch: {
			js: {
				files: ["<%= jshint.dist.src %>"],
				tasks: ["jshint", "requirejs:dev", "copy"],
			},
			compass: {
				files: ["<%= compass.options.sassDir %>" + "/**/*"],
				tasks: ["compass:dev"]
			},
			icons: {
				files: [project.sourceDir + "sass/**/*.svg"],
				tasks: ["icons"]
			},
			config: {
				files: [
					project.sourceDir + ".jshintrc",
					project.sourceDir + "bower.json",
					project.sourceDir + "Gruntfile.js"
				],
				options: {
					reload: true
				}
			}
		}
	});

	// on watch events configure jshint:all to only run on changed file
	grunt.event.on('watch', function(action, filepath) {
		grunt.config('jshint.all.src', filepath);
	});

	// load node modules
	grunt.loadNpmTasks("grunt-bower-task");
	grunt.loadNpmTasks("grunt-contrib-compass");
	grunt.loadNpmTasks("grunt-contrib-copy");
	grunt.loadNpmTasks("grunt-contrib-jshint");
	grunt.loadNpmTasks("grunt-contrib-requirejs");
	grunt.loadNpmTasks("grunt-contrib-watch");
	grunt.loadNpmTasks("grunt-grunticon");
	grunt.loadNpmTasks("grunt-jsdoc");
	grunt.loadNpmTasks("grunt-modernizr");
	grunt.loadNpmTasks("grunt-sftp-deploy");
	grunt.loadNpmTasks("grunt-svgmin");

	// register tasks here
	grunt.registerTask("default", project.tasks.production);
	grunt.registerTask("production", project.tasks.production);
	grunt.registerTask("dev", project.tasks.development);
	grunt.registerTask("docs", project.tasks.docs);
	grunt.registerTask("icons", project.tasks.icons);

};
