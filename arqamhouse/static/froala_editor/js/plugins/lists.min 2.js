/*!
 * froala_editor v3.0.6 (https://www.froala.com/wysiwyg-editor)
 * License https://froala.com/wysiwyg-editor/terms/
 * Copyright 2014-2019 Froala Labs
 */

!function(e,t){"object"==typeof exports&&"undefined"!=typeof module?t(require("froala-editor")):"function"==typeof define&&define.amd?define(["froala-editor"],t):t(e.FroalaEditor)}(this,function(p){"use strict";p=p&&p.hasOwnProperty("default")?p["default"]:p,Object.assign(p.DEFAULTS,{listAdvancedTypes:!0}),p.PLUGINS.lists=function(d){var c=d.$;function g(e){return'<span class="fr-open-'+e.toLowerCase()+'"></span>'}function m(e){return'<span class="fr-close-'+e.toLowerCase()+'"></span>'}function i(e,t){!function f(e,t){for(var a=[],n=0;n<e.length;n++){var r=e[n].parentNode;"LI"==e[n].tagName&&r.tagName!=t&&a.indexOf(r)<0&&a.push(r)}for(var i=a.length-1;0<=i;i--){var s=c(a[i]);s.replaceWith("<"+t.toLowerCase()+" "+d.node.attributes(s.get(0))+">"+s.html()+"</"+t.toLowerCase()+">")}}(e,t);var a,n=d.html.defaultTag(),r=null;e.length&&(a="rtl"==d.opts.direction||"rtl"==c(e[0]).css("direction")?"margin-right":"margin-left");for(var i=0;i<e.length;i++)if("TD"!=e[i].tagName&&"TH"!=e[i].tagName&&"LI"!=e[i].tagName){var s=d.helpers.getPX(c(e[i]).css(a))||0;(e[i].style.marginLeft=null)===r&&(r=s);var o=0<r?"<"+t+' style="'+a+": "+r+'px ">':"<"+t+">",l="</"+t+">";for(s-=r;0<s/d.opts.indentMargin;)o+="<"+t+">",l+=l,s-=d.opts.indentMargin;n&&e[i].tagName.toLowerCase()==n?c(e[i]).replaceWith(o+"<li"+d.node.attributes(e[i])+">"+c(e[i]).html()+"</li>"+l):c(e[i]).wrap(o+"<li></li>"+l)}d.clean.lists()}function s(e){var t,a;for(t=e.length-1;0<=t;t--)for(a=t-1;0<=a;a--)if(c(e[a]).find(e[t]).length||e[a]==e[t]){e.splice(t,1);break}var n=[];for(t=0;t<e.length;t++){var r=c(e[t]),i=e[t].parentNode,s=r.attr("class");if(r.before(m(i.tagName)),"LI"==i.parentNode.tagName)r.before(m("LI")),r.after(g("LI"));else{var o="";s&&(o+=' class="'+s+'"');var l="rtl"==d.opts.direction||"rtl"==r.css("direction")?"margin-right":"margin-left";d.helpers.getPX(c(i).css(l))&&0<=(c(i).attr("style")||"").indexOf(l+":")&&(o+=' style="'+l+":"+d.helpers.getPX(c(i).css(l))+'px;"'),d.html.defaultTag()&&0===r.find(d.html.blockTagsQuery()).length&&r.wrapInner(d.html.defaultTag()+o),d.node.isEmpty(r.get(0),!0)||0!==r.find(d.html.blockTagsQuery()).length||r.append("<br>"),r.append(g("LI")),r.prepend(m("LI"))}r.after(g(i.tagName)),"LI"==i.parentNode.tagName&&(i=i.parentNode.parentNode),n.indexOf(i)<0&&n.push(i)}for(t=0;t<n.length;t++){var f=c(n[t]),p=f.html();p=(p=p.replace(/<span class="fr-close-([a-z]*)"><\/span>/g,"</$1>")).replace(/<span class="fr-open-([a-z]*)"><\/span>/g,"<$1>"),f.replaceWith(d.node.openTagString(f.get(0))+p+d.node.closeTagString(f.get(0)))}d.$el.find("li:empty").remove(),d.$el.find("ul:empty, ol:empty").remove(),d.clean.lists(),d.html.wrap()}function o(e){d.selection.save();for(var t=0;t<e.length;t++){var a=e[t].previousSibling;if(a){var n=c(e[t]).find("> ul, > ol").last().get(0);if(n){var r=c(document.createElement("li"));c(n).prepend(r);for(var i=d.node.contents(e[t])[0];i&&!d.node.isList(i);){var s=i.nextSibling;r.append(i),i=s}c(a).append(c(n)),c(e[t]).remove()}else{var o=c(a).find("> ul, > ol").last().get(0);if(o)c(o).append(c(e[t]));else{var l=c("<"+e[t].parentNode.tagName+">");c(a).append(l),l.append(c(e[t]))}}}}d.clean.lists(),d.selection.restore()}function l(e){d.selection.save(),s(e),d.selection.restore()}function e(e){if("indent"==e||"outdent"==e){var t=!1,a=d.selection.blocks(),n=[],r=a[0].previousSibling||a[0].parentElement;if("outdent"==e){if("LI"==r.tagName||"LI"!=r.parentNode.tagName)return}else if(!a[0].previousSibling||"LI"!=a[0].previousSibling.tagName)return;for(var i=0;i<a.length;i++)"LI"==a[i].tagName?(t=!0,n.push(a[i])):"LI"==a[i].parentNode.tagName&&(t=!0,n.push(a[i].parentNode));t&&("indent"==e?o(n):l(n))}}return{_init:function t(){d.events.on("commands.after",e),d.events.on("keydown",function(e){if(e.which==p.KEYCODE.TAB){for(var t=d.selection.blocks(),a=[],n=0;n<t.length;n++)"LI"==t[n].tagName?a.push(t[n]):"LI"==t[n].parentNode.tagName&&a.push(t[n].parentNode);if(1<a.length||a.length&&(d.selection.info(a[0]).atStart||d.node.isEmpty(a[0])))return e.preventDefault(),e.stopPropagation(),e.shiftKey?l(a):o(a),!1}},!0)},format:function f(e,t){var a,n;for(d.selection.save(),d.html.wrap(!0,!0,!0,!0),d.selection.restore(),n=d.selection.blocks(),a=0;a<n.length;a++)"LI"!=n[a].tagName&&"LI"==n[a].parentNode.tagName&&(n[a]=n[a].parentNode);if(d.selection.save(),function r(e,t){for(var a=!0,n=0;n<e.length;n++){if("LI"!=e[n].tagName)return!1;e[n].parentNode.tagName!=t&&(a=!1)}return a}(n,e)?t||s(n):i(n,e),d.html.unwrap(),d.selection.restore(),t=t||"default"){for(n=d.selection.blocks(),a=0;a<n.length;a++)"LI"!=n[a].tagName&&"LI"==n[a].parentNode.tagName&&(n[a]=n[a].parentNode);for(a=0;a<n.length;a++)"LI"==n[a].tagName&&(c(n[a].parentNode).css("list-style-type","default"===t?"":t),0===(c(n[a].parentNode).attr("style")||"").length&&c(n[a].parentNode).removeAttr("style"))}},refresh:function r(e,t){var a=c(d.selection.element());if(a.get(0)!=d.el){var n=a.get(0);(n="LI"!=n.tagName&&n.firstElementChild&&"LI"!=n.firstElementChild.tagName?a.parents("li").get(0):"LI"==n.tagName||n.firstElementChild?n.firstElementChild&&"LI"==n.firstElementChild.tagName?a.get(0).firstChild:a.get(0):a.parents("li").get(0))&&n.parentNode.tagName==t&&d.el.contains(n.parentNode)&&e.addClass("fr-active")}}}},p.DefineIcon("formatOLSimple",{NAME:"list-ol",SVG_KEY:"orderedList"}),p.RegisterCommand("formatOLSimple",{title:"Ordered List",type:"button",options:{"default":"Default",circle:"Circle",disc:"Disc",square:"Square"},refresh:function(e){this.lists.refresh(e,"OL")},callback:function(e,t){this.lists.format("OL",t)},plugin:"lists"}),p.RegisterCommand("formatUL",{title:"Unordered List",type:"button",hasOptions:function(){return this.opts.listAdvancedTypes},options:{"default":"Default",circle:"Circle",disc:"Disc",square:"Square"},refresh:function(e){this.lists.refresh(e,"UL")},callback:function(e,t){this.lists.format("UL",t)},plugin:"lists"}),p.RegisterCommand("formatOL",{title:"Ordered List",hasOptions:function(){return this.opts.listAdvancedTypes},options:{"default":"Default","lower-alpha":"Lower Alpha","lower-greek":"Lower Greek","lower-roman":"Lower Roman","upper-alpha":"Upper Alpha","upper-roman":"Upper Roman"},refresh:function(e){this.lists.refresh(e,"OL")},callback:function(e,t){this.lists.format("OL",t)},plugin:"lists"}),p.DefineIcon("formatUL",{NAME:"list-ul",SVG_KEY:"unorderedList"}),p.DefineIcon("formatOL",{NAME:"list-ol",SVG_KEY:"orderedList"})});