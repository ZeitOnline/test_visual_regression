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
    selctors: ['.joblisting'],
    selectorExpansion: true,
  },
  {
  label: 'carousel',
  url: '/zeit-online/centerpage/headed-carousel',
  selctors: ['.cp-area--headed-carousel'],
  selectorExpansion: true,
},
{
label: 'authorpage',
url: '/autoren/j_random',
},
{
  label: 'markdown-long',
  url: '/serie/die-schaulustigen',
},
{
  label: 'markdown-short',
  url: '/serie/rice-and-shine',
},{
  label: 'markdown-with-list',
  url: '/thema/manualtopic',
},

];

http://localhost:9090/autoren/j_random

module.exports = scenarios;
