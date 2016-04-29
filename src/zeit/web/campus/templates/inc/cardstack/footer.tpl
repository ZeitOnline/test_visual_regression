{# This generates an esi:include at the end of the HTML body to load some js from the cards backend. #}

{% if view.has_cardstack %}
    {{ lama.insert_esi(view.cardstack_scripts, 'Cardstack konnte nicht eingebunden werden') }}
{% endif %}

