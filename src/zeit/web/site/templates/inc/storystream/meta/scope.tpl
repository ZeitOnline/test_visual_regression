{% set blockname = 'storystream-scope' %}
<div class="{{ blockname }}">
	<div class="{{ blockname }}__container">
		<p class="{{ blockname }}__content">
			{% if view.atom_meta.count %}
				<span class="{{ blockname }}__counter"><span class="{{ blockname }}__number">{{ view.atom_meta.count }}</span> Beiträge</span>
			{% endif %}

			{% if view.atom_meta.oldest_date and view.atom_meta.latest_date %}
				{% set oldest_date = view.atom_meta.oldest_date | format_date('short') %}
				{% set latest_date = view.atom_meta.latest_date | format_date('short') %}
				<span class="{{ blockname }}__dates">
					{% if oldest_date == latest_date %}
						{{ oldest_date }}
					{% else %}
						<a href="#first_atom" class="{{ blockname }}__link">{{ oldest_date }}</a> bis <a href="#latest_atom" class="{{ blockname }}__link">{{ latest_date }}</a>
					{% endif %}
				</span>
			{% endif %}
		</p>
	</div>
</div>
