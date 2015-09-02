{#

Default teaser template for large teasers

Available attributes:
    cp
    lama
    blocks
    module
    teaser

All calling templates have to provide:
    format: to define type of leader (eg. 'upright', 'square', 'full')
    shade: to define shading ('light', 'darker', 'dark', 'none')
    supertitle: to define display of supertitle ('true', 'false')
#}

{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{%- import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}
{%- import 'zeit.web.magazin:templates/macros/article_macro.tpl' as blocks with context %}

{%- set video = teaser | get_video_asset %}
{%- set image = get_teaser_image(module, teaser) %}

<div class="cp_leader cp_leader--{{ self.format() }}{{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}">

    {# call comment box #}
    {% if self.format() != 'full' -%}
         {{ cp.comment_count(view.comment_counts[teaser.uniqueId], teaser | create_url) }}
    {%- endif %}

    <a href="{{ teaser | create_url }}">
        {% if video -%}
            {# call video asset #}
            {{ blocks.headervideo(video, 'cp_leader__asset cp_leader__asset--' + self.shade(), '') }}
        {%- elif image -%}
            {# call image asset #}
            <div class="scaled-image is-pixelperfect cp_leader__asset cp_leader__asset--{{ self.shade() }}">
                {{ lama.insert_responsive_image(image) }}
            </div>
        {%- endif %}
    </a>
    {# call teaser text #}
    {{ cp.teaser_text_block(teaser, 'leader', self.shade(), self.supertitle()) }}
</div>
