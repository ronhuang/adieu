// Midautumn
// Copyright 2011 Ron Huang
// See LICENSE for details.


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

    FB.Event.subscribe('auth.statusChange', function (response) {
      if (response.authResponse) {
        document.location.reload(true);
      }
    });
  };

  (function() {
    var e = document.createElement('script');
    e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
    e.async = true;
    document.getElementById('fb-root').appendChild(e);
  }());

});
