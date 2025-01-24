const scenarios = [
  {
    url: '/zeit-online/centerpage/index?ad-debug',
    selectors: ['.ad-container[data-type="desktop"]'],
    selectorExpansion: true,
    expect: 13,
    viewports: ['desktop', 'tablet']
  },
  {
    url: '/zeit-online/centerpage/index?ad-debug',
    selectors: ['.ad-container[data-type="mobile"]'],
    selectorExpansion: true,
    expect: 10,
    viewports: ['mobile']
  },
  {
    url: '/zeit-online/centerpage/index?ad-debug',
    selectors: ['.ad-container--in-app[data-type="mobile"]'],
    selectorExpansion: true,
    expect: 10,
    onBeforeScript: 'appUserAgent.js',
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/zeit-online/centerpage/index?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/zeit-online/centerpage/index?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/zeit-online/centerpage/index-with-classic?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/zeit-online/centerpage/index-with-classic?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/zeit-online/centerpage/centerpage?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/zeit-online/centerpage/centerpage?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/zeit-online/centerpage/teaser-to-wochenmarkt?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/zeit-online/centerpage/teaser-to-wochenmarkt?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/thema/index?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/thema/index?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/thema/autotopic?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/thema/autotopic?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/thema/manualtopic?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/thema/manualtopic?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
  {
    label: 'browser',
    url: '/thema/jurastudium?ad-debug',
    selectors: ['document']
  },
  {
    label: 'app-webview',
    url: '/thema/jurastudium?ad-debug',
    onBeforeScript: 'appUserAgent.js',
    selectors: ['document'],
    viewports: ['mobile', 'tablet']
  },
];

module.exports = scenarios;
