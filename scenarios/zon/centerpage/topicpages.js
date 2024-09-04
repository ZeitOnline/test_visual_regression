const scenarios = [
	{
		url: '/thema/index',
		selectors: [
			'.topic-duo',
			'.cp-region--standard',
			'.cp-region--topic-duo ~ .cp-region--standard',
			'.cp-region--has-topicranking',
		],
	},
	{
		url: '/thema/autotopic',
	},
	{
		url: '/thema/jurastudium',
	},
	{
		url: '/thema/manualtopic',
		selectors: ['.cp-region--standard'],
	},
];

module.exports = scenarios;
