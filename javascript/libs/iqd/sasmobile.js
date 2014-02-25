if (typeof (sas_scriptDomain) == "undefined") {
    sas_scriptDomain = "http://mobile.smartadserver.com"
}
if (typeof (sas_renderMode) == "undefined") {
    sas_renderMode = 0
}
var sas_ajax = true;
sas_callIndex = 1;
sas_delay = 20;
sas_d = document;
sas_w = window;
sas_tsn = sas_gtsf();
sas_mfb = 1;
sas_olfb = 0;
sas_fa = new Array();
sas_ta = new Array();
sas_aca = new Array();
sas_ccba = new Array();

function sascc(b, a) {
    img = new Image();
    img.src = "http://mobile.smartadserver.com/h/mcp?imgid=" + b + "&pgid=" + a + "&uid=[uid]&tmstp=" + sas_tmstp + "&tgt=[targeting]"
}

function sas_ccf(c) {
    var b = sas_gcf(c);
    myLength = b.childNodes.length;
    if ((b.childNodes != null) && (myLength > 0)) {
        for (sas_cccn = 0; sas_cccn < myLength; sas_cccn++) {
            b.removeChild(b.childNodes[0])
        }
    }
    if (sas_aca.length >= c) {
        if ((typeof (sas_aca[c]) != "undefined") && (sas_aca[c] != null)) {
            for (sas_aca_counter = 0; sas_aca_counter < sas_aca[c].length; sas_aca_counter++) {
                var a = sas_aca[c][sas_aca_counter];
                if ((typeof (a) != "undefined") && (a != null)) {
                    a.parentNode.removeChild(a)
                }
            }
            sas_aca[c] = new Array()
        }
    }
    if (sas_ccba.length >= c) {
        if (typeof (sas_ccba[c]) == "function") {
            sas_ccba[c]();
            sas_ccba[c] = null
        }
    }
}

function sas_gcf(a) {
    return sas_d.getElementById("sas_" + a)
}

function sas_appendToContainer(c, a) {
    var d = sas_gcf(c);
    if ((typeof (d) != "undefined") && (d != null) && (typeof (a) != "undefined") && (a != null)) {
        if (typeof (a) == "string") {
            var b = sas_d.createElement("div");
            b.innerHTML = a;
            a = b
        }
        d.appendChild(a)
    }
}

function sas_addCleanListener(b, a) {
    sas_ccba[b] = a
}

function sasmobile(f, c, e) {
    if (typeof (this.sas_pageid) == "undefined") {
        this.sas_pageid = f
    }
    if (sas_mfb == 1) {
        sas_mfb = 0;
        sas_master = "M"
    } else {
        sas_master = "S"
    }
    sas_scripturl = sas_scriptDomain + "/call2/pubmj/" + f + "/" + c + "/" + sas_master + "/" + sas_tsn + "/" + escape(e) + "?";
    if (sas_fa.indexOf(c) === -1) {
        sas_fa.push(c);
        sas_ta.push(e);
        if (sas_renderMode == 0) {
            var a = sas_createScript(c, sas_scripturl);
            var d = sas_d.getElementById("sas_" + c);
            d.appendChild(a)
        } else {
            if (sas_renderMode == 3) {
                var b = "sas_d.getElementById('sas_" + c + "').appendChild(sas_createScript(" + c + ", '" + sas_scripturl + "'));";
                sas_w.setTimeout(b, sas_callIndex * sas_delay);
                sas_callIndex++
            } else {
                if (sas_renderMode == 1 && !sas_olfb) {
                    sas_olfb = 1;
                    sas_addEvent(sas_w, "load", sas_callAds, false)
                }
            }
        }
    } else {
        var a = sas_createScript(c, sas_scripturl);
        sas_ccf(c);
        sas_appendToContainer(c, a)
    }
}

function sas_createScript(b, c) {
    var a = sas_d.createElement("script");
    a.id = "sas_s" + b;
    a.type = "text/javascript";
    a.src = c;

    a.onload = function () {
        sas_scriptLoadHandler(this);
    };
    a.async = "async";

    return a
}

function sas_scriptLoadHandler(c) {
    var d;
    if (c.id !== undefined) {
        d = c.id.replace("sas_s", "")
    } else {
        if (c.target !== undefined && c.target.id !== undefined) {
            d = c.target.id.replace("sas_s", "")
        }
    }
    if (d != null && typeof (sas_loadHandler) != "undefined") {
        var b = sas_gcf(d);
        var a = {
            id: d
        };
        if (b != null && b.hasChildNodes() && b.childNodes.length > 1) {
            a.hasAd = true
        } else {
            a.hasAd = false
        }
        sas_loadHandler(a)
    }
}

function sas_callAds() {
    sas_callIndex = 1;
    if (sas_fa.length > 0) {
        sas_tsn = sas_gtsf();
        sas_mfb = 1;
        for (i = 0; i < sas_fa.length; i++) {
            sasmobile(sas_pageid, sas_fa[i], sas_ta[i])
        }
    }
}

function sas_callAd(c, d, b, a) {
    if (d === undefined) {
        d = ""
    }
    if (b === undefined) {
        b = true
    }
    if (a === undefined) {
        a = true
    }
    if (b) {
        sas_mfb = 1
    }
    if (a) {
        sas_tsn = sas_gtsf()
    }
    for (i = 0; i < sas_fa.length; i++) {
        if (c == sas_fa[i]) {
            sas_target = sas_ta[i];
            if (typeof (d) != "undefined") {
                sas_target = d
            }
            sasmobile(sas_pageid, sas_fa[i], sas_target)
        }
    }
}

function sas_cleanAds() {
    if (sas_fa.length > 0) {
        for (i = 0; i < sas_fa.length; i++) {
            sas_ccf(sas_fa[i])
        }
    }
}

function sas_cleanAd(a) {
    for (i = 0; i < sas_fa.length; i++) {
        if (a == sas_fa[i]) {
            sas_ccf(sas_fa[i])
        }
    }
}

function sas_addEvent(e, b, c, a) {
    if (e.addEventListener) {
        e.addEventListener(b, c, a);
        return true
    } else {
        if (e.attachEvent) {
            var d = e.attachEvent("on" + b, c);
            return d
        } else {
            e["on" + b] = c
        }
    }
}

function sas_gtsf() {
    return Math.round(Math.random() * 10000000000)
};