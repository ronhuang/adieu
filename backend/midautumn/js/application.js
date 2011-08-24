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
      appId : '271148119565356',
      status : true,
      cookie : true,
      xfbml : true,
      oauth : true
    });

    FB.getLoginStatus(loginStatusChanged);
  };

  (function() {
    var e = document.createElement('script');
    e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
    e.async = true;
    document.getElementById('fb-root').appendChild(e);
  }());


  // update info after login status changed
  var loginStatusChanged = function (response) {
    updateUi(response);
    updateUserInfo(response);
    updateObjects(response);

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

  var updateUserInfo = function (response) {
    if (response.authResponse) {
      // Logged in
      FB.api('/me', function (user) {
        if (user) {
          $('a.menu span').text(user.name);
          $('a.menu img').attr('src', 'http://graph.facebook.com/' + user.id + '/picture?type=square');
          $('a.profile').attr('href', 'profile/' + user.id);
          $('input[name=owner]').val(user.id);
        }
      });
    } else {
      // Not logged in
      $('a.menu span').text('');
      $('a.menu img').attr('src', 'img/blank.jpg');
      $('a.profile').attr('href', '#');
      $('input[name=owner]').val('');
    }
  };

  function updateUi(response) {
    var privateItems = ['#navbar', '#add', '#list'];
    var publicItems = ['#header', '#about', '#login'];

    if (response.authResponse) {
      // Logged in
      $.each(privateItems, function (index, value) {
        $(value).show();
      });
      $.each(publicItems, function (index, value) {
        $(value).hide();
      });
    } else {
      // Not logged in
      $.each(privateItems, function (index, value) {
        $(value).hide();
      });
      $.each(publicItems, function (index, value) {
        $(value).show();
      });
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
    FB.logout(loginStatusChanged);
  });


  // prevent invalid input...
  $('input[name=title]').keyup(function () {
    var length = $(this).val().length;
    var btn = $('button[type=submit]');
    if (length > 0) {
      btn.removeClass('disabled');
    } else {
      btn.addClass('disabled');
    }
  });

  $('#add form').submit(function () {
    var length = $('input[name=title]').val().length;
    if (length <= 0) {
      return false;
    }
  });

});
