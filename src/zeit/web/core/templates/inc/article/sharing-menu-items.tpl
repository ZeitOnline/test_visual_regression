<ul class="sharing-menu__items">
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--facebook" href="http://www.facebook.com/sharer/sharer.php?u={{ view.content_url + '?wt_zmc=sm.int.zonaudev.facebook.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=facebook_zonaudev_int&utm_campaign=facebook_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlebottom.1.1.social.facebook">
            {% block fb_icon %}{% endblock %}<span class="sharing-menu__text">Facebook</span>
        </a>
    </li>
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--twitter" href="http://twitter.com/intent/tweet?text={{ view.title | urlencode }}&amp;via=zeitonline&amp;url={{ view.content_url + '?wt_zmc=sm.int.zonaudev.twitter.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=twitter_zonaudev_int&utm_campaign=twitter_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlebottom.1.2.social.twitter">
            {% block twitter_icon %}{% endblock %}<span class="sharing-menu__text">Twitter</span>
        </a>
    </li>
    <li class="sharing-menu__item sharing-menu__item--whatsapp">
        <a class="sharing-menu__link sharing-menu__link--whatsapp" href="whatsapp://send?text={{ (view.title + ' - Artikel auf ' + self.product() + ': ' + view.content_url) | urlencode }}" data-id="articlebottom.1.4.social.whatsapp">
            {% block wa_icon %}{% endblock %}<span class="sharing-menu__text">WhatsApp</span>
        </a>
    </li>
    {% block mail %}{% endblock %}
</ul>
