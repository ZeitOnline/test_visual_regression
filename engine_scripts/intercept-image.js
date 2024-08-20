const fs = require('fs');
const path = require('path');

const IMAGE_URL_RE = /\.gif|\.jpg|\.png|\.webp/i;
const HEADERS_STUB = {};

module.exports = async (page, scenario) => {
	const IMAGE_STUB_URL = path.resolve(__dirname, scenario.interceptImagePath || 'imageStub.jpg');
	const IMAGE_DATA_BUFFER = fs.readFileSync(IMAGE_STUB_URL);
	console.log('intercept image', IMAGE_STUB_URL);
	const intercept = async request => {
		if (IMAGE_URL_RE.test(request.url()) || request.resourceType() === 'image') {
			await request.respond({
				body: IMAGE_DATA_BUFFER,
				headers: HEADERS_STUB,
				status: 200,
			});
		} else {
			request.continue();
		}
	};
	await page.setRequestInterception(true);
	page.on('request', intercept);
};
