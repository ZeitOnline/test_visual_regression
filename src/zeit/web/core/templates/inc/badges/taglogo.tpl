{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}
{{ lama.use_svg_icon(teaser | tag_with_logo_content, logo_layout + '__kicker-logo--tag', 'zeit.web.site', a11y=False) }}
