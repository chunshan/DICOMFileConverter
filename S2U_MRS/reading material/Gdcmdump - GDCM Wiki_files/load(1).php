var isCompatible=function(){if(navigator.appVersion.indexOf('MSIE')!==-1&&parseFloat(navigator.appVersion.split('MSIE')[1])<6){return false;}return true;};var startUp=function(){mw.config=new mw.Map(true);mw.loader.addSource({"local":{"loadScript":"/wiki/load.php","apiScript":"/wiki/api.php"}});mw.loader.register([["site","1355751448",[],"site"],["noscript","1355751448",[],"noscript"],["startup","1476804878",[],"startup"],["user","1355751448",[],"user"],["user.groups","1355751448",[],"user"],["user.options","1476804878",[],"private"],["user.cssprefs","1476804878",["mediawiki.user"],"private"],["user.tokens","1355751448",[],"private"],["filepage","1355751448",[]],["skins.chick","1355751448",[]],["skins.cologneblue","1355751448",[]],["skins.modern","1355751448",[]],["skins.monobook","1355751448",[]],["skins.nostalgia","1355751448",[]],["skins.simple","1355751448",[]],["skins.standard","1355751448",[]],["skins.vector","1355751448",[]],["jquery","1355751448",[]],["jquery.appear",
"1355751448",[]],["jquery.arrowSteps","1355751448",[]],["jquery.async","1355751448",[]],["jquery.autoEllipsis","1355751448",["jquery.highlightText"]],["jquery.byteLength","1355751448",[]],["jquery.byteLimit","1355751448",["jquery.byteLength"]],["jquery.checkboxShiftClick","1355751448",[]],["jquery.client","1355751448",[]],["jquery.collapsibleTabs","1355751448",[]],["jquery.color","1355751448",["jquery.colorUtil"]],["jquery.colorUtil","1355751448",[]],["jquery.cookie","1355751448",[]],["jquery.delayedBind","1355751448",[]],["jquery.expandableField","1355751448",["jquery.delayedBind"]],["jquery.farbtastic","1355751448",["jquery.colorUtil"]],["jquery.footHovzer","1355751448",[]],["jquery.form","1355751448",[]],["jquery.getAttrs","1355751448",[]],["jquery.highlightText","1355751448",[]],["jquery.hoverIntent","1355751448",[]],["jquery.json","1355751448",[]],["jquery.localize","1355751448",[]],["jquery.makeCollapsible","1421998353",[]],["jquery.messageBox","1355751448",[]],["jquery.mockjax",
"1355751448",[]],["jquery.mw-jump","1355751448",[]],["jquery.mwExtension","1355751448",[]],["jquery.placeholder","1355751448",[]],["jquery.qunit","1355751448",[]],["jquery.qunit.completenessTest","1355751448",["jquery.qunit"]],["jquery.spinner","1355751448",[]],["jquery.suggestions","1355751448",["jquery.autoEllipsis"]],["jquery.tabIndex","1355751448",[]],["jquery.tablesorter","1355751448",[]],["jquery.textSelection","1355751448",[]],["jquery.validate","1355751448",[]],["jquery.xmldom","1355751448",[]],["jquery.tipsy","1355751448",[]],["jquery.ui.core","1355751448",["jquery"],"jquery.ui"],["jquery.ui.widget","1355751448",[],"jquery.ui"],["jquery.ui.mouse","1355751448",["jquery.ui.widget"],"jquery.ui"],["jquery.ui.position","1355751448",[],"jquery.ui"],["jquery.ui.draggable","1355751448",["jquery.ui.core","jquery.ui.mouse","jquery.ui.widget"],"jquery.ui"],["jquery.ui.droppable","1355751448",["jquery.ui.core","jquery.ui.mouse","jquery.ui.widget","jquery.ui.draggable"],"jquery.ui"],[
"jquery.ui.resizable","1355751448",["jquery.ui.core","jquery.ui.widget","jquery.ui.mouse"],"jquery.ui"],["jquery.ui.selectable","1355751448",["jquery.ui.core","jquery.ui.widget","jquery.ui.mouse"],"jquery.ui"],["jquery.ui.sortable","1355751448",["jquery.ui.core","jquery.ui.widget","jquery.ui.mouse"],"jquery.ui"],["jquery.ui.accordion","1355751448",["jquery.ui.core","jquery.ui.widget"],"jquery.ui"],["jquery.ui.autocomplete","1355751448",["jquery.ui.core","jquery.ui.widget","jquery.ui.position"],"jquery.ui"],["jquery.ui.button","1355751448",["jquery.ui.core","jquery.ui.widget"],"jquery.ui"],["jquery.ui.datepicker","1355751448",["jquery.ui.core"],"jquery.ui"],["jquery.ui.dialog","1355751448",["jquery.ui.core","jquery.ui.widget","jquery.ui.button","jquery.ui.draggable","jquery.ui.mouse","jquery.ui.position","jquery.ui.resizable"],"jquery.ui"],["jquery.ui.progressbar","1355751448",["jquery.ui.core","jquery.ui.widget"],"jquery.ui"],["jquery.ui.slider","1355751448",["jquery.ui.core",
"jquery.ui.widget","jquery.ui.mouse"],"jquery.ui"],["jquery.ui.tabs","1355751448",["jquery.ui.core","jquery.ui.widget"],"jquery.ui"],["jquery.effects.core","1355751448",["jquery"],"jquery.ui"],["jquery.effects.blind","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.bounce","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.clip","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.drop","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.explode","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.fade","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.fold","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.highlight","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.pulsate","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.scale","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.shake","1355751448",["jquery.effects.core"],
"jquery.ui"],["jquery.effects.slide","1355751448",["jquery.effects.core"],"jquery.ui"],["jquery.effects.transfer","1355751448",["jquery.effects.core"],"jquery.ui"],["mediawiki","1355751448",[]],["mediawiki.api","1355751448",["mediawiki.util"]],["mediawiki.api.category","1355751448",["mediawiki.api","mediawiki.Title"]],["mediawiki.api.edit","1355751448",["mediawiki.api","mediawiki.Title"]],["mediawiki.api.parse","1355751448",["mediawiki.api"]],["mediawiki.api.titleblacklist","1355751448",["mediawiki.api","mediawiki.Title"]],["mediawiki.api.watch","1355751448",["mediawiki.api","mediawiki.user"]],["mediawiki.debug","1355751448",["jquery.footHovzer"]],["mediawiki.debug.init","1355751448",["mediawiki.debug"]],["mediawiki.feedback","1355751448",["mediawiki.api.edit","mediawiki.Title","mediawiki.jqueryMsg","jquery.ui.dialog"]],["mediawiki.htmlform","1355751448",[]],["mediawiki.Title","1355751448",["mediawiki.util"]],["mediawiki.Uri","1355751448",[]],["mediawiki.user","1355751448",[
"jquery.cookie"]],["mediawiki.util","1421998353",["jquery.client","jquery.cookie","jquery.messageBox","jquery.mwExtension"]],["mediawiki.action.edit","1355751448",["jquery.textSelection","jquery.byteLimit"]],["mediawiki.action.history","1355751448",["jquery.ui.button"],"mediawiki.action.history"],["mediawiki.action.history.diff","1355751448",[],"mediawiki.action.history"],["mediawiki.action.view.dblClickEdit","1355751448",["mediawiki.util"]],["mediawiki.action.view.metadata","1424556518",[]],["mediawiki.action.view.rightClickEdit","1355751448",[]],["mediawiki.action.watch.ajax","1426834812",["mediawiki.api.watch","mediawiki.util"]],["mediawiki.language","1355751448",[]],["mediawiki.jqueryMsg","1355751448",["mediawiki.language","mediawiki.util"]],["mediawiki.libs.jpegmeta","1355751448",[]],["mediawiki.page.ready","1355751448",["jquery.checkboxShiftClick","jquery.makeCollapsible","jquery.placeholder","jquery.mw-jump","mediawiki.util"]],["mediawiki.page.startup","1355751448",[
"jquery.client","mediawiki.util"]],["mediawiki.special","1355751448",[]],["mediawiki.special.block","1355751448",["mediawiki.util"]],["mediawiki.special.changeemail","1355751448",["mediawiki.util"]],["mediawiki.special.changeslist","1355751448",["jquery.makeCollapsible"]],["mediawiki.special.movePage","1355751448",["jquery.byteLimit"]],["mediawiki.special.preferences","1355751448",[]],["mediawiki.special.recentchanges","1355751448",["mediawiki.special"]],["mediawiki.special.search","1355751448",[]],["mediawiki.special.undelete","1355751448",[]],["mediawiki.special.upload","1355751448",["mediawiki.libs.jpegmeta","mediawiki.util"]],["mediawiki.special.javaScriptTest","1355751448",["jquery.qunit"]],["mediawiki.tests.qunit.testrunner","1355751448",["jquery.qunit","jquery.qunit.completenessTest","mediawiki.page.startup","mediawiki.page.ready"]],["mediawiki.legacy.ajax","1355751448",["mediawiki.util","mediawiki.legacy.wikibits"]],["mediawiki.legacy.commonPrint","1355751448",[]],[
"mediawiki.legacy.config","1355751448",["mediawiki.legacy.wikibits"]],["mediawiki.legacy.IEFixes","1355751448",["mediawiki.legacy.wikibits"]],["mediawiki.legacy.mwsuggest","1355751448",["mediawiki.legacy.wikibits"]],["mediawiki.legacy.preview","1355751448",["mediawiki.legacy.wikibits"]],["mediawiki.legacy.protect","1355751448",["mediawiki.legacy.wikibits","jquery.byteLimit"]],["mediawiki.legacy.shared","1355751448",[]],["mediawiki.legacy.oldshared","1355751448",[]],["mediawiki.legacy.upload","1355751448",["mediawiki.legacy.wikibits","mediawiki.util"]],["mediawiki.legacy.wikibits","1355751448",["mediawiki.util"]],["mediawiki.legacy.wikiprintable","1355751448",[]],["ext.nuke","1355751448",[]]]);mw.config.set({"wgLoadScript":"/wiki/load.php","debug":false,"skin":"vector","stylepath":"/wiki/skins","wgUrlProtocols":
"http\\:\\/\\/|https\\:\\/\\/|ftp\\:\\/\\/|irc\\:\\/\\/|ircs\\:\\/\\/|gopher\\:\\/\\/|telnet\\:\\/\\/|nntp\\:\\/\\/|worldwind\\:\\/\\/|mailto\\:|news\\:|svn\\:\\/\\/|git\\:\\/\\/|mms\\:\\/\\/|\\/\\/","wgArticlePath":"/wiki/index.php/$1","wgScriptPath":"/wiki","wgScriptExtension":".php","wgScript":"/wiki/index.php","wgVariantArticlePath":false,"wgActionPaths":{},"wgServer":"http://gdcm.sourceforge.net","wgUserLanguage":"en","wgContentLanguage":"en","wgVersion":"1.19.2","wgEnableAPI":true,"wgEnableWriteAPI":true,"wgDefaultDateFormat":"dmy","wgMonthNames":["","January","February","March","April","May","June","July","August","September","October","November","December"],"wgMonthNamesShort":["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"wgMainPageTitle":"Main Page","wgFormattedNamespaces":{"-2":"Media","-1":"Special","0":"","1":"Talk","2":"User","3":"User talk","4":"GDCM Wiki","5":"GDCM Wiki talk","6":"File","7":"File talk","8":"MediaWiki","9":"MediaWiki talk",
"10":"Template","11":"Template talk","12":"Help","13":"Help talk","14":"Category","15":"Category talk"},"wgNamespaceIds":{"media":-2,"special":-1,"":0,"talk":1,"user":2,"user_talk":3,"gdcm_wiki":4,"gdcm_wiki_talk":5,"file":6,"file_talk":7,"mediawiki":8,"mediawiki_talk":9,"template":10,"template_talk":11,"help":12,"help_talk":13,"category":14,"category_talk":15,"image":6,"image_talk":7,"project":4,"project_talk":5},"wgSiteName":"GDCM Wiki","wgFileExtensions":["png","gif","jpg","jpeg"],"wgDBname":"g137895_mediawiki","wgFileCanRotate":true,"wgAvailableSkins":{"monobook":"MonoBook","chick":"Chick","myskin":"MySkin","modern":"Modern","nostalgia":"Nostalgia","vector":"Vector","cologneblue":"CologneBlue","simple":"Simple","standard":"Standard"},"wgExtensionAssetsPath":"/wiki/extensions","wgCookiePrefix":"g137895_mediawiki","wgResourceLoaderMaxQueryLength":-1,"wgCaseSensitiveNamespaces":[]});};if(isCompatible()){document.write(
"\x3cscript src=\"/wiki/load.php?debug=false\x26amp;lang=en\x26amp;modules=jquery%2Cmediawiki\x26amp;only=scripts\x26amp;skin=vector\x26amp;version=20120830T222535Z\"\x3e\x3c/script\x3e");}delete isCompatible;;

/* cache key: g137895_mediawiki:resourceloader:filter:minify-js:7:8349c1fc5687a2d3a795bb00ffb606b0 */
