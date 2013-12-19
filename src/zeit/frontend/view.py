# -*- coding: utf-8 -*-
from babel.dates import get_timezone
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo, IModified
from zeit.content.image.interfaces import IImageMetadata
from zeit.magazin.interfaces import IArticleTemplateSettings, INextRead
import zeit.content.article.interfaces


class Base(object):
    """Base class for all views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {}


_navigation = {'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
               'zmo':('ZEIT Magazin', 'http://www.zeit.de/index', 'myid_zmo'),
               'lebensart': (
                   'ZEIT Magazin',
                   'http://www.zeit.de/magazin/index',
                   'myid2',
               ),
               'mode': (
                   'Mode',
                   'http://www.zeit.de/magazin/lebensart/index',
                   'myid3',
               ), }


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json')
@view_config(context=zeit.content.article.interfaces.IArticle,
             renderer='templates/article.html')
class Article(Base):

    def __call__(self):
        self.context.advertising_enabled = True
        self.context.main_nav_full_width = False
        self.context.is_longform = False

        if IArticleTemplateSettings(self.context).template == 'longform':
            self.context.advertising_enabled = False
            self.context.main_nav_full_width = True
            self.context.is_longform = True
            return render_to_response('templates/longform.html',
                                      {"view": self},
                                      request=self.request)
        return {}

    @property
    def title(self):
        return self.context.title

    @property
    def subtitle(self):
        return self.context.subtitle

    @property
    def supertitle(self):
        return self.context.supertitle

    @property
    def pages(self):
        return zeit.frontend.interfaces.IPages(self.context)

    @property
    def header_img(self):
        return self.context.header_img

    @property
    def author(self):
        try:
            author = self.context.authors[0]
        except IndexError:
            author = None
        return {
            'name': author.display_name if author else None,
            'href': author.uniqueId if author else None,
            'prefix': " von " if self.context.genre else "Von ",
            'suffix': ', ' if self.location else None,
        }

    @property
    def publish_date(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(
            self.context).date_last_published_semantic
        if date:
            return date.astimezone(tz)

    @property
    def publish_date_meta(self):
        return IPublishInfo(
            self.context).date_last_published_semantic.isoformat()

    @property
    def last_modified_date(self):
        return IModified(self.context).date_last_modified

    @property
    def rankedTags(self):
        return self.context.keywords

    @property
    def genre(self):
        return self.context.genre

    @property
    def source(self):
        return self.context.copyrights or self.context.product_text

    @property
    def location(self):
        return None  # XXX not implemented in zeit.content.article yet

    @property
    def focussed_nextread(self):
        nextread = INextRead(self.context)
        related = nextread.nextread
        if related:
            image = related.main_image
            if image is not None:
                image = {
                    'uniqueId': image.uniqueId,
                    'caption': (related.main_image_block.custom_caption
                                or IImageMetadata(image).caption),
                }
            else:
                image = {'uniqueId': None}
            return {'layout': nextread.nextread_layout,
                    'article': related,
                    'image': image}

    @property
    def breadcrumb(self):
        l = [_navigation['start']]
        l.append(_navigation['zmo'])
        if self.context.ressort in _navigation:
            l.append(_navigation[self.context.ressort])
        if self.context.sub_ressort in _navigation:
            l.append(_navigation[self.context.sub_ressort])
        if self.title:
            l.append((self.title, 'http://localhost'))
        return l


    @property
    def comments(self):
        return [
            (False, u"/img/exner.jpg", u"Maria Exner", 2, u"Community", u"Unter Freunden bedarf es ja auch nicht eines solchen Abkommens..." ),
            (False, False, u"ImmanuelKant", 5, False, u"... wäre es wohl angebracht die Amerikanische Botschaft mit Störsignalen aller Art zu übersähen und vielleicht eine intensiever an Verschlüsselungsalgorithmen zu forschen die man dann am besten der ganzen Welt frei zur Verfügung stellt um den so netten Amerikanern mal ordentlich auf ihren arroganten Schlips zu treten!" ),
            (True, False, u"Super_Kluk", 3, False, u"sollte man die Botschaft schließen und alle rechtlichen Mittel nutzen um die Personen ggf. wegen Spionage einzubuchten. Die dann übrig bleiben sollten acht-kantig rausgeschmissen werden. Oder wie verhalten Sie sich mit einem Gast, der sich unmöglich aufführt?" ),
            (True, False, u"Freidenker.", 2, u"Experte", u"Da es nachgewiesen ist das die USA von der Botschaft aus spionieren ist der Botschaftsstatus Null und Nichtig. Laut Wiener Übereinkommen untersteht der Botschaft keinerlei Schutz mehr und darf von deutschen Behörden auf staatsfeindliche und Bedrohende Aktivitäten durchsucht werden.Eine andere Sache ist, wieso man erst nach 6 Monaten gemerkt hat das man einen 5 meter hohen Fernsendemast auf der britischen Botschaft hochgezogen hat." ),
            (False, False, u"michael29821", 10, False, u"Ein Völkerrechtler hat neulich im Interview gesagt, das Teile des Besatzungsstatut immer noch in Kraft sind und die USA berechtigt sind uns zu Überwachen. Die Regelungen sind in den Pariser Verträgen und den Geheimen 2+4 Verträgen. Also können sie einen Rückzieher machen wie sie wollen. Sie haben Hoheitsrechte in Deutschland." ),
            (False, False, u"AntonPree", 15, False, u"Die USA erklärt also, dass sie Deutschland weiter ausspionieren muss, um eine gewisse Parität herzustellen?! Sarkastisch gesagt: wir sollen nicht ausgegrenzt werden." ),
            (False, u"http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDQvMjAvMTYvMDYvNDcvOTQ3L0NocmlzdGlhbl9wb3J0cmFpdF9xdWFkXzEyMDQxMC5qcGciXSxbInAiLCJ0aHVtYiIsIjUwMHg1MDAjIl1d/Christian_portrait_quad_120410.jpg", u"dachsus", 20, False, u"Vielleicht kommen unsere Regierenden jetzt doch einmal auf den Gedanken, das wir uns selbst einmal die Finder dreckig machen sollten… sprich: Einen eigenen Geheimdienst ausstatten, der in der Lage ist Deutschland und sein Bürger gegen Übergriffe anderer Staaten zu schützen, und ggf. auch selbst zubeißen kann. Die bequeme Haltung, den Amerikanern die Drecksarbeit zu überlassen und sich selbst die Hände in Unschuld zu Waschen ist leider nicht die Lösung." ),
            (False, False, u"Gerry10", 25, False, u"Hören Politiker sich eigentlich noch selbst zu oder haben die den Verstand nur dann und wann eingeschaltet? Das muss man sich auf der Zunge zergehen lassen: Ein Vertrag der das brechen von Grundrechten regulieren soll wird wohl nicht unterschrieben weil die USA keinen Präzedenzfall schaffen wollen! Ich schaffe es nicht darüber nachzudenken weil mein Verstand etweder kapituliert oder mich verlässt." ),
            (False, False, u"Super_Klug", 30, False, u"sollte man die Botschaft schließen und alle rechtlichen Mittel nutzen um die Personen ggf. wegen Spionage einzubuchten. Die dann übrig bleiben sollten acht-kantig rausgeschmissen werden." ),
            (True, False, u"Buegeleisenverkaeufer", 25, False, u"...indem man sich überlegt, wie mächtig der Gast ist. Und dann lässt man solche Halbstarkenphantasien lieber..." ),
            (True, False, u"bluecheck", 20, False, u"Sie haben vollkommen Recht! Leider ist es aber so, dass die USA zwar Gast bei uns sind, ihnen unser Haus aber gehört." ),
            (False, False, u"nilszbzb", 55, False, u"in sonstigen Meldungen: USA verweigern Deutschland No-Nuke-Abkommen" ),
            (False, u"http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTMvMDgvMjkvMTAvMTMvMzMvOTA4L3BldGVyX3J1ZG9scGguanBnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/peter_rudolph.jpg", u"Klaus Teuber", 60, False, u"Ja, wer solche Freunde hat, braucht keine Feinde mehr. Gibt es vielleicht noch ein Plätzchen für Deutschland in der russischen Freihandelszone? Oder kriegen wir es dann auch mit Klitschko zu tun?" ),
            (False, False, u"AlleZeitenÄndernSich", 65, False, u"Bündnispartner? Die verhalten sich anders. Die Manie der Amerikaner seit dem 11.09. alles unter Kontrolle haben zu wollen, wird ihnen international das Genick brechen! Wir als Europäer können uns das eigentlich nicht gefallen lassen. Es ist ihnen egal! Es ist auch egal, dass sie angeordnete Tötungen durch Drohnen vornehmen lassen. Selbstverständlich nicht im eigenen Land! Alles zum Schutz von wem? Und wer hat wirklich die Kontrolle darüber? Wir sind Bündnispartner von diesem Land? Wirklich?" ),
            (False, False, u"spectator23", 70, False, u"Der Guardian hat doch mal eine NSA Spy Map veröffentlicht, da wird Deutschland eindeutig bevorzugt behandelt in Europa." ),
            (False, False, u"anne129", 75, False, u"... unsere Finger sauber sind. Die USA können nahezu uneingeschränkt deutsche Bürger und Organisationen überwachen und ausspionieren. Das wäre deutschen Nachrichtendiensten und dem Verfassungsschutz in diesem Maße nicht gestattet. Es war schon immer an zu nehmen, dass dies weitgehend mit dem Wissen der deutschen Regierung geschieht, und dass diese auch zumindest teilweise in den Genuss dieser Informationen gelangt, die sie selber gar nicht hätte legal erheben können." ),
            (False, u"http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTMvMDUvMzEvMTQvMjUvMDUvMjI2L2p1bGlhbl9wYW56ZXIuanBnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/julian-panzer.jpg", u"redshrink", 75, False, u"... unsere Finger sauber sind. Die USA können nahezu uneingeschränkt deutsche Bürger und Organisationen überwachen und ausspionieren. Das wäre deutschen Nachrichtendiensten und dem Verfassungsschutz in diesem Maße nicht gestattet. Es war schon immer an zu nehmen, dass dies weitgehend mit dem Wissen der deutschen Regierung geschieht, und dass diese auch zumindest teilweise in den Genuss dieser Informationen gelangt, die sie selber gar nicht hätte legal erheben können." ),
            (True, False, u"Buegeleisenverkaeufer", 30, False, u"In Diensten des deutschen Volkes. Es stellt sich nur die Frage, was dann daraus folgt." ),
            (False, u"http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDIvMTAvMTUvMjkvMjkvODUzL2R1bnN0ZXIuanBnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/dunster.jpg", u"raybird", 80, False, u"Die Wahl ist ja auch durch. Regierung steht." ),
            (False, False, u"Thomas Haug", 85, False, u"Über kurz oder lang (eher lang) wird das Bündnis mit den USA brechen. Hintergrund werden die nicht mehr zu überbrückenden Differenzen im Blick auf die Welt sein." ),
            (False, False, u"tomtom19582", 90, False, u"Zum Einen scheint es im Interesse unserer eigenen Politiker zu sein, auch über unsere Grundrechte hinausgehende Überwachungsmethoden anwenden zu wollen. Ich erinnere hier nur an die Aktivitäten DEUTSCHER Politiker binnen der letzten 25 Jahre, was die Verschärfung der Überwachungsmöglichkeiten anbelangt. Diese Linie wurde von allen Regierungsparteien gleichermaßen Schritt für Schritt verfolgt! (Rot-Grün, Schwarz-Rot, Schwarz-Gelb). Von den im Bundestag vertretenen Parteien waren lediglich die FDP und die Linken nicht damit einverstanden. Die spielen aber die nächsten Jahre vor dem Hintergrund eine GroKo keine Rolle mehr. Zum Zweiten stehen handfeste wirtschaftliche Interessen dahinter, so dass auch die Wirtschaftslobbies sich vehement gegen einen Bruch mit den USA aussprechen werden." ),
            (False, False, u"DerDoktor", 100, False, u"in den Hinterzimmern eigentlich bereits einen Verhandlungsvorteil durch ihr aus der Spionage resultierendes Mehrwissen?" ),
            (False, u"http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDIvMTAvMTUvMjkvMTQvOTY4L3Bob3RvXzIxOC5qcGVnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/photo_218.jpeg", u"mugu1", 120, False, u"Kommen wir zum 2. Gesicht: Echt überraschend ist m.E., dass nun endlich ein US-Bundesgericht gegen diese maßlose Praxis der NSA der Totalüberwachung vorgegangen ist. Sollte dies Schule machen, steht zumindest i.d. USA diese Form vor dem Aus. Aber natürlich nicht die Praxis an sich. Das Schlupfloch wurde ja gleich mitpräsentiert: So halten dann eben die Telefongesellschaften die Daten zum Abruf bereit. Und trotzdem ist es bemerkenswert, was sich in den USA vor Gericht ereignet hat. Denn für die Zukunft könnte dies der 1. Schritt zurück auf den richtigen Pfad sein. Doch der Rückweg ist lang. Vielleicht gar schon unerreichbar." ),
        ]


class Gallery(Base):
    pass


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json', name='teaser')
@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             renderer='templates/teaser.html')
class Teaser(Article):

    @property
    def teaser_text(self):
        """docstring for teaser"""
        return self.context.teaser
