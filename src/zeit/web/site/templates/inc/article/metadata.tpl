{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="article__item">
    <div class="article__intro">
    {% if view.pagination and view.pagination.current > 1 %}
        <div class="article__page-teaser">
            Seite {{ view.pagination.current }}/{{ view.pagination.total }}
            {%- if view.current_page.teaser -%}
                : <h1>{{ view.current_page.teaser }}</h1>
            {% endif %}
        </div>
    {% else %}
        <div class="summary" itemprop="description">
            {{ view.subtitle }}
        </div>
        {%- set byline = view.context | get_byline('main') %}
        {% if byline | length -%}
        <div class="byline">
            {% include 'zeit.web.core:templates/inc/meta/byline.html' %}
        </div>
        {% endif -%}
        <div class="metadata">
            {% include "zeit.web.core:templates/inc/article/metadata.tpl" %}
        </div>
    {% endif %}
</div>
{% if view.context is zplus_content %}
<div class="article__badge">
    <div class="zplus article__item article__item--rimless">
        <div class="zplus__marker">
            {{ lama.use_svg_icon('zplus', 'zplus__marker-icon svg-symbol--hide-ie', view.package, a11y=False) }}
        </div>
        <div class="zplus__label">
            <a class="zplus__link" href="#">
                Exklusiv für Abonennten <!-- {{  view.context.acquisition }} -->
            </a>
            {{ adapt(article, 'volumen.interfaces.IVolume') }}
        </div>
    </div>
</div>
{% endif %}
</div>

