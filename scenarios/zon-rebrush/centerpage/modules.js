const scenarios = [
  {
    label: 'kpi',
    url: '/zeit-online/centerpage/kpi',
  },
  {
    label: 'studylisting',
    url: '/campus/centerpage/joblisting',
    selectors: ['.studylisting'],
    selectorExpansion: true,
  },
  {
    label: 'joblisting',
    url: '/zeit-online/centerpage/index',
    selectors: ['.joblisting'],
    selectorExpansion: true,
  },
  {
  label: 'carousel',
  url: '/zeit-online/centerpage/headed-carousel',
  selectors: ['.cp-area--headed-carousel'],
  selectorExpansion: true,
},
{
label: 'authorpage',
url: '/autoren/j_random',
selectors: ['.author-header'],
},
{
  label: 'markdown-long',
  url: '/serie/die-schaulustigen',
  selectors: ['.cp-region'],
},
{
  label: 'markdown-short',
  url: '/serie/rice-and-shine',
  selectors: ['.cp-region'],
},{
  label: 'markdown-with-list',
  selectors: ['.cp-region'],
  url: '/thema/manualtopic',
},
];
module.exports = scenarios;
