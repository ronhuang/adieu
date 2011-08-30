// Midautumn
// Copyright 2011 Ron Huang
// See LICENSE for details.


// Config timeago library
// Traditional Chinese
jQuery.timeago.settings.strings = {
  prefixAgo: null,
  prefixFromNow: null,
  suffixAgo: "前",
  suffixFromNow: "後",
  seconds: "不到 1 分鐘",
  minute: "約 1 分鐘",
  minutes: "%d 分鐘",
  hour: "約 1 小時",
  hours: "約 %d 小時",
  day: "1 天",
  days: "%d 天",
  month: "約 1 個月",
  months: "%d 個月",
  year: "約 1 年",
  years: "%d 年",
  numbers: []
}


$(document).ready(function(){

  // facebook init
  window.fbAsyncInit = function() {
    FB.init({
      appId: '271148119565356',
      status: true,
      cookie: true,
      xfbml: true,
      channelUrl: document.location.protocol + '//' + document.location.host + '/channel',
      oauth: true
    });

    FB.getLoginStatus(loginStatusChanged);
    FB.Event.subscribe('edge.create', edgeCreated);
    FB.Event.subscribe('edge.remove', edgeRemoved);
    FB.Event.subscribe('comment.create', commentCreated);
    FB.Event.subscribe('comment.remove', commentRemoved);
  };

  (function() {
    var e = document.createElement('script');
    e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
    e.async = true;
    document.getElementById('fb-root').appendChild(e);
  }());


  // prompt achievements
  var handleAchievements = function (achievements) {
    for (var i in achievements) {
      var achi = achievements[i];
      var className = 'achievement' + Math.floor(Math.random() * 1000);

      var html = '<div class="alert-message info ' + className + '" style="display: none;">';
      html += '<img alt="成就圖示" src="' + achi.icon_url + '" width="64" height="64">';
      html += '<p><strong>' + achi.title + '</strong></p>';
      //html += '<a href="#" class="close">x</a>';
      html += '<p>' + achi.description + '</p>';
      html += '</div>';

      var dlg = $(html);
      dlg.appendTo($('#notification .placement'));
      dlg.fadeIn('fast');
      setTimeout("$('#notification ." + className + "').fadeOut('fast');", 10000);
    }
  };


  // inform server about this visit
  $.post('/api/visit', function (data, status) {
    if (data.result == 'success') {
      handleAchievements(data.achievements);
    } else {
    }
  }, 'json');


  // new object row
  var newObjectRow = function (obj) {
    var cloned = $('#list-template .row').clone();

    var fb_like = '<fb:like href="' + obj.absolute_url + '" send="false" ' +
      'layout="button_count" width="200" show_faces="false" ' +
      'action="like"></fb:like>';
    $(fb_like).appendTo(cloned.find('.like'));

    var fb_comment_count = '<fb:comments-count href="' + obj.absolute_url + '">0</fb:comments>';
    $(fb_comment_count).appendTo(cloned.find('.comment-container .count span'));

    cloned.find('.title').text(obj.title);
    cloned.find('.timeago').attr('href', obj.relative_url).attr('title', obj.pubtime.iso8601).text(obj.pubtime.localized).timeago();
    cloned.find('.delete').attr('title', '刪除' + obj.title).addClass(obj.modifiable ? 'modifiable' : '');
    cloned.find('img:first').attr('src', obj.owner_picture);
    cloned.find('.timestamp').text(obj.timestamp);

    FB.XFBML.parse(cloned[0]);

    return cloned;
  };


  // object posted
  var objectPosted = function (data, status) {
    var field = $('#add input[name=title]');
    var button = $('#add button[type=submit]')

    if (data.result == 'success') {
      var container = $('#list');

      var latest_title = container.find('.row:first').text()

      // append retrieved objects
      for (var i = data.objects.length - 1; i >= 0; i--) {
        var obj = data.objects[i];

        if (latest_title == obj.title) {
          // should only happen at the old obj,
          // due to the poor resolution of timestamp
          continue;
        }

        var cloned = newObjectRow(obj);
        cloned.prependTo(container).fadeIn('slow');
      }

      // handle achievements
      handleAchievements(data.achievements);
    } else {
      // show error message
    }

    field.removeAttr('disabled');
    field.val('');
  };

  // The url that was liked is returned
  var edgeCreated = function (url) {
    $.post('/api/edge', {url: url, action: 'create'}, function (data, status) {
      if (data.result == 'success') {
        handleAchievements(data.achievements);
      } else {
      }
    });
  };

  // The url that was unliked is returned
  var edgeRemoved = function (url) {
    $.post('/api/edge', {url: url, action: 'remove'}, function (data, status) {
      if (data.result == 'success') {
        handleAchievements(data.achievements);
      } else {
      }
    });
  };

  // {href: '', commentID: ''}
  var commentCreated = function (response) {
    $.post('/api/comment', {href: response.href, commentID: response.commentID, action: 'create'}, function (data, status) {
      if (data.result == 'success') {
        handleAchievements(data.achievements);
      } else {
      }
    });
  };

  // {href: '', commentID: ''}
  var commentRemoved = function (response) {
    $.post('/api/comment', {href: response.href, commentID: response.commentID, action: 'remove'}, function (data, status) {
      if (data.result == 'success') {
        handleAchievements(data.achievements);
      } else {
      }
    });
  };


  // update info after login status changed
  var loginStatusChanged = function (response) {
    // subscribe here to avoid invoking loginStatusChanged twice.
    FB.Event.subscribe('auth.statusChange', loginStatusChanged);

    if (response.authResponse) {
      // get profile if needed
      var profile_hidden = $('#navbar li.menu').hasClass('hidden');

      if (profile_hidden) {
        FB.api('/me', function (info) {
          var url = '/profile/' + info.id;
          var picture = 'http://graph.facebook.com/' + info.id + '/picture?type=square';
          var name = info.name;

          // update profile info
          $('#navbar .profile a').attr('href', url);
          $('#navbar a.menu img').attr('src', picture);
          $('#navbar a.menu span').text(name);

          // show elements displaying profile info
          $('#navbar li.menu').removeClass('hidden');
          $('#navbar li.login').addClass('hidden');
        });
      }
    } else {
      // hide elements displaying profile info
      $('#navbar li.menu').addClass('hidden');
      $('#navbar li.login').removeClass('hidden');
    }
  };


  // menu
  $("body").bind("click", function(e) {
    $("ul.menu-dropdown").hide();
    $('a.menu').parent("li").removeClass("open").children("ul.menu-dropdown").hide();
  });

  $("a.menu").click(function(e) {
    var $target = $(this);
    var $parent = $target.parent("li");
    var $siblings = $target.siblings("ul.menu-dropdown");
    var $parentSiblings = $parent.siblings("li");
    if ($parent.hasClass("open")) {
      $parent.removeClass("open");
      $siblings.hide();
    } else {
      $parent.addClass("open");
      $siblings.show();
    }
    $parentSiblings.children("ul.menu-dropdown").hide();
    $parentSiblings.removeClass("open");
    return false;
  });

  // logout
  $("a.logout").click(function (e) {
    e.preventDefault();

    FB.logout(function (response) {
      document.location.reload(true);
    });
  });


  // prevent invalid input...
  $('#add input[name=title]').keyup(function () {
    var length = $(this).val().length;
    var btn = $('button[type=submit]');
    if (length > 0) {
      btn.removeClass('disabled');
    } else {
      btn.addClass('disabled');
    }
  });

  $('#add form').submit(function (e) {
    e.preventDefault();

    var field = $('#add input[name=title]');
    var button = $('#add button[type=submit]')

    var length = field.val().length;
    if (length <= 0) {
      return false;
    }

    // update timestamp (of the latest object) in the form
    var latest = $('#list .row:first .timestamp').text();
    if (latest.length <= 0) {
      latest = "0";
    }
    $('#add input[name=timestamp]').val(latest)

    $.post('/api/object', $('#add form').serialize(), objectPosted, 'json');

    // disable field and button
    field.attr('disabled', 'disabled');
    button.addClass('disabled');
  });


  // User friendly time representation
  $('.timeago').timeago();


  // comment expand/collapse
  $('#list .comment-container .banner').live('click', function () {
    var btn = $(this).find('.button');
    var comment = $(this).next();

    if (!btn.hasClass('expand')) {
      btn.addClass('expand');

      if (comment.find('fb\\:comments').length == 0) {
        // create new fb:comments
        url = $(this).find('fb\\:comments-count').attr('href');
        $('<fb:comments href="' + url + '" num_posts="2" width="580"></fb:comments>').appendTo(comment);
        FB.XFBML.parse(comment[0]);
      }

      comment.slideDown();
    } else {
      btn.removeClass('expand');

      comment.slideUp();
    }
  });


  // load more objects
  $('#next-action .more-button').click(function () {
    var btn = $('#next-action .more-button');
    var throbber = $('#next-action .more-throbber');

    btn.hide();
    throbber.show();

    $.get('/api/objects', {cursor: $('span.cursor').text()}, function (data, status) {
      if (data.result == 'success') {
        var container = $('#list');

        for (var i in data.objects) {
          var obj = data.objects[i];
          var cloned = newObjectRow(obj);
          cloned.prependTo(container).fadeIn('slow');
        }

        // update cursor
        $('span.cursor').text(data.cursor);

        // if no more objects, indicate to user
        if (data.more) {
          btn.show();
        } else {
          var symbol = $('#next-action .more-empty');
          symbol.show();
        }
      } else {
        btn.show();
      }

      throbber.hide();
    }, 'json');

  });


  // show delete on hover
  $('#list .action').live('mouseover mouseout', function (event) {
    var lbl = $(this).find('.delete.modifiable');
    if (event.type == "mouseover") {
      lbl.show();
    } else {
      lbl.hide();
    }
  });

  // delete
  $('#list .delete').live('click', function (e) {
    e.preventDefault();

    var dlg = $('div.modal');
    var parents = $(this).parentsUntil('#list');
    var row = parents.slice(-1);
    var title = row.find('.title').text();
    var url = row.find('a.timeago').attr('href');
    var btnp = dlg.find('.modal-footer .primary');
    var btns = dlg.find('.modal-footer .secondary');

    // config dialog
    dlg.find('.modal-header h3').text('確定刪除？');
    dlg.find('.modal-body p').text('確定刪除' + title + '嗎？');
    btnp.text('刪除');
    btns.text('取消');

    // handle events
    btnp.unbind();
    btnp.click(function () {
      $.post('/api' + url + '/delete', function (data, status) {
        if (data.result == 'success') {
          // fade the deleted object.
          row.fadeOut('slow');
        }
        dlg.fadeOut('fast');
      });
    });

    btns.unbind();
    btns.click(function () {
      dlg.fadeOut('fast');
    });

    // show dialog
    dlg.fadeIn('fast');
  });

});
