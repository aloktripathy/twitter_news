$(document).ready(function() {
    // This command is used to initialize some elements and make them work properly
    $.material.init();
});

var app = angular.module('twitterNews', ['ngRoute']);


// SERVICE
app.service('globals', function(){
    this.category_url = 'http://news.aloktripathy.com/api/categories';
    this.tweets_url = 'http://news.aloktripathy.com/api/tweets';
    this.shuffle = function(o){
        for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
        return o;
    }
});


// FILTER
app.filter('ngRepeatFinish', function($timeout){
    return function(data){
        var me = this;
        var flagProperty = '__finishedRendering__';
        if(!data[flagProperty]){
            Object.defineProperty(
                data, 
                flagProperty, 
                {enumerable:false, configurable:true, writable: false, value:{}});
            $timeout(function(){
                    $.material.init();
                    delete data[flagProperty];
                },0,false);                
        }
        return data;
    };
});


// CONTROLLER
app.controller("mainCtrl", ["$scope", "$http", "globals", function($scope, $http, globals){
    $scope.categories = {};
    $scope.currentCategoryIndex = 1;
    $scope.current_page = 1;
    $scope.order_tweets_by = 'score';
    $scope.loading = false;
    // $scope.channel_flags = {newsycombinator: true, TechCrunch: true, Gizmodo: true, Recode: true, mashabletech: true};
    
    $scope.loadCategory = function(index){
        $scope.currentCategoryIndex = index;
        // $scope.categories[$scope.currentCategoryIndex].channels.forEach(function(v){$scope.channel_flags[v.screen_name] = true;});
        console.log($scope.channel_flags);
        $scope.fetchTweets(true);
    };
    
    // fetch tweets
    $scope.fetchTweets = function(reset_pagination){
        if($scope.loading && !reset_pagination)
            return false;
        var container_element = $('.stream .inner');
        if(reset_pagination){
            $scope.current_page = 1;
            container_element.html('');
        }
        // order_by=score&category=Business&start_from=1446287446&until=1446299777
        var params = {order_by: $scope.order_tweets_by, start_from: parseInt($scope.timeline.start_from / 1000),
                     until: parseInt($scope.timeline.until / 1000), page: $scope.current_page};
        if($scope.currentCategoryIndex !== 0)
            params.category = $scope.categories[$scope.currentCategoryIndex].text;
        
        $scope.loading = true;
        $http({url: globals.tweets_url, params: params, method: "GET"}).
        then(function(response){    // success
            $scope.loading = false;
            var tweets = response.data;
            var target = $('')
            var template = '<blockquote class="twitter-tweet" lang="en"><a href="__link__"></a></blockquote>';
            
            tweets.forEach(function(v){
                var txt = template.replace('__link__', v.tweet_link);
                container_element.append(txt);
            });
            // load async tweets
            twttr.widgets.load();
            
            $scope.current_page++;
        }, function(response){      // failure
            $scope.loading = false;
        });
    };
    
    // lazyload
    $(window).scroll(function(e){
        var gap = Math.abs($('.stream').height() - window.scrollY);
        if(gap < 1000){
            $scope.fetchTweets();
        }
    });
    
    $http.get(globals.category_url).
    then(function(response){
        $scope.categories = response.data;
        var all = {'text': 'All', channels: globals.shuffle($scope.categories.map(function(v){return v['channels'];}).reduce(function(a, b){return a.concat(b);}))};
        // add `all` category
        $scope.categories.unshift(all);
        // now start fetching tweets
        $scope.loadCategory($scope.currentCategoryIndex);
        $scope.fetchTweets(true);
        
    }, function(response){
        console.log(response);
    });
    
    $scope.timestamp = function(date){
        // if no arguments passed, then current time
        if(arguments.length === 0)
            return Math.round(Date.now() / 3600000) * 3600000;
        // if timestamp round off to hours
        if(typeof date == "number")
            return Math.round(date / 3600000) * 3600000;
        // if string
        else if(typeof date == "string")
            return new Date(date).getTime();
        
    };
    
    $scope.timeline = {start_from: $scope.timestamp() - 3600 * 23 * 1000, until: $scope.timestamp() + 3600 * 1000};
    
    // initialize timeline slider
    var slider = document.getElementById('time-slider');
    noUiSlider.create(slider, {
        start: [$scope.timeline.start_from, $scope.timeline.until],
        direction: 'rtl',
        connect: true,
        orientation: 'vertical',
        step: 3600 * 1000,

        range: {
            'min': $scope.timeline.start_from,
            'max': $scope.timeline.until
        }
    });
    
    $scope.updateTimeline = function(t){
        $scope.timeline.start_from = parseInt(t[0]);
        $scope.timeline.until = parseInt(t[1]);
        $('.start-time.time').html($scope.pretty_date($scope.timeline.start_from));
        $('.end-time.time').html($scope.pretty_date($scope.timeline.until));
        
        if($scope.current_page != 1)
            $scope.fetchTweets(true);
    };
    
    $scope.pretty_date = function(t){
        var now = new Date();
        var t = new Date(t);
        var day = t.getDate() == now.getDate() ? 'Today' : 'Yesterday';
        var am_pm = t.getHours() >= 12 ? 'PM' : 'AM';
        var hours = t.getHours() % 12 ? t.getHours() % 12 : 12;
        return hours + ' ' + am_pm + ' ' + day;
    };
    
    slider.noUiSlider.on('update', function( values, handle ) {
        $scope.updateTimeline(values);
        /*
        $scope.$apply(function(){
            $scope.timeline.start_from = parseInt(values[0]);
            $scope.timeline.start_from = parseInt(values[1]); 
        });
        */
    });
    window.scope = $scope;
}]);
