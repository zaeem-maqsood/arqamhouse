/*!
 * froala_editor v3.0.6 (https://www.froala.com/wysiwyg-editor)
 * License https://froala.com/wysiwyg-editor/terms/
 * Copyright 2014-2019 Froala Labs
 */

!function(e,t){"object"==typeof exports&&"undefined"!=typeof module?t(require("froala-editor")):"function"==typeof define&&define.amd?define(["froala-editor"],t):t(e.FroalaEditor)}(this,function(e){"use strict";(e=e&&e.hasOwnProperty("default")?e["default"]:e).PLUGINS.fullscreen=function(s){var t,r,o,n,i=s.$;function a(){return s.$box.hasClass("fr-fullscreen")}function l(){if(s.helpers.isIOS()&&s.core.hasFocus())return s.$el.blur(),setTimeout(c,250),!1;t=s.helpers.scrollTop(),s.$box.toggleClass("fr-fullscreen"),i("body").first().toggleClass("fr-fullscreen"),s.helpers.isMobile()&&(s.$tb.data("parent",s.$tb.parent()),s.$box.prepend(s.$tb),s.$tb.data("sticky-dummy")&&s.$tb.after(s.$tb.data("sticky-dummy"))),r=s.opts.height,o=s.opts.heightMax,n=s.opts.zIndex,s.opts.height=s.o_win.innerHeight-(s.opts.toolbarInline?0:s.$tb.outerHeight()+(s.$second_tb?s.$second_tb.outerHeight():0)),s.opts.zIndex=2147483641,s.opts.heightMax=null,s.size.refresh(),s.opts.toolbarInline&&s.toolbar.showInline();for(var e=s.$box.parent();!e.first().is("body");)e.addClass("fr-fullscreen-wrapper"),e=e.parent();s.opts.toolbarContainer&&s.$box.prepend(s.$tb),s.events.trigger("charCounter.update"),s.events.trigger("codeView.update"),s.$win.trigger("scroll")}function f(){if(s.helpers.isIOS()&&s.core.hasFocus())return s.$el.blur(),setTimeout(c,250),!1;s.$box.toggleClass("fr-fullscreen"),i("body").first().toggleClass("fr-fullscreen"),s.$tb.data("parent")&&s.$tb.data("parent").prepend(s.$tb),s.$tb.data("sticky-dummy")&&s.$tb.after(s.$tb.data("sticky-dummy")),s.opts.height=r,s.opts.heightMax=o,s.opts.zIndex=n,s.size.refresh(),i(s.o_win).scrollTop(t),s.opts.toolbarInline&&s.toolbar.showInline(),s.events.trigger("charCounter.update"),s.opts.toolbarSticky&&s.opts.toolbarStickyOffset&&(s.opts.toolbarBottom?s.$tb.css("bottom",s.opts.toolbarStickyOffset).data("bottom",s.opts.toolbarStickyOffset):s.$tb.css("top",s.opts.toolbarStickyOffset).data("top",s.opts.toolbarStickyOffset));for(var e=s.$box.parent();!e.first().is("body");)e.removeClass("fr-fullscreen-wrapper"),e=e.parent();s.opts.toolbarContainer&&i(s.opts.toolbarContainer).append(s.$tb),i(s.o_win).trigger("scroll"),s.events.trigger("codeView.update")}function c(){a()?f():l(),d(s.$tb.find('.fr-command[data-cmd="fullscreen"]'));var e=s.$tb.find('.fr-command[data-cmd="moreText"]'),t=s.$tb.find('.fr-command[data-cmd="moreParagraph"]'),r=s.$tb.find('.fr-command[data-cmd="moreRich"]'),o=s.$tb.find('.fr-command[data-cmd="moreMisc"]');e.length&&s.refresh.moreText(e),t.length&&s.refresh.moreParagraph(t),r.length&&s.refresh.moreRich(r),o.length&&s.refresh.moreMisc(o)}function d(e){var t=a();e.toggleClass("fr-active",t).attr("aria-pressed",t),e.find("> *").not(".fr-sr-only").replaceWith(t?s.icon.create("fullscreenCompress"):s.icon.create("fullscreen"))}return{_init:function e(){if(!s.$wp)return!1;s.events.$on(i(s.o_win),"resize",function(){a()&&(f(),l())}),s.events.on("toolbar.hide",function(){if(a()&&s.helpers.isMobile())return!1}),s.events.on("position.refresh",function(){if(s.helpers.isIOS())return!a()}),s.events.on("destroy",function(){a()&&f()},!0)},toggle:c,refresh:d,isActive:a}},e.RegisterCommand("fullscreen",{title:"Fullscreen",undo:!1,focus:!1,accessibilityFocus:!0,forcedRefresh:!0,toggle:!0,callback:function(){this.fullscreen.toggle()},refresh:function(e){this.fullscreen.refresh(e)},plugin:"fullscreen"}),e.DefineIcon("fullscreen",{NAME:"expand",SVG_KEY:"fullscreen"}),e.DefineIcon("fullscreenCompress",{NAME:"compress",SVG_KEY:"exitFullscreen"})});