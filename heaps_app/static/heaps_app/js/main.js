(function ($) {
    var $window = $(window),
        $body = $('body');

    // Disable animations/transitions until the page has loaded.
    $body.addClass('is-loading');

    $window.on('load', function () {
        $body.removeClass('is-loading');
    });

    // Toggle.
    $('<div id="headerToggle"><a href="#header" class="toggle"></a></div>').appendTo($body);

    // Header.
    $('#header').panel({
        delay: 0,
        hideOnClick: true,
        hideOnSwipe: true,
        resetScroll: true,
        resetForms: true,
        side: 'left',
        target: $body,
        visibleClass: 'header-visible'
    });

    // Login/register buttons handler
    $('.but-log-reg-sdb button').click(function (e) {
        $('' + $(this).attr('data-target') + '').modal();
    });

    // Paginate
    var page = 2;

    $(document).on('click', '.paginate button', function (e) {
        e.preventDefault();

        $.get(window.location.href, {page: page}, function (response) {
            if (response['celebrities']) {
                $('.paginate').before(response['celebrities']);
            }

            if (response['paginate_has_next']) {
                page++;
            } else {
                $('.paginate').remove();
            }
        });
    });

    // Celebrity social links
    $('.all').click(function (e) {
        e.preventDefault();

        var elem = $(this),
            wrapper = elem.parents('.item'),
            elem_index = wrapper.index();

        $('.item:not(:eq(' + elem_index + ')) .open-social').removeClass('open-social');
        $('.item').attr('style', '');

        elem.parent().toggleClass('open-social');

        if ($window.innerWidth() >= 992) {
            $('.item:nth-child(' + ((parseInt(elem_index / 3) + 1) * 3 + 1) + ')').css('clear', 'both');
        } else if ($window.innerWidth() < 992 && $window.innerWidth() > 769) {
            $('.item:nth-child(' + ((parseInt(elem_index / 2) + 1) * 2 + 1) + ')').css('clear', 'both');
        }
    });

    // Login and register forms
    $('#login form, #registration form').submit(function (e) {
        e.preventDefault();

        var form = $(this),
            emailPat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            errors = 0;

        $('.input-error', form).removeClass('input-error');
        $('.ic-log-error', form).removeClass('ic-log-error');
        $('.ic-parol-error', form).removeClass('ic-parol-error');

        if (!$('input[name="email"]', form).val() || !emailPat.test($('input[name="email"]', form).val())) {
            $('input[name="email"]', form).addClass('input-error');
            $('input[name="email"]', form).prev().addClass('ic-log-error');
            errors = 1;
        }

        if (!$.trim($('input[name="password"]', form).val())) {
            $('input[name="password"]', form).addClass('input-error');
            $('input[name="password"]', form).prev().addClass('ic-parol-error');
            errors = 1;
        }

        if ($('input[name="password_repeat"]', form).length && $('input[name="password_repeat"]', form).val() != $('input[name="password"]', form).val()) {
            $('input[name="password_repeat"]', form).addClass('input-error');
            $('input[name="password_repeat"]', form).prev().addClass('ic-parol-error');
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
                            $('input[name="email"]', form).prev().addClass('ic-log-error');
                            $('input[name="password"]', form).prev().addClass('ic-parol-error');
                        } else {
                            $('input[name="' + k + '"]', form).addClass('input-error');
                            $('input[name="' + k + '"]', form).prev().addClass(k == 'email' ? 'ic-log-error' : 'ic-parol-error');
                        }
                    });
                }
            });
        }
    });

    $('.link-forgot-log').click(function (e) {
        e.preventDefault();

        $('#login').modal('hide');
    });

    // Forgotten password form
    $('#forgotten-password form').submit(function (e) {
        e.preventDefault();

        var form = $(this),
            emailPat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            errors = 0;

        if (!$('input[name="email"]', form).val() || !emailPat.test($('input[name="email"]', form).val())) {
            $('input[name="email"]', form).addClass('input-error');
            $('input[name="email"]', form).prev().addClass('ic-log-error');
            errors = 1;
        }

        if (!errors) {
            $.post(form.attr('action'), form.serialize(), function (response) {
                if (response['success']) {
                    $('#forgotten-password form').trigger('reset');
                    $('#forgotten-password').modal('hide');
                    $('#message-modal .head-form span').text(response['message']);
                    $('#message-modal').modal('show');
                } else {
                    $.each(response['errors'], function (k, v) {
                        $('input[name="' + k + '"]', form).addClass('input-error');
                        $('input[name="' + k + '"]', form).prev().addClass(k == 'email' ? 'ic-log-error' : 'ic-parol-error');
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
        } else console.log('not isset files data or files API not supordet');
    });

    $('#add-celebrity').submit(function (e) {
        e.preventDefault();

        var form = $(this);

        $('.input-error', form).removeClass('input-error');
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
                        $('[name="' + k + '"]', form).addClass('input-error');
                        $('[name="' + k + '"]', form).prev().children('span').addClass('error-text');
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

                    $("html, body").stop().animate({scrollTop:0}, '1000', 'swing', function(){
                        setTimeout(function(){
                            message_wrapper.text(default_message);
                        }, 3000);
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
    var jcrop_api;

    $('#account-settings #popup').on('hide.bs.modal', function(e){
        jcrop_api.destroy();
    });

    $('#account-settings .upload-photo-box input[type="file"]').change(function (e) {
        var input = $(this)[0];
        if (input.files && input.files[0]) {
            if (input.files[0].type.match('image.*')) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    $('#account-settings #popup img').attr('src', e.target.result);

                    $('#account-settings #popup').modal('show');

                    var image = new Image();
                    image.src = e.target.result;

                    jcrop_api = $.Jcrop('#account-settings #popup img', {
                        aspectRatio: 1,
                        setSelect: [
                            image.width / 2 - 100,
                            image.height / 2 - 100,
                            image.width / 2 + 100,
                            image.height / 2 + 100
                        ],
                        onChange: jcrop_set_data,
                        onSelect: jcrop_set_data
                    });
                }
                reader.readAsDataURL(input.files[0]);
            } else console.log('is not image mime type');
        } else console.log('not isset files data or files API not supported');
    });

    $('#account-settings #popup .send').click(function(e){
        $('#account-settings #popup').modal('hide');
        var x1 = $('#id_crop_attr_x').val();
        var y1 = $('#id_crop_attr_y').val();
        var width = $('#id_crop_attr_w').val();
        var height = $('#id_crop_attr_h').val();
        var canvas = $("#canvas")[0];
        var context = canvas.getContext('2d');
        var img = new Image();
        img.onload = function () {
            canvas.height = height;
            canvas.width = width;
            context.drawImage(img, x1, y1, width, height, 0, 0, width, height);
            var avatar = canvas.toDataURL();

            $('.upload-photo-box .photo-box img').attr('src', avatar);
            $('.user-descrpt-sidebar img').attr('src', avatar);
        };
        img.src = $('#account-settings #popup img').attr("src");
    });

    $('#account-settings').submit(function (e) {
        e.preventDefault();

        var form = $(this);

        $('.has-error', form).removeClass('has-error');

        var options = {
            beforeSubmit: function () {
                if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
                    alert("Please upgrade your browser, because your current browser lacks some new features we need!");
                }
            },
            success: function (response) {
                if (response['errors']) {
                    $.each(response['errors'], function (k, v) {
                        $('[name="' + k + '"]', form).addClass('input-error');
                        $('[name="' + k + '"]', form).prev().children('span').addClass('error-text');
                    });
                }

                if (response['success']) {
                    var message_wrapper = $('.wrap-info-message');

                    message_wrapper.html('<div class="info-message">' + response['message'] + '</div>');

                    $('input[name="password"], input[name="password_repeat"]', form).val('');

                    $("html, body").stop().animate({scrollTop:0}, '1000', 'swing', function(){
                        setTimeout(function(){
                            message_wrapper.empty();
                        }, 3000);
                    });
                }
            }
        };

        form.ajaxSubmit(options);
    });

    modal_handler();

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
            return uri + separator + key + "=" + value;
        }
    }

    function modal_handler() {
        var modal = get_query_string_param('modal');

        if (modal) {
            $('#' + modal).modal();
        }
    }

    function jcrop_set_data(c) {
        $('#id_crop_attr_x').val(c.x);
        $('#id_crop_attr_y').val(c.y);
        $('#id_crop_attr_w').val(c.w);
        $('#id_crop_attr_h').val(c.h);
    }

})(jQuery);