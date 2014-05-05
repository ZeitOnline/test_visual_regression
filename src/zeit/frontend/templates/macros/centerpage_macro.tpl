
{% macro include_cp_block(obj, ad) -%}
    {% for teaser_block in obj -%}
        {% if teaser_block.layout %}
            {%-
                set teaser_blocks = [
                    'templates/inc/teaser_block_' + teaser_block.layout.id + '.html',
                    'templates/inc/teaser_block_default.html'
                ]
            %}
            {% include teaser_blocks ignore missing %}

            {% if (ad == 'enable') and (loop.index == 2 or loop.last) and (added is not defined) -%}
                <!-- special ad integration by counter -->
                {% set added = true %}
                {% include 'templates/inc/teaser/teaser_ad.html' ignore missing %}
            {% endif %}
        {% endif %}
    {% endfor %}
{%- endmacro %}

{% macro comments_count(comments) -%}
    {% if comments %}
        <span class="cp__comment__count__wrap icon-comments-count">
            {{comments}}
        </span>
    {% endif %}
{%- endmacro %}

{% macro teaser_supertitle_title(teaser, additional_css_class, withlink=True) -%}
    {% if withlink -%}<a href="{{teaser.uniqueId | translate_url}}">{%- endif %}
    <div class="{{ additional_css_class | default('teaser') }}__kicker">
        {{teaser.teaserSupertitle | hide_none}}
    </div>
    <div class="{{ additional_css_class | default('teaser') }}__title">
        {{teaser.teaserTitle}}
    </div>
    {% if withlink -%}</a>{%- endif %}
{%- endmacro %}
