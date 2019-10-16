/*!
 * froala_editor v3.0.6 (https://www.froala.com/wysiwyg-editor)
 * License https://froala.com/wysiwyg-editor/terms/
 * Copyright 2014-2019 Froala Labs
 */

!function(e,a){"object"==typeof exports&&"undefined"!=typeof module?a(require("froala-editor")):"function"==typeof define&&define.amd?define(["froala-editor"],a):a(e.FroalaEditor)}(this,function(A){"use strict";if(A=A&&A.hasOwnProperty("default")?A["default"]:A,Object.assign(A.DEFAULTS,{imageManagerLoadURL:"https://i.froala.com/load-files",imageManagerLoadMethod:"get",imageManagerLoadParams:{},imageManagerPreloader:null,imageManagerDeleteURL:"",imageManagerDeleteMethod:"post",imageManagerDeleteParams:{},imageManagerPageSize:12,imageManagerScrollOffset:20,imageManagerToggleTags:!0}),A.PLUGINS.imageManager=function(s){var g,l,i,o,d,m,f,c,u,p,h,v=s.$,M="image_manager",e=10,b=11,w=12,C=13,L=14,D=15,t=21,r=22,n={};function y(){var e=v(window).outerWidth();return e<768?2:e<1200?3:4}function P(){d.empty();for(var e=0;e<h;e++)d.append('<div class="fr-list-column"></div>')}function I(){if(u<f.length&&(d.outerHeight()<=i.outerHeight()+s.opts.imageManagerScrollOffset||i.scrollTop()+s.opts.imageManagerScrollOffset>d.outerHeight()-i.outerHeight())){c++;for(var e=s.opts.imageManagerPageSize*(c-1);e<Math.min(f.length,s.opts.imageManagerPageSize*c);e++)a(f[e])}}function a(n){var i=new Image,o=v(document.createElement("div")).attr("class","fr-image-container fr-empty fr-image-"+p++).attr("data-loading",s.language.translate("Loading")+"..").attr("data-deleting",s.language.translate("Deleting")+"..");R(!1),i.onload=function(){o.height(Math.floor(o.width()/i.width*i.height));var t=v(document.createElement("img"));if(n.thumb)t.attr("src",n.thumb);else{if(O(L,n),!n.url)return O(D,n),!1;t.attr("src",n.url)}if(n.url&&t.attr("data-url",n.url),n.tag)if(l.find(".fr-modal-more.fr-not-available").removeClass("fr-not-available"),l.find(".fr-modal-tags").show(),0<=n.tag.indexOf(",")){for(var e=n.tag.split(","),a=0;a<e.length;a++)e[a]=e[a].trim(),0===m.find('a[title="'+e[a]+'"]').length&&m.append('<a role="button" title="'+e[a]+'">'+e[a]+"</a>");t.attr("data-tag",e.join())}else 0===m.find('a[title="'+n.tag.trim()+'"]').length&&m.append('<a role="button" title="'+n.tag.trim()+'">'+n.tag.trim()+"</a>"),t.attr("data-tag",n.tag.trim());for(var r in n.name&&t.attr("alt",n.name),n)n.hasOwnProperty(r)&&"thumb"!==r&&"url"!==r&&"tag"!==r&&t.attr("data-"+r,n[r]);o.append(t).append(v(s.icon.create("imageManagerDelete")).addClass("fr-delete-img").attr("title",s.language.translate("Delete"))).append(v(s.icon.create("imageManagerInsert")).addClass("fr-insert-img").attr("title",s.language.translate("Insert"))),m.find(".fr-selected-tag").each(function(e,a){k(t,a.text)||o.hide()}),t.on("load",function(){o.removeClass("fr-empty"),o.height("auto"),u++,E(T(parseInt(t.parent().attr("class").match(/fr-image-(\d+)/)[1],10)+1)),R(!1),u%s.opts.imageManagerPageSize==0&&I()}),s.events.trigger("imageManager.imageLoaded",[t])},i.onerror=function(){u++,o.remove(),E(T(parseInt(o.attr("class").match(/fr-image-(\d+)/)[1],10)+1)),O(e,n),u%s.opts.imageManagerPageSize==0&&I()},i.src=n.thumb||n.url,S().append(o)}function S(){var r,n;return d.find(".fr-list-column").each(function(e,a){var t=v(a);0===e?(n=t.outerHeight(),r=t):t.outerHeight()<n&&(n=t.outerHeight(),r=t)}),r}function T(e){e===undefined&&(e=0);for(var a=[],t=p-1;e<=t;t--){var r=d.find(".fr-image-"+t);r.length&&(a.push(r),v(document.createElement("div")).attr("id","fr-image-hidden-container").append(r),d.find(".fr-image-"+t).remove())}return a}function E(e){for(var a=e.length-1;0<=a;a--)S().append(e[a])}function R(e){if(e===undefined&&(e=!0),!g.isVisible())return!0;var a=y();if(a!==h){h=a;var t=T();P(),E(t)}s.modals.resize(M),e&&I()}function U(e){var a={},t=e.data();for(var r in t)t.hasOwnProperty(r)&&"url"!==r&&"tag"!==r&&(a[r]=t[r]);return a}function x(e){var a=v(e.currentTarget).siblings("img"),t=g.data("instance")||s,r=g.data("current-image");if(s.modals.hide(M),t.image.showProgressBar(),r)r.data("fr-old-src",r.attr("src")),r.trigger("click");else{t.events.focus(!0),t.selection.restore();var n=t.position.getBoundingRect(),i=n.left+n.width/2+v(s.doc).scrollLeft(),o=n.top+n.height+v(s.doc).scrollTop();t.popups.setContainer("image.insert",s.$sc),t.popups.show("image.insert",i,o)}t.image.insert(a.data("url"),!1,U(a),r)}function H(e){var i=v(e.currentTarget).siblings("img"),a=s.language.translate("Are you sure? Image will be deleted.");confirm(a)&&(s.opts.imageManagerDeleteURL?!1!==s.events.trigger("imageManager.beforeDeleteImage",[i])&&(i.parent().addClass("fr-image-deleting"),v(this).ajax({method:s.opts.imageManagerDeleteMethod,url:s.opts.imageManagerDeleteURL,data:Object.assign(Object.assign({src:i.attr("src")},U(i)),s.opts.imageManagerDeleteParams),crossDomain:s.opts.requestWithCORS,withCredentials:s.opts.requestWithCredentials,headers:s.opts.requestHeaders,done:function(e,a,t){s.events.trigger("imageManager.imageDeleted",[e]);var r=T(parseInt(i.parent().attr("class").match(/fr-image-(\d+)/)[1],10)+1);i.parent().remove(),E(r),function n(){g.find("#fr-modal-tags > a").each(function(){0===g.find('#fr-image-list [data-tag*="'+v(this).text()+'"]').length&&v(this).removeClass("fr-selected-tag").hide()}),_()}(),R(!0)},fail:function(e){O(t,e.response||e.responseText)}})):O(r))}function O(e,a){10<=e&&e<20?o.hide():20<=e&&e<30&&v(".fr-image-deleting").removeClass("fr-image-deleting"),s.events.trigger("imageManager.error",[{code:e,message:n[e]},a])}function q(){var e=l.find(".fr-modal-head-line").outerHeight(),a=m.outerHeight();l.toggleClass("fr-show-tags"),l.hasClass("fr-show-tags")?(l.css("height",e+a),i.css("marginTop",e+a),m.find("a").css("opacity",1)):(l.css("height",e),i.css("marginTop",e),m.find("a").css("opacity",0))}function _(){var e=m.find(".fr-selected-tag");0<e.length?(d.find("img").parents().show(),e.each(function(e,r){d.find("img").each(function(e,a){var t=v(a);k(t,r.text)||t.parent().hide()})})):d.find("img").parents().show(),E(T()),I()}function j(e){e.preventDefault();var a=v(e.currentTarget);a.toggleClass("fr-selected-tag"),s.opts.imageManagerToggleTags&&a.siblings("a").removeClass("fr-selected-tag"),_()}function k(e,a){for(var t=(e.attr("data-tag")||"").split(","),r=0;r<t.length;r++)if(t[r]===a)return!0;return!1}return n[e]="Image cannot be loaded from the passed link.",n[b]="Error during load images request.",n[w]="Missing imageManagerLoadURL option.",n[C]="Parsing load response failed.",n[L]="Missing image thumb.",n[D]="Missing image URL.",n[t]="Error during delete image request.",n[r]="Missing imageManagerDeleteURL option.",{require:["image"],_init:function z(){if(!s.$wp&&"IMG"!==s.el.tagName)return!1},show:function G(){if(!g){var e,a='<button class="fr-command fr-btn fr-modal-more fr-not-available" id="fr-modal-more-'.concat(s.sid,'"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24""><path d="').concat(A.SVG.tags,'"/></svg></button><h4 data-text="true">').concat(s.language.translate("Manage Images"),'</h4></div>\n      <div class="fr-modal-tags" id="fr-modal-tags">');e=s.opts.imageManagerPreloader?'<img class="fr-preloader" id="fr-preloader" alt="'+s.language.translate("Loading")+'.." src="'+s.opts.imageManagerPreloader+'" style="display: none;">':'<span class="fr-preloader" id="fr-preloader" style="display: none;">'+s.language.translate("Loading")+"</span>",e+='<div class="fr-image-list" id="fr-image-list"></div>';var t=s.modals.create(M,a,e);g=t.$modal,l=t.$head,i=t.$body}g.data("current-image",s.image.get()),s.modals.show(M),o||function r(){o=g.find("#fr-preloader"),d=g.find("#fr-image-list"),m=g.find("#fr-modal-tags"),h=y(),P(),l.css("height",l.find(".fr-modal-head-line").outerHeight()),s.events.$on(v(s.o_win),"resize",function(){R(!!f)}),s.events.bindClick(d,".fr-insert-img",x),s.events.bindClick(d,".fr-delete-img",H),s.helpers.isMobile()&&(s.events.bindClick(d,"div.fr-image-container",function(e){g.find(".fr-mobile-selected").removeClass("fr-mobile-selected"),v(e.currentTarget).addClass("fr-mobile-selected")}),g.on(s._mousedown,function(){g.find(".fr-mobile-selected").removeClass("fr-mobile-selected")})),g.on(s._mousedown+" "+s._mouseup,function(e){e.stopPropagation()}),g.on(s._mousedown,"*",function(){s.events.disableBlur()}),i.on("scroll",I),s.events.bindClick(g,"button#fr-modal-more-"+s.sid,q),s.events.bindClick(m,"a",j)}(),function n(){o.show(),d.find(".fr-list-column").empty(),s.opts.imageManagerLoadURL?v(this).ajax({url:s.opts.imageManagerLoadURL,method:s.opts.imageManagerLoadMethod,data:s.opts.imageManagerLoadParams,dataType:"json",crossDomain:s.opts.requestWithCORS,withCredentials:s.opts.requestWithCredentials,headers:s.opts.requestHeaders,done:function(e,a,t){s.events.trigger("imageManager.imagesLoaded",[e]),function r(e,a){try{d.find(".fr-list-column").empty(),p=u=c=0,f=e,I()}catch(t){O(C,a)}}(e,t.response),o.hide()},fail:function(e){O(b,e.response||e.responseText)}}):O(w)}()},hide:function $(){s.modals.hide(M)}}},!A.PLUGINS.image)throw new Error("Image manager plugin requires image plugin.");A.DEFAULTS.imageInsertButtons.push("imageManager"),A.RegisterCommand("imageManager",{title:"Browse",undo:!1,focus:!1,modal:!0,callback:function(){this.imageManager.show()},plugin:"imageManager"}),A.DefineIcon("imageManager",{NAME:"folder",SVG_KEY:"imageManager"}),A.DefineIcon("imageManagerInsert",{NAME:"plus",SVG_KEY:"add"}),A.DefineIcon("imageManagerDelete",{NAME:"trash",SVG_KEY:"remove"})});