{% import 'templates/macros/layout_macro.tpl' as lama with context %}

{% macro include_teaser_block(obj) -%}
    {% if obj -%}
        {% for teaser_block in obj -%}
            {% if teaser_block.layout -%}
                {{ include_teaser(teaser_block) }}
            {% endif %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_teaser_block_with_ad(obj) -%}
    {% if obj -%}
        {% for teaser_block in obj -%}
            {% if teaser_block.layout -%}
                {{ include_teaser(teaser_block) }}

                {% if (loop.index == 2 or loop.last) and (added is not defined) -%}
                    <!-- special ad integration by counter -->
                    {% set added = true %}
                    {{ include_cp_ad() }}
                {% endif %}
            {% endif %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_teaser(teaser_block, prefix) -%}
    {% if prefix is not defined -%}
        {% set prefix = '' -%}
    {% endif %}

    {% if teaser_block -%}
        {% for teaser in teaser_block %}
            {% include ['templates/inc/teaser/' + prefix + teaser_block.layout.id + '.html', 'templates/inc/teaser/default.html'] ignore missing %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_cp_ad() -%}
    <div class='cp_button--ad'>
        {{ lama.adplace(view.banner(7), view.banner_channel) }}
    </div>
{%- endmacro %}

{% macro comments_count(comments) -%}
    {% if comments %}
        <span class="cp_comment__count__wrap icon-comments-count">{{comments}}</span>
    {% endif %}
{%- endmacro %}

{% macro teaser_text_block(teaser, block='leader', shade='none', supertitle=true, subtitle=true, icon=false) -%}
    <header class="cp_{{block}}__title__wrap cp_{{block}}__title__wrap--{{ shade }}">
        {% if icon == 'true' %}
            <span class="icon-galerie-icon-white"></span>
        {% endif %}
        <a href="{{teaser | create_url}}">
            <h2>
                {% if supertitle != 'false' %}
                    <div class="cp_{{block}}__supertitle">
                        {% if teaser.teaserSupertitle %}
                            {{ teaser.teaserSupertitle | hide_none }}
                        {% elif teaser.supertitle %}
                            {{ teaser.supertitle | hide_none }}
                        {% endif %}
                    </div>
                {% endif %}
                <div class="cp_{{block}}__title">
                    {{ teaser.teaserTitle | hide_none }}
                </div>
            </h2>
            {% if subtitle != 'false' %}
                <span class="cp_{{block}}__subtitle">
                    {{ teaser.teaserText | hide_none }}
                </span>
            {% endif %}
        </a>
    </header>
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
