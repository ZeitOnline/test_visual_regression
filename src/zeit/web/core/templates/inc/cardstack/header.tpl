{# This generates an esi:include in the HTML head to load some js from the cards backend. #}

{% if view.has_cardstack %}
	{{ lama.insert_esi(view.cardstack_head, 'Cardstack Ressourcen konnten nicht geladen werden') }}
{% endif %}
