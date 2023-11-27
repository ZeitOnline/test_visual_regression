const scenarios = [
{
  label: 'teaser-classic-video',
  url: '/zeit-online/centerpage/zon-teaser-classic-video',
},
{
  label: 'teaser-column',
  url: '/zeit-online/centerpage/zon-teaser-column',
},

{
  label: 'teaser-standard',
  selectors: ['.zon-teaser--standard'],
  url: '/zeit-online/centerpage/zon-teaser-standard',
  selectorExpansion: true,
},
{
  label: 'teaser-wide',
  url: '/zeit-online/centerpage/zon-teaser-wide',
  selectors: ['.zon-teaser--wide'],
  selectorExpansion: true,
},
{
  label: 'teaser-wide-panorama',
  url: '/zeit-online/centerpage/zon-teaser-wide-panorama',
},
{
  label: 'teaser-upright',
  url: '/zeit-online/centerpage/zon-teaser-upright',
  selectors: ['.zon-teaser--upright'],
  selectorExpansion: true,
},
{
  label: 'teaser-square',
  url: '/zeit-online/centerpage/zon-teaser-square',
  selectors: ['.zon-teaser--square'],
  selectorExpansion: true,
},
{
  label: 'teaser-poster',
  url: '/zeit-online/centerpage/zon-teaser-poster',
  selectors: ['.zon-teaser--poster'],
  selectorExpansion: true,
},
{
  label: 'teaser-poster-panorama',
  url: '/zeit-online/centerpage/zon-teaser-poster-panorama',
},
{
  label: 'teaser-lead',
  url: '/zeit-online/centerpage/zon-teaser-lead',
  selectors: ['.zon-teaser--lead'],
  selectorExpansion: true,
},
{
  label: 'teaser-podcast',
  url: '/zeit-online/centerpage/zon-teaser-podcast-variants',
},
{
  label: 'teaser-video',
  url: '/zeit-online/centerpage/zon-teaser-video',
},
{
  label: 'teaser-duo',
  url: '/zeit-online/centerpage/duo-teaser-mix',
  selectors: ['.cp-region--duo'],
  selectorExpansion: true,
},
{
  label: 'teaser-author',
  url: '/zeit-online/author-teaser',
  selectors: ['.zon-teaser--is-author'],
  selectorExpansion: true,
},
];

module.exports = scenarios;
