(function ($) {
    $(document).ready(function () {
        $(document).on('click', '.social-post a', function (e) {
            var link = $(this),
                item = link.parents('.item'),
                data = {};

            data['social_network_name'] = link.parent().attr('class');

            var celebrity_url = $('.name-post-container', item).attr('href');

            data['slug'] = celebrity_url.replace(/^\/(.*)\/$/, '$1').split('/')[1];

            send_data('/heaps-stat/social-link-clicks/', data);
        });

        $(document).on('click', '.but-go-sosial-web, .com-soon', function(e) {
            var data = {};

            data['social_network_name'] = $('.social-post-znam-page .active').attr('class').replace(/(?:^|\s)active(?!\S)/g , '');
            data['slug'] = window.location.pathname.replace(/^\/(.*)\/$/, '$1').split('/')[1];

            send_data('/heaps-stat/social-link-clicks/', data);
        });

        function send_data(url, data) {
            data['csrfmiddlewaretoken'] = getCookie('csrftoken');

            $.post(url, data, function (e) {}, 'json');
        }

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = $.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    });
}(jQuery));