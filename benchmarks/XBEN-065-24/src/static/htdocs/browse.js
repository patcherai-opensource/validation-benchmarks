var sharePointPlugin = undefined;

function onLoad() {
}

function getSharePointPlugin() {
    if (sharePointPlugin !== undefined) {
        return sharePointPlugin;
    }
    sharePointPlugin = null;
    var plugin = document.getElementById("winFirefoxPlugin");
    if (plugin && typeof plugin.EditDocument === "function") {
        sharePointPlugin = plugin;
    } else if ("ActiveXObject" in window) {
        try {
            sharePointPlugin = new ActiveXObject("SharePoint.OpenDocuments.3");
        } catch(e) {
            try {
                sharePointPlugin = new ActiveXObject("SharePoint.OpenDocuments.2");
            } catch(e2) {}
        }
    }
    return sharePointPlugin;
}

function openWebDavDocument(opts) {
    var ofe_link = opts.ofe + opts.href;
    var url = opts.href;
    var plugin = getSharePointPlugin();
    var res = false;
    if (plugin) {
        try {
            res = plugin.EditDocument(url);
        } catch(e) {}
    }
    if (res === false && ofe_link) {
        window.open(ofe_link, "_self");
        res = true;
    }
    return res;
}

function onClickTable(event) {
    var target = event.target || event.srcElement;
    var opts = {
        href: target.href,
        ofe: target.getAttribute("data-ofe")
    };
    if (target.className === "msoffice") {
        if (openWebDavDocument(opts)) {
            return false;
        }
    }
}
