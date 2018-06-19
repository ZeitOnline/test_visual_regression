{% if podlove_button_configuration %}
    {% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}
    <script type="text/javascript">
        window.podcastData_{{ podlove_button_id }} = {{ podlove_button_configuration | tojson | safe }};
    </script>
    {# Podlove verträgt es derzeit nicht, wenn der Button ein Link ist.
       Das wäre mal einen Pull Request in deren Software wert!
       Und dann können wir das hier nutzen:
        {% set external_site_url = view.header_module.podlove_configuration.external_site_url or 'http://{}.podigee.io'.format(view.header_module.podlove_configuration.podigee_subdomain) %}
       Und dann auch cursor:pointer sowie no-js aus dem CSS entfernen!
    #}
    <span tabindex="0" class="podcastfooter__podlove podlove-button podlove-subscribe-button-{{ podlove_button_id }}">
        {{ lama.use_svg_icon('podcast', 'podlove-button__icon', view.package, a11y=False) }}
        Abonnieren
    </span>
    <script class="podlove-subscribe-button" src="https://cdn.podlove.org/subscribe-button/javascripts/app.js" data-language="de" data-size="small" data-hide="true" data-buttonid="{{ podlove_button_id }}" data-json-data="podcastData_{{ podlove_button_id }}" async defer></script>
    {# Attention: The data-size attribute is needed, even though we use our own button. Otherwise the podlove script fails. #}
{% endif %}
