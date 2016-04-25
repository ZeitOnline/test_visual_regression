{% extends "zeit.web.core:templates/inc/article/sharing-menu-items.tpl" %}

{% block mail %}
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--mail" href="mailto:?subject={{ (view.title + ' - Artikel auf ZEIT ONLINE') | urlencode }}&amp;body={{ ('Artikel auf ZEIT ONLINE lesen: ' + view.content_url + '?wt_zmc=sm.ext.zonaudev.mail.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=mail_zonaudev_ext&utm_campaign=mail_referrer&utm_content=zeitde_dskshare_link_x') | urlencode }}" data-id="articlebottom.1.5.social.mail">
            Mail
        </a>
    </li>
{% endblock %}
