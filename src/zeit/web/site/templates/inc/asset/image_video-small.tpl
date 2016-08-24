{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'video-thumbnail' %}
{% block media_block %}{{ module_layout }} {{ module_layout }}--small{% endblock %}

{% block media_caption -%}
    {# TODO: Was haben wir denn hier? blocks schonmal nicht ... #}
    {% if teaser.credit and teaser.credit | trim | length > 7 %}
        <figcaption class="figure__caption figure__caption--hidden">
            <span class="video-figure__copyright" itemprop="copyrightHolder" itemscope itemtype="http://schema.org/Person">
                <span itemprop="name">{{ teaser.credit | trim | replace('© Foto: ', '© Foto: ') }}</span>
            </span>
        </figcaption>
        {% endif %}
{%- endblock media_caption -%}
