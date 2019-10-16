/*!
 * froala_editor v3.0.6 (https://www.froala.com/wysiwyg-editor)
 * License https://froala.com/wysiwyg-editor/terms/
 * Copyright 2014-2019 Froala Labs
 */

!function(e,t){"object"==typeof exports&&"undefined"!=typeof module?t(require("froala-editor")):"function"==typeof define&&define.amd?define(["froala-editor"],t):t(e.FroalaEditor)}(this,function(r){"use strict";(r=r&&r.hasOwnProperty("default")?r["default"]:r).URLRegEx="(^| |\\u00A0)("+r.LinkRegEx+"|([a-z0-9+-_.]{1,}@[a-z0-9+-_.]{1,}\\.[a-z0-9+-_]{1,}))$",r.PLUGINS.url=function(i){var l=i.$,a=null;function t(e,t,n){for(var r="";n.length&&"."==n[n.length-1];)r+=".",n=n.substring(0,n.length-1);var o=n;if(i.opts.linkConvertEmailAddress)i.helpers.isEmail(o)&&!/^mailto:.*/i.test(o)&&(o="mailto:"+o);else if(i.helpers.isEmail(o))return t+n;return/^((http|https|ftp|ftps|mailto|tel|sms|notes|data)\:)/i.test(o)||(o="//"+o),(t||"")+"<a"+(i.opts.linkAlwaysBlank?' target="_blank"':"")+(a?' rel="'+a+'"':"")+' data-fr-linked="true" href="'+o+'">'+n.replace(/&amp;/g,"&").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")+"</a>"+r}function s(){return new RegExp(r.URLRegEx,"gi")}function p(e){return i.opts.linkAlwaysNoFollow&&(a="nofollow"),i.opts.linkAlwaysBlank&&(i.opts.linkNoOpener&&(a?a+=" noopener":a="noopener"),i.opts.linkNoReferrer&&(a?a+=" noreferrer":a="noreferrer")),e.replace(s(),t)}function f(e){var t=e.split(" ");return t[t.length-1]}function n(){var e=i.selection.ranges(0),t=e.startContainer;if(!t||t.nodeType!==Node.TEXT_NODE||e.startOffset!==(t.textContent||"").length)return!1;if(function o(e){return!!e&&("A"===e.tagName||!(!e.parentNode||e.parentNode==i.el)&&o(e.parentNode))}(t))return!1;if(s().test(f(t.textContent))){l(t).before(p(t.textContent));var n=l(t.parentNode).find("a[data-fr-linked]");n.removeAttr("data-fr-linked"),t.parentNode.removeChild(t),i.events.trigger("url.linked",[n.get(0)])}else if(t.textContent.split(" ").length<=2&&t.previousSibling&&"A"===t.previousSibling.tagName){var r=t.previousSibling.innerText+t.textContent;s().test(f(r))&&(l(t.previousSibling).replaceWith(p(r)),t.parentNode.removeChild(t))}}return{_init:function e(){i.events.on("keypress",function(e){!i.selection.isCollapsed()||"."!=e.key&&")"!=e.key&&"("!=e.key||n()},!0),i.events.on("keydown",function(e){var t=e.which;!i.selection.isCollapsed()||t!=r.KEYCODE.ENTER&&t!=r.KEYCODE.SPACE||n()},!0),i.events.on("paste.beforeCleanup",function(e){if(i.helpers.isURL(e)){var t=null;return i.opts.linkAlwaysBlank&&(i.opts.linkNoOpener&&(t?t+=" noopener":t="noopener"),i.opts.linkNoReferrer&&(t?t+=" noreferrer":t="noreferrer")),"<a"+(i.opts.linkAlwaysBlank?' target="_blank"':"")+(t?' rel="'+t+'"':"")+' href="'+e+'" >'+e+"</a>"}})}}}});