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
      channelUrl: 'http://midautumn.ronhuang.org/channel',
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

  // object posted
  var objectPosted = function (data, textStatus) {
    var field = $('#add input[name=title]');
    var button = $('#add button[type=submit]')

    if (data.result == 'success') {
      var latest = $('#list .row:first');
      var latest_title = latest.find('.title').text()

      for (var i in data.objects) {
        var obj = data.objects[i];

        if (latest_title == obj.title) {
          // should only happen at the very last obj,
          // due to the poor resolution of timestamp
          continue;
        }

        var cloned = $('#list-template .row').clone();

        var fb_like = '<fb:like href="' + obj.absolute_url + '" send="false" ' +
          'layout="button_count" width="200" show_faces="false" ' +
          'action="like"></fb:like>';
        $(fb_like).appendTo(cloned.find('.share'));

        var fb_comment_count = '<fb:comments-count href="' + obj.absolute_url + '">0</fb:comments>';
        $(fb_comment_count).appendTo(cloned.find('.comment-container .count span'));

        cloned.find('.title').text(obj.title);
        cloned.find('.timeago').attr('href', obj.relative_url).attr('title', obj.pubtime_iso8601).text(obj.pubtime_local).timeago();
        cloned.find('img:first').attr('src', obj.owner_picture);
        cloned.find('.timestamp').text(obj.timestamp);

        cloned.insertBefore(latest)
        FB.XFBML.parse(cloned[0]);
      }

      // show achievement
    } else {
      // show error message
    }

    field.removeAttr('disabled');
    button.removeClass('disabled');
    field.val('');
  };

  // The url that was liked is returned
  var edgeCreated = function (url) {
  };

  // The url that was unliked is returned
  var edgeRemoved = function (url) {
  };

  // {href: '', commentID: ''}
  var commentCreated = function (response) {
  };

  // {href: '', commentID: ''}
  var commentRemoved = function (response) {
  };


  // update info after login status changed
  var loginStatusChanged = function (response) {
    // subscribe here to avoid invoking loginStatusChanged twice.
    FB.Event.subscribe('auth.statusChange', loginStatusChanged);
  };

  var updateObjects = function  (response) {
    if (response.authResponse) {
      $.ajax({
        url: 'api/objects',
        dataType: 'json',
        success: function (data, status) {
          if (data.result == 'success') {
            var container = $('#list');
            for (var i in data.objects) {
              var obj = data.objects[i];
              var relative_url = '/object/' + obj.key;
              var absolute_url = document.location.protocol + '//' + document.location.host + relative_url;

              var template = container.find('div:first').clone();

              var fb_like = '<fb:like href="' + absolute_url + '" send="false" ' +
                'layout="button_count" width="200" show_faces="false" ' +
                'action="like"></fb:like>';
              $(fb_like).appendTo(template.find('.share'));

              var fb_comment = '<fb:comments href="' + absolute_url + '" num_posts="2" width="400"></fb:comments>';
              $(fb_comment).appendTo(template.find('.comment'));

              template.find('.title').text(obj.title);
              template.find('.timeago').attr('href', relative_url).attr('title', obj.pubtime).timeago();
              template.find('img:first').attr('src', 'http://graph.facebook.com/' + obj.owner + '/picture?type=square');

              template.show();
              container.append(template);
            }
            FB.XFBML.parse(container[0]);
          }
        },
        error: function (xhr, status) {
        },
      });
    } else {
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
    var latest = $('#list .row:first .timestamp').text()
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
        $('<fb:comments href="' + url + '" num_posts="2" width="400"></fb:comments>').appendTo(comment);
        FB.XFBML.parse(comment[0]);
      }

      comment.slideDown();
    } else {
      btn.removeClass('expand');

      comment.slideUp();
    }
  });

});
