<ul class="sharing-menu__items" data-publisher="{% block publisher %}ZEIT ONLINE{% endblock %}">
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--facebook" href="http://www.facebook.com/sharer/sharer.php?u={{ view.content_url + '?wt_zmc=sm.int.zonaudev.facebook.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=facebook_zonaudev_int&utm_campaign=facebook_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlebottom.1.2.social.facebook">
            {% block fb_icon %}{% endblock %}<span class="sharing-menu__text">Facebook</span>
        </a>
    </li>
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--twitter" href="http://twitter.com/intent/tweet?text={{ view.title | urlencode }}&amp;via=zeitonline&amp;url={{ view.content_url + '?wt_zmc=sm.int.zonaudev.twitter.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=twitter_zonaudev_int&utm_campaign=twitter_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlebottom.1.3.social.twitter">
            {% block twitter_icon %}{% endblock %}<span class="sharing-menu__text">Twitter</span>
        </a>
    </li>
    <li class="sharing-menu__item sharing-menu__item--whatsapp">
        <a class="sharing-menu__link sharing-menu__link--whatsapp" href="whatsapp://send?text={{ '%s - Artikel auf %s: %s' | format(view.title, self.publisher(), view.content_url) | urlencode }}" data-id="articlebottom.1.4.social.whatsapp">
            {% block wa_icon %}{% endblock %}<span class="sharing-menu__text">WhatsApp</span>
        </a>
    </li>
    {% block mail -%}
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--mail" href="mailto:?subject={{ '%s - Artikel auf %s' | format(view.title, self.publisher()) | urlencode }}&amp;body={{ 'Artikel auf %s lesen: %s?wt_zmc=sm.ext.zonaudev.mail.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=mail_zonaudev_ext&utm_campaign=mail_referrer&utm_content=zeitde_dskshare_link_x' | format(self.publisher(), view.content_url) | urlencode }}" data-id="articlebottom.1.5.social.mail">
            <span class="sharing-menu__text">Mail</span>
        </a>
    </li>
    {%- endblock %}
</ul>