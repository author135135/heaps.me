(function ($) {
    var $window = $(window),
        $body = $('body');

    // Disable animations/transitions until the page has loaded.
    $body.addClass('is-loading');

    $window.on('load', function () {
        $body.removeClass('is-loading');
    });

    // Header.
    $('#sidebarToggle').click(function (e) {
        e.preventDefault();

        $('body').toggleClass('header-visible');
    });

    $(window).scroll(function (e) {
        // Up button show/hide
        if ($(this).scrollTop() > 700) {
            $('.up-button').fadeIn();
        } else {
            $('.up-button').fadeOut();
        }
    });

    $('.up-button').click(function (e) {
        $('body, html').animate({
            scrollTop: 0
        }, 500);
    });

    $('.subscribe-wrapper .but-remove-subscribe, .subscribe-wrapper .subscribe-remove-close').click(function(e) {
        e.preventDefault();

        $('.subscribe-wrapper').toggleClass('subscribe-wrapper-open');
    });

    // Paginate
    var page = 2,
        in_progress = false,
        has_next = false;

    $(document).on('click', '.paginate button', function (e) {
        e.preventDefault();

        $('.paginate .but-load button').hide();
        $('.paginate .but-load .load-motion').show();

        if (!in_progress) {
            in_progress = true;

            $.get(window.location.href, {page: page}, function (response) {
                if (response['celebrities']) {
                    $('.item:last').after(response['celebrities']);
                }

                if (response['paginate_has_next']) {
                    page++;
                    in_progress = false;
                    has_next = true;

                    if ($('.section-content').height() > ($(window).height() - $('footer').height())) {
                        $(window).scroll(function (e) {
                            if (!in_progress && has_next && $(window).scrollTop() >= ($('.section-content').height() - $(window).height())) {
                                in_progress = true;

                                $('.paginate .but-load .load-motion').show();

                                $.get(window.location.href, {page: page}, function (response) {
                                    if (response['celebrities']) {
                                        $('.item:last').after(response['celebrities']);
                                    }

                                    $('.paginate .but-load .load-motion').hide();

                                    page++;
                                    has_next = response['paginate_has_next'];
                                    in_progress = false;
                                }, 'json');
                            }
                        });
                    } else {
                        $('.paginate .but-load button').show();
                    }
                }

                $('.paginate .but-load .load-motion').hide();
            }, 'json');
        }
    });

    // Filter form
    $('#filter-form input').click(function (e) {
        $(this).parent().parent().toggleClass('active');
    });

    $('#filter-form').submit(function (e) {
        e.preventDefault();

        var form = $(this),
            filter = [];

        $('input[name="filter_tags"]:checked', form).each(function (element) {
            filter.push(this.value);
        });

        var query_string = set_query_string_param(window.location.search, 'filter_tags', filter.join(','));

        window.location = form.attr('action') + query_string;
    });

    $('#filter-form button[type="reset"]').click(function (e) {
        e.preventDefault();

        var query_string = set_query_string_param(window.location.search, 'filter_tags', '');
        window.location = $('#filter-form').attr('action') + query_string;
    });

    $('.filter-indicators-wrapper a').click(function (e) {
        e.preventDefault();

        var current_filters = get_query_string_param('filter_tags'),
            remove_tag = $(this).attr('data-store-id');

        current_filters = current_filters.split(',');
        current_filters.splice(current_filters.indexOf(remove_tag), 1);

        var query_string = set_query_string_param(window.location.search, 'filter_tags', current_filters.join(','));

        if (query_string) {
            window.location.search = query_string;
        } else {
            window.location = window.location.pathname;
        }
    });

    if ($('.filter-wrap-category').length) {
        var filter_slider1_settings = function () {
                var settings_1 = {
                        maxSlides: 8,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_2 = {
                        maxSlides: 7,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_3 = {
                        maxSlides: 6,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_4 = {
                        maxSlides: 5,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_5 = {
                        maxSlides: 4,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_6 = {
                        maxSlides: 3,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_7 = {
                        maxSlides: 2,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    };

                if (window.innerWidth > 1603) {
                    return settings_2;
                } else if (window.innerWidth <= 1603 && window.innerWidth > 1464) {
                    return settings_2;
                } else if (window.innerWidth <= 1464 && window.innerWidth > 1280) {
                    return settings_3;
                } else if (window.innerWidth <= 1280 && window.innerWidth > 1092) {
                    return settings_4;
                } else if (window.innerWidth <= 1092 && window.innerWidth >= 1024) {
                    return settings_5;
                } else if (window.innerWidth <= 1023 && window.innerWidth > 924) {
                    return settings_3;
                } else if (window.innerWidth <= 923 && window.innerWidth > 798) {
                    return settings_4;
                } else if (window.innerWidth <= 797 && window.innerWidth > 655) {
                    return settings_5;
                } else if (window.innerWidth <= 654 && window.innerWidth > 532) {
                    return settings_6;
                } else if (window.innerWidth <= 531) {
                    return settings_7;
                }
            },
            filter_slider1 = $('.filter-wrap-category ul').bxSlider(filter_slider1_settings());

        $(window).resize(function (e) {
            filter_slider1.reloadSlider(filter_slider1_settings());
        });
    }

    if ($('.filter-wrap-social').length) {
        var filter_slider2_settings = function () {
                var settings_1 = {
                        maxSlides: 8,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_2 = {
                        maxSlides: 7,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_3 = {
                        maxSlides: 6,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_4 = {
                        maxSlides: 5,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_5 = {
                        maxSlides: 4,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_6 = {
                        maxSlides: 3,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    },
                    settings_7 = {
                        maxSlides: 2,
                        slideWidth: 114,
                        slideMargin: 12,
                        pager: false,
                        moveSlides: 2,
                        infiniteLoop: false
                    };

                if (window.innerWidth > 1603) {
                    return settings_2;
                } else if (window.innerWidth <= 1603 && window.innerWidth > 1464) {
                    return settings_2;
                } else if (window.innerWidth <= 1464 && window.innerWidth > 1280) {
                    return settings_3;
                } else if (window.innerWidth <= 1280 && window.innerWidth > 1092) {
                    return settings_4;
                } else if (window.innerWidth <= 1092 && window.innerWidth >= 1024) {
                    return settings_5;
                } else if (window.innerWidth <= 1023 && window.innerWidth > 924) {
                    return settings_3;
                } else if (window.innerWidth <= 923 && window.innerWidth > 798) {
                    return settings_4;
                } else if (window.innerWidth <= 797 && window.innerWidth > 655) {
                    return settings_5;
                } else if (window.innerWidth <= 654 && window.innerWidth > 532) {
                    return settings_6;
                } else if (window.innerWidth <= 531) {
                    return settings_7;
                }
            },
            filter_slider2 = $('.filter-wrap-social ul').bxSlider(filter_slider2_settings());

        $(window).resize(function (e) {
            filter_slider2.reloadSlider(filter_slider2_settings());
        });
    }

    // Filter toggle class and Fix for slider
    $('#header .but-filter').click(function (e) {
        var button = $(this);

        if (!button.hasClass('active')) {
            $('body').animate({
                scrollTop: 0
            }, 0, function () {
                button.toggleClass('active');
                $('#filter-form').toggleClass('show');
            }).stop();
        } else if (button.hasClass('active') && button.offset().top > 400) {
            $('body').animate({
                scrollTop: 0
            }, 0).stop();
        } else {
            button.toggleClass('active');
            $('#filter-form').toggleClass('show');
        }
    });

    // Celebrity social links
    $(document).on('click', '.all', function (e) {
        e.preventDefault();

        var elem = $(this),
            wrapper = elem.parents('.item'),
            elem_index = $('.item').index(wrapper);

        $('.item:not(:eq(' + (elem_index) + ')) .open-social').removeClass('open-social');
        $('.item').attr('style', '');

        elem.parent().toggleClass('open-social');

        if (elem.parent().hasClass('open-social')) {
            if ($window.innerWidth() >= 992) {
                $('.item:eq(' + ((parseInt(elem_index / 3) + 1) * 3) + ')').css('clear', 'both');
            } else if ($window.innerWidth() < 992 && $window.innerWidth() >= 768) {
                $('.item:eq(' + ((parseInt(elem_index / 2) + 1) * 2) + ')').css('clear', 'both');
            }
        }
    });

    // Login and register forms
    $('#registration').on('show.bs.modal', function (e) {
        $('#login').modal('hide');
    });

    $('#login').on('show.bs.modal', function (e) {
        $('#registration').modal('hide');
    });

    $('#login form, #registration form').submit(function (e) {
        e.preventDefault();

        var form = $(this),
            emailPat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            errors = 0;

        $('.error-wrap', form).removeClass('error-wrap');

        if (!$('input[name="email"]', form).val() || !emailPat.test($('input[name="email"]', form).val())) {
            $('input[name="email"]', form).parent().addClass('error-wrap');
            errors = 1;
        }

        if (!$.trim($('input[name="password"]', form).val())) {
            $('input[name="password"]', form).parent().addClass('error-wrap');
            errors = 1;
        }

        if ($('input[name="password_repeat"]', form).length && $('input[name="password_repeat"]', form).val() != $('input[name="password"]', form).val()) {
            $('input[name="password_repeat"]', form).parent().addClass('error-wrap');
            errors = 1;
        }

        if (!errors) {
            $.post(form.attr('action'), form.serialize(), function (response) {
                if (response['authenticated']) {
                    var redirect_url = get_query_string_param('next');

                    if (!redirect_url) {
                        redirect_url = response['redirect_to'];
                    }

                    window.location = redirect_url;
                } else {
                    $.each(response['errors'], function (k, v) {
                        if (k == 'all') {
                            $('input[name="email"]', form).parent().addClass('error-wrap');
                        } else {
                            $('input[name="' + k + '"]', form).parent().addClass('error-wrap');
                        }
                    });
                }
            });
        }
    });

    // Toggle celebrity description
    if ($('.full-description').length && ($('.full-description *').height() > parseFloat($('.full-description').css('maxHeight')))) {
        $('.full-description').after('<a href="#" class="load-full-description">Полное описание</a>');
    }

    // Social posts block loader
    var social_posts_in_progress = false,
        social_network_block_load = function() {
        if (!$('.content-news.active .head-soc-news').length) {
            var request_data = {},
                social_network = $('.social-post-znam-page .active').attr('class').replace(/(?:^|\s)active(?!\S)/g , '');

            request_data['social_network'] = social_network;
            request_data['block_has_content'] = $('.content-news.' + social_network + ' .head-soc-news').length;

            $.get(window.location.href + 'social-posts-loader/', request_data, function(response){
                if ($('.content-news.' + social_network + ' > .load-news').length) {
                    $('.content-news.' + social_network + ' > .load-news').remove();
                }

                if (response['header']) {
                    $('.content-news.' + social_network).append(response['header']);
                }

                var content = response['content'];

                content = Autolinker.link(content);
                content = minEmoji(content);

                $('.content-news.' + social_network).append(content);

                if (response['has_next']) {
                    var button_html = '<div class="load-more-news load-motion clearfix"><button value="' + response['next_page_id'] + '">Загрузить еще</button></div>'
                    $('.content-news.' + social_network).append(button_html);
                }
            }, 'json');
        }
    };

    // Social posts paginate handler
    $(document).on('click', '.content-news.active .load-more-news button', function(e) {
        e.preventDefault();

        var request_data = {},
            social_network = $('.social-post-znam-page .active').attr('class').replace(/(?:^|\s)active(?!\S)/g , ''),
            page = $(this).attr('value');

        $('.content-news.' + social_network + ' .load-more-news button').remove();

        request_data['social_network'] = social_network;
        request_data['block_has_content'] = 1;
        request_data['page'] = page;

        $.get(window.location.href + 'social-posts-loader/', request_data, function(response){
            $('.content-news.' + social_network + ' .load-more-news').remove();

            var content = response['content'];

            content = Autolinker.link(content);
            content = minEmoji(content);

            $('.content-news.' + social_network).append(content);

            if (response['has_next']) {
                $('.content-news.' + social_network).attr('data-has-next', true);
                $('.content-news.' + social_network).attr('data-next-page-id', response['next_page_id']);
            }
        }, 'json');
    });

    if ($('.social-post-znam-page').length) {
        $(window).scroll(function (e) {
            var request_data = {},
                social_network = $('.social-post-znam-page .active').attr('class').replace(/(?:^|\s)active(?!\S)/g , ''),
                social_block = $('.content-news.' + social_network);

            if (!social_block[0].hasAttribute('data-has-next')) {
                return false;
            }

            if (social_block.attr('data-has-next') != 'true') {
                return false;
            }

            if (social_posts_in_progress) {
                return false;
            }

            if ($(window).scrollTop() >= ($('.wrapper-post-soc-news', social_block).eq($('.wrapper-post-soc-news', social_block).length - 2).offset().top - $(window).height())) {
                social_posts_in_progress = true;

                social_block.append('<div class="load-more-news load-motion clearfix"></div>');

                request_data['social_network'] = social_network;
                request_data['block_has_content'] = 1;
                request_data['page'] = social_block.attr('data-next-page-id');

                $.get(window.location.href + 'social-posts-loader/', request_data, function(response){
                    $('.load-more-news', social_block).remove();

                    var content = response['content'];

                    content = Autolinker.link(content);
                    content = minEmoji(content);

                    social_block.append(content);

                    if (response['has_next']) {
                        social_block.attr('data-has-next', true);
                        social_block.attr('data-next-page-id', response['next_page_id']);
                    } else {
                        social_block.attr('data-has-next', false);
                        social_block.attr('data-next-page-id', '');
                    }

                    social_posts_in_progress = false;
                }, 'json');
            }
        });
    }

    // Social tabs
    $(document).on('click', '.social-post-znam-page li:not(.all) a', function(e) {
        e.preventDefault();

        var wrapper_width = $('.social-post-znam-page').width(),
            social_tabs_count = $('.social-post-znam-page li').length,
            social_tab_width = $('.social-post-znam-page li').outerWidth(true),
            visible_tabs = Math.floor(wrapper_width / social_tab_width) - 1,
            list_item = $(this).parent();

        if (list_item.hasClass('active')) {
            return false;
        }

        if (list_item.index() > visible_tabs) {
            $('.social-post-znam-page').removeClass('all-social-open').prepend(list_item);
            social_tabs_visualization();
        }

        $('.social-post-znam-page li').removeClass('active');
        $('.content-news').removeClass('active');

        $('.content-news.' + list_item.attr('class')).addClass('active');
        list_item.addClass('active');

        social_network_block_load();
    });

    $(document).on('click', '.social-post-znam-page .all a', function(e) {
        e.preventDefault();

        var wrapper = $('.social-post-znam-page');

        if (wrapper.hasClass('all-social-open')) {
            $('+ li', $(this).parent()).hide();
        } else {
            $('+ li', $(this).parent()).show();
        }

        wrapper.toggleClass('all-social-open');
    });

    if ($('.social-post-znam-page').length) {
        social_tabs_visualization();

        if ($('.social-post-znam-page .facebook').length && $('.social-post-znam-page .facebook').index() != 0) {
            $('.social-post-znam-page .facebook a').click();
        } else {
            social_network_block_load();
        }
    }

    $(document).on('click', '.load-full-description', function(e){
        e.preventDefault();

        $(this).prev().toggleClass('full-description-open');
        $(this).text($(this).text() == 'Полное описание' ? 'Скрыть описание' : 'Полное описание');
    });

    // Social posts content

    // Facebook block
    $(document).on('click', '.play-button', function(e) {
        var media_box = $(this).parents('.media-box');

        $(this).after('<iframe src="' + $('img', media_box).attr('data-url') + '"></iframe>');

        $('img', media_box).remove();
        $(this).remove();

        media_box.next().addClass('left');
    });

    $(document).on('click', '.media-description .title a', function(e) {
        var data_url = $(this).attr('data-url'),
            media_box = $(this).parents('.media-description').prev();

        if (data_url) {
            e.preventDefault();

            $('.prev-video', media_box).append('<iframe src="' + data_url + '"></iframe>');
            $(this).removeAttr('data-url');

            media_box.next().addClass('left');
        }
    });

    // End Social posts content

    // Forgotten password form
    $('#forgotten-password').on('show.bs.modal', function (e) {
        $('#login').modal('hide');
    });

    $('#forgotten-password form').submit(function (e) {
        e.preventDefault();

        var form = $(this),
            emailPat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            errors = 0,
            email = $('input[name="email"]', form).val();

        $('.error-wrap', form).removeClass('error-wrap');

        if (!email || !emailPat.test(email)) {
            $('input[name="email"]', form).parent().addClass('error-wrap');
            errors = 1;
        }

        if (!errors) {
            $.post(form.attr('action'), form.serialize(), function (response) {
                if (response['success']) {
                    $('#forgotten-password form').trigger('reset');
                    $('#forgotten-password').modal('hide');
                    $('#message-modal .go-mail-info span').text(response['message']);
                    $('#message-modal .go-mail-info button').attr('data-url', '//' + email.split('@')[1]);
                    $('#message-modal').modal('show');
                } else {
                    $.each(response['errors'], function (k, v) {
                        $('input[name="' + k + '"]', form).parent().addClass('error-wrap');
                    });
                }
            }, 'json');
        }
    });

    // Email verification form
    $('#email-verification form').submit(function (e) {
        var form = $(this),
            emailPat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            errors = 0;

        if (!$('input[name="email"]', form).val() || !emailPat.test($('input[name="email"]', form).val())) {
            $('input[name="email"]', form).addClass('input-error');
            $('input[name="email"]', form).prev().addClass('ic-log-error');
            errors = 1;
        }

        if (errors) {
            e.preventDefault();
        }
    });

    // Email verification send
    $('#message-modal button').click(function(e) {
        $('#message-modal').modal('hide');

        window.open($(this).attr('data-url'), '_blank');
    });

    // Celebrity add form
    var default_image = $('#add-celebrity .photo-box img').attr('src');

    $('.upload-photo-box button').click(function (e) {
        $('.upload-photo-box input[type="file"]').click();
    });

    $('#add-celebrity .upload-photo-box input[type="file"]').change(function (e) {
        var input = $(this)[0];
        if (input.files && input.files[0]) {
            if (input.files[0].type.match('image.*')) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    $('.upload-photo-box .photo-box img').attr('src', e.target.result);
                }
                reader.readAsDataURL(input.files[0]);
            } else console.log('is not image mime type');
        } else console.log('not isset files data or files API not supported');
    });

    $('#add-celebrity').submit(function (e) {
        e.preventDefault();

        var form = $(this);

        $('.error-wrap', form).removeClass('error-wrap');
        $('.error-text', form).removeClass('error-text');

        var options = {
            beforeSubmit: function () {
                if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
                    alert("Please upgrade your browser, because your current browser lacks some new features we need!");
                }
            },
            success: function (response) {
                if (response['errors']) {
                    $.each(response['errors'], function (k, v) {
                        $('[name="' + k + '"]', form).parent().addClass('error-wrap');
                        //$('[name="' + k + '"]', form).prev().children('span').addClass('error-text');
                        //$('[name="' + k + '"]', form).after('<p class="error">' + k + ': ' + v + '</p>');
                    });
                }

                if (response['success']) {
                    var message_wrapper = $('.info-message'),
                        default_message = message_wrapper.text();

                    message_wrapper.text(response['message']);

                    // Reset form after success submit
                    form.trigger('reset');
                    $('#add-celebrity input[name="social_network"]').not(':first').parent().remove();
                    $('#add-celebrity .photo-box img').attr('src', default_image);

                    $("html, body").stop().animate({scrollTop: 0}, '1000', 'swing', function () {
                        setTimeout(function () {
                            message_wrapper.text(default_message);
                        }, 10000);
                    });
                }
            }
        };

        form.ajaxSubmit(options);
    });

    $('#add-celebrity .more-load-link-box').click(function (e) {
        e.preventDefault();

        var field = $('#add-celebrity input[name="social_network"]').first().parent().clone();

        $('input[name="social_network"]', field).val('').removeClass('input-error');
        $('span', field).remove();

        $('#add-celebrity input[name="social_network"]:last').parent().after(field);
    });

    // Account settings
    $(document).on('change', '#settings-avatar-form .upload-photo-box input[type="file"]', function (e) {
        var input = $(this)[0];
        if (input.files && input.files[0]) {
            if (input.files[0].type.match('image.*')) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    var image = new Image();
                    image.src = e.target.result;

                    $('#settings-avatar-form #popup img').attr('src', image.src).cropbox({
                        width: 200,
                        height: 200,
                        showControls: 'always'
                    }, function () {
                        //on load
                        //console.log('Url: ' + this.result);
                    }).on('cropbox', function (e, data) {
                        $('#id_crop_attr_x').val(data.cropX);
                        $('#id_crop_attr_y').val(data.cropY);
                        $('#id_crop_attr_w').val(data.cropW);
                        $('#id_crop_attr_h').val(data.cropH);
                    });

                    $('#settings-avatar-form #popup').modal('show');
                }
                reader.readAsDataURL(input.files[0]);
            } else console.log('is not image mime type');
        } else console.log('not isset files data or files API not supported');
    });

    $('#settings-avatar-form #popup .send').click(function (e) {
        var form = $('#settings-avatar-form');

        $('#settings-avatar-form #popup').modal('hide');

        var options = {
            beforeSubmit: function () {
                if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
                    alert("Please upgrade your browser, because your current browser lacks some new features we need!");
                }
            },
            success: function (response) {
                if (response['success']) {
                    console.log(response);

                    var crop = $('#settings-avatar-form #popup img').data('cropbox');

                    $('.upload-photo-box .photo-box img').attr('src', crop.getDataURL());
                    $('.user-descrpt-sidebar img').attr('src', crop.getDataURL());

                    var message_wrapper = $('.wrap-info-message');

                    message_wrapper.html('<div class="info-message">' + response['message'] + '</div>');

                    $('.photo-box input', form).val('');

                    $("html, body").stop().animate({scrollTop: 0}, '1000', 'swing', function () {
                        setTimeout(function () {
                            message_wrapper.empty();
                        }, 5000);
                    });
                }
            }
        };

        form.ajaxSubmit(options);
    });

    $('#settings-info-form').submit(function (e) {
        e.preventDefault();

        var form = $(this);

        $('.error-wrap', form).removeClass('error-wrap');

        $.post(form.attr('action'), form.serialize(), function (response) {
            if (response['errors']) {
                $.each(response['errors'], function (k, v) {
                    $('[name="' + k + '"]', form).parents('.input-box').addClass('error-wrap');
                });
            }

            if (response['modal']) {
                $('#message-modal .go-mail-info span').text(response['message']);
                $('#message-modal .go-mail-info button').attr('data-url', response['email_url']);

                $('input[name="password"], input[name="password_repeat"]', form).val('');

                $("html, body").stop().animate({scrollTop: 0}, '1000', 'swing', function () {
                    $('#message-modal').modal('show');
                });
            }

            if (response['success']) {
                var message_wrapper = $('.wrap-info-message');

                message_wrapper.html('<div class="info-message">' + response['message'] + '</div>');

                $('input[name="password"], input[name="password_repeat"]', form).val('');

                $("html, body").stop().animate({scrollTop: 0}, '1000', 'swing', function () {
                    setTimeout(function () {
                        message_wrapper.empty();
                    }, 3000);
                });
            }
        }, 'json');
    });

    modal_handler();

    // Response design fixes
    $(window).resize(function (e) {
        if (window.innerWidth >= 1024) {
            $('body').removeClass('header-visible');
        }

        if ($('.social-post-znam-page').length) {
            social_tabs_visualization();
        }
    });

    $('#registration, #login').on('show.bs.modal', function (e) {
        if (window.innerWidth < 768) {
            $('body').removeClass('header-visible');
        }
    });

    // Helpers
    function get_query_string_param(name) {
        if (name = (new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)')).exec(location.search)) {
            return decodeURIComponent(name[1]);
        } else {
            return false;
        }
    }

    function set_query_string_param(uri, key, value) {
        var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i"),
            separator = uri.indexOf('?') !== -1 ? "&" : "?";

        if (uri.match(re)) {
            if (!value) {
                return uri.replace(re, '');
            } else {
                return uri.replace(re, '$1' + key + "=" + value + '$2');
            }
        } else {
            if (!value) {
                return uri;
            }

            return uri + separator + key + "=" + value;
        }
    }

    function modal_handler() {
        var modal = get_query_string_param('modal');

        if (modal) {
            $('#' + modal).modal();
        }
    }

    function minEmoji(content) {
        return $('<div/>').html(content).minEmojiSVG({
            svg_path: '/static/heaps_app/js/jMinEmoji/img/svg/'
        });
    }

    function social_tabs_visualization() {
        $('.social-post-znam-page li.all').remove();

        var wrapper_width = $('.social-post-znam-page').width(),
            social_tabs_count = $('.social-post-znam-page li').length,
            social_tab_width = $('.social-post-znam-page li').outerWidth(true);

        if (social_tabs_count * social_tab_width > wrapper_width) {
            var visible_tabs = Math.floor(wrapper_width / social_tab_width) - 1;

            $('.social-post-znam-page li:nth-child(' + visible_tabs + ')').after('<li class="all"><a href="#"></a></li>');

            $('.social-post-znam-page li:gt(' + visible_tabs + ')').hide();
            $('.social-post-znam-page li:lt(' + visible_tabs + ')').show();
        }
    }

})(jQuery);