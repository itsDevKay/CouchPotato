function isSafari() {
    var sfri = window.navigator.userAgent.toLowerCase().indexOf("safari") > -1;
    return sfri;
}
function isChrome() {
    var chr = window.navigator.userAgent.toLowerCase().indexOf("chrome") > -1;
    return chr;
}
function isFirefox() {
    var ffox = window.navigator.userAgent.toLowerCase().indexOf("firefox") > -1;
    return ffox;
}


// 1. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

if (!window['YT']) {var YT = {loading: 0,loaded: 0};}
if (!window['YTConfig']) {var YTConfig = {'host': 'http://www.youtube.com'};}
if (!YT.loading) {YT.loading = 1;(function(){var l = [];YT.ready = function(f) {if (YT.loaded) {f();} 
else 
{l.push(f);}};
window.onYTReady = function() {YT.loaded = 1;for (var i = 0; i < l.length; i++) {try {l[i]();} catch (e) {}}};
YT.setConfig = function(c) {for (var k in c) {if (c.hasOwnProperty(k)) {YTConfig[k] = c[k];}}};
var a = document.createElement('script');
a.type = 'text/javascript';
a.id = 'www-widgetapi-script';
a.src = 'https:' + '//s.ytimg.com/yts/jsbin/www-widgetapi-vflumC9r0/www-widgetapi.js';
a.async = true;
var b = document.getElementsByTagName('script')[0];
b.parentNode.insertBefore(a, b);})();}

// 2. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;

// 3. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    console.log('playing youtube video');
    if (playMuted) { player.mute(); }
    event.target.playVideo();
    // player.mute()
}

var done = false;
function onPlayerStateChange(event) {
  
}
function stopVideo() {
    player.stopVideo();
    $('.movie-backdrop').show();
    $('.movie-trailer').hide();
}

let playMuted = false;
function playYouTubeTrailer(videoID, height, width, muted) {
    playMuted = muted;
    player = new YT.Player('movie-trailer', {
        height: height,
        width: width,
        playerVars: {
            autoplay: 1,
            loop: 1,
            controls: 0,
            showinfo: 0,
            autohide: 1,
            modestbranding: 1,
            vq: 'hd1080',
            wmode: 'opaque',
            origin: window.location.href,
            host: `${window.location.protocol}//www.youtube.com`,
            // host: `https://www.youtube.com`,
            iv_load_policy: 3,
            widget_referrer : window.location.href,
            enablejsapi: 1
        },
        videoId: videoID,
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;
function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.ENDED) {
        setTimeout(stopVideo, 6000);
        done = true;
    } else if (event.data == YT.PlayerState.PLAYING) {
        $('.movie-backdrop').hide();
        document.querySelector('.movie-trailer').style.height = window.innerHeight + 'px';
        document.querySelector('.movie-trailer').style.width = window.innerWidth + 'px';
    }
}