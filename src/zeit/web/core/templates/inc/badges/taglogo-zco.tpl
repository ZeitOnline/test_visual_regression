{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{{ lama.use_svg_icon(teaser | tag_with_logo_content, logo_layout + '__kicker-logo--tag svg-symbol--hide-ie', 'zeit.web.site', a11y=False) }}
{{ lama.use_svg_icon('logo-zco', logo_layout + '__kicker-logo--zco svg-symbol--hide-ie', 'zeit.web.campus', a11y=False) }}
