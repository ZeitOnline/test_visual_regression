
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
        <span class="cp__comment__count__wrap icon-comments-count">{{comments}}</span>
    {% endif %}
{%- endmacro %}

{% macro teaser_supertitle_title(teaser, additional_css_class, withlink=True) -%}
    {% if withlink -%}<a href="{{teaser | create_url}}">{%- endif %}
    <div class="{{ additional_css_class | default('teaser') }}__kicker">
        {% if teaser.teaserSupertitle is not none %}
            {{teaser.teaserSupertitle | hide_none}}
        {% else %}
            {{teaser.supertitle | hide_none }}
        {% endif %}
    </div>
    <div class="{{ additional_css_class | default('teaser') }}__title">
        {{teaser.teaserTitle}}
    </div>
    {% if withlink -%}</a>{%- endif %}
{%- endmacro %}

{% macro teaser_sharing_card(teaser) -%}
    <div class="card__slider">
        <div class="card__slide js-slide-card">
            <div class="card__sharing-icons">
                <a href="http://twitter.com/home?status={{teaser | create_url | e}}"
                    class="card__sharing-icon js-stop-propagation icon-twitter" target="_blank" title="Auf Twitter teilen"></a>

                <a href="https://plus.google.com/share?url={{teaser | create_url | e}}"
                    class="card__sharing-icon js-stop-propagation icon-google" target="_blank" title="Auf Google+ teilen"></a>

                <a href="http://www.facebook.com/sharer/sharer.php?u={{teaser | create_url | e}}"
                    class="card__sharing-icon js-stop-propagation icon-facebook" target="_blank" title="Auf Facebook teilen"></a>

                <a href="mailto:?subject={{teaser.teaserTitle}}&amp;body={{teaser | create_url | e}}" class="card__sharing-icon js-stop-propagation icon-mail" title="Per Mail senden"></a>
            </div>
        </div>
    </div>
{%- endmacro %}
