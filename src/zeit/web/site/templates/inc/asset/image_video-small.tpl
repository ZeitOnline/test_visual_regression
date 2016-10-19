{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'video-thumbnail' %}
{% block media_block %}{{ module_layout }} {{ module_layout }}--small{% endblock %}

{% block media_caption -%}
    {% if teaser.video_still_copyright and teaser.video_still_copyright | trim %}
        <figcaption class="figure__caption figcaption--hidden">
            <span class="video-figure__copyright" itemprop="copyrightHolder" itemscope itemtype="http://schema.org/Person">
                <span itemprop="name">© Foto: {{ teaser.video_still_copyright | trim }}</span>
            </span>
        </figcaption>
        {% endif %}
{%- endblock media_caption -%}
