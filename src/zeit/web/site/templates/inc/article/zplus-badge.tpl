{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="{% block layout %}zplus-badge{% endblock %}
    {%- if not view.zplus_label.volume_exists %} {{ self.layout() }}--coverless{% endif %}" data-ct-row="zplus-badge
    {%- if not view.zplus_label.cover %}_coverless{% endif %}" data-ct-column="false">
    <div class="{{ self.layout() }}__banner article__item article__item--rimless">
        {% if view.zplus_label.link -%}
            <a class="{{ self.layout() }}__link" href="{{ view.zplus_label.link }}">
                {% block volumeteaser -%}
                <span class="{{ self.layout() }}__text">
                    <span class="{{ self.layout() }}__intro">{{ view.zplus_label.intro }}</span>
                    <span class="{{ self.layout() }}__link-text">{{ view.zplus_label.link_text }}</span>
                </span>
                {%  if view.context is zplus_abo_content -%}
                    {{ lama.use_svg_icon('zplus', self.layout() ~ '__icon svg-symbol--hide-ie', view.package, a11y=False) }}
                {% endif -%}
                {% if view.zplus_label.volume_exists -%}
                    {% set packshot = view.zplus_label.cover -%}
                    {% set module_layout = self.layout() -%}
                    {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
                {% endif -%}
                {% endblock volumeteaser -%}
            </a>
        {%- else -%}
            {{- self.volumeteaser() -}}
        {%- endif -%}
    </div>
</div>
