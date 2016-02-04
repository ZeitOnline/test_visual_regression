{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}

{% set image = get_teaser_image(module, teaser) %}

<article class="{% block layout %}teaser-card{% endblock %} {{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
         data-clicktracking="{{ area.kind }}"
         {% block teaser_attributes %}{% endblock %}>
	
	<div class="card__deck">
		{# front of card #}
		<div class="card {% block card_class %}{% endblock %}" {% block background_color_styles %}{% endblock %}>
			{% include "zeit.web.magazin:templates/inc/asset/image-card.tpl" %}
			<h2>
			    <div class="card__title">
			        {{ teaser.teaserSupertitle or teaser.supertitle }}
			    </div>
			    <div class="card__text {% block text_class %}card__text--with-bg{% endblock %}">
			        {% block teaser_text %}{{ teaser.teaserTitle or teaser.title }}{% endblock %}
			    </div>
			</h2>

			{% block author %}{% endblock %}
			
			{% block button %}<a href="{{ teaser | create_url }}" class="card__button">Lesen</a>{% endblock %}
		</div>
		{# back of card #}
		{% block back %}{% endblock %}
	</div>

</article>
