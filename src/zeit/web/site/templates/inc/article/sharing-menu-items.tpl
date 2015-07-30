<ul class="sharing-menu__items">
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--facebook" href="http://www.facebook.com/sharer/sharer.php?u={{ view.content_url + '?wt_zmc=sm.int.zonaudev.facebook.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=facebook_zonaudev_int&utm_campaign=facebook_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlebottom.1.1.social.facebook">
            Facebook
        </a>
    </li>
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--twitter" href="http://twitter.com/intent/tweet?text={{ view.title | urlencode }}&amp;via=zeitonline&amp;url={{ view.content_url + '?wt_zmc=sm.int.zonaudev.twitter.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=twitter_zonaudev_int&utm_campaign=twitter_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlebottom.1.2.social.twitter">
            Twitter
        </a>
    </li>
    {# Google+ will be closed in the near future, all info is fetched automaticall, no params needed #}
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--google" href="https://plus.google.com/share?url={{ view.content_url + '?wt_zmc=sm.int.zonaudev.gplus.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=gplus_zonaudev_int&utm_campaign=gplus_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlebottom.1.3.social.googleplus">
            Google +
        </a>
    </li>
    <li class="sharing-menu__item sharing-menu__item--whatsapp">
        <a class="sharing-menu__link sharing-menu__link--whatsapp" href="whatsapp://send?text={{ (view.title + ' - Artikel auf ZEIT ONLINE: ' + view.content_url) | urlencode }}" data-id="articlebottom.1.4.social.whatsapp">
            WhatsApp
        </a>
    </li>
    <li class="sharing-menu__item">
        <a class="sharing-menu__link sharing-menu__link--mail" href="mailto:?subject={{ (view.title + ' - Artikel auf ZEIT ONLINE') | urlencode }}&amp;body={{ ('Artikel auf ZEIT ONLINE lesen: ' + view.content_url + '?wt_zmc=sm.ext.zonaudev.mail.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=mail_zonaudev_ext&utm_campaign=mail_referrer&utm_content=zeitde_dskshare_link_x') | urlencode }}" data-id="articlebottom.1.5.social.mail">
            Mail
        </a>
    </li>
</ul>
