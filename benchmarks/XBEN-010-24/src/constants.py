# TYPO3 CMS Configuration Constants
# Site configuration defaults

TYPO3_VERSION = '11.5.24'
TYPO3_BRANCH = 'stable'

DEFAULT_PAGE_TSCONFIG = '''
mod.web_layout {
    defLangBinding = 1
}
TCEFORM.tt_content.header_layout {
    removeItems = 3
}
'''

DEFAULT_TYPOSCRIPT_SETUP = '''
page = PAGE
page {
    typeNum = 0
    10 = FLUIDTEMPLATE
    10 {
        templateRootPaths.0 = EXT:bootstrap_package/Resources/Private/Templates/Page/
        templateRootPaths.1 = fileadmin/templates/
        partialRootPaths.0 = EXT:bootstrap_package/Resources/Private/Partials/Page/
        layoutRootPaths.0 = EXT:bootstrap_package/Resources/Private/Layouts/Page/
    }
}

config {
    absRefPrefix = auto
    doctype = html5
    language = en
    locale_all = en_US.UTF-8
    htmlTag_setParams = none
    cache_period = 86400
    sendCacheHeaders = 1
    compressJs = 0
    compressCss = 0
    concatenateJs = 0
    concatenateCss = 0
}

plugin.tx_news {
    settings {
        listPid = 12
        detailPid = 15
    }
}
'''
