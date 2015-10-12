(function ($) {
    $(document).ready(function () {
        var page = 2;

        $(document).on('click', '.paginate a', function (e) {
            e.preventDefault();
            $.get(window.location.href, {page: page}, function (response) {
                if (response['celebrities']) {
                    $('#main-container .items-container').append(response['celebrities'])
                }

                if (response['paginate_has_next']) {
                    page++;
                } else {
                    $('#main-container .paginate').remove();
                }
            });
        });

        $(document).on('click', 'form.filter-tags', function (e) {
            e.stopPropagation();
        });

        $('form.filter-tags').submit(function (e) {
            e.preventDefault();

            var form = $(this),
                filter = [],
                filters = '';

            $('input[name="filter_tags"]:checked', form).each(function (element) {
                filter.push(this.value);
            });

            var query_string = set_query_string_param(window.location.search, 'filter_tags', filter.join(','));

            window.location = form.attr('action') + query_string;
        });

        $('.current-tags a').click(function (e) {
            e.preventDefault();

            var current_filters = get_query_string_param('filter_tags'),
                filters = '',
                remove_tags = $(this).attr('data-store-id');

            if (remove_tags != 'all') {
                current_filters = current_filters.split(',');
                current_filters.splice(current_filters.indexOf(remove_tags), 1);
            } else {
                current_filters = [];
            }

            var query_string = set_query_string_param(window.location.search, 'filter_tags', current_filters.join(','));

            if (query_string) {
                window.location.search = query_string;
            } else {
                window.location = window.location.pathname;
            }
        });

        // Modal handler
        modal_handler();

        $('#add-celebrity').submit(function (e) {
            e.preventDefault();

            var form = $(this);

            $('.has-error', form).removeClass('has-error');
            $('.error', form).remove();
            $('.messages *', form).remove();

            var options = {
                beforeSubmit: function() {
                    if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
                        alert("Please upgrade your browser, because your current browser lacks some new features we need!");
                    }
                },
                success: function(response) {
                    if (response['errors']) {
                        $.each(response['errors'], function(k, v){
                            $('[name="' + k + '"]', form).parent().addClass('has-error');
                            $('[name="' + k + '"]', form).after('<p class="error">' + k + ': '+ v + '</p>');
                        });
                    }

                    if (response['success']) {
                        var message_html = '<div class="alert alert-info alert-dismissible" role="alert">';
                            message_html += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                            message_html += '<span aria-hidden="true">&times;</span></button>';
                            message_html += response['message'] + '</div>';

                        $('.messages', form).append(message_html);

                        // Reset form after success submit
                        form.trigger('reset');
                        $('.social-network input:not(:first-child)', form).remove();
                        $('#add-celebrity div.thumbnail img').attr('src', '');
                        $('#add-celebrity div.thumbnail span').show();
                    }
                }
            };

            form.ajaxSubmit(options);
        });

        $('#add-celebrity div.thumbnail').click(function (e) {
            $('#add-celebrity input[type="file"]').click();
        });

        $('#add-celebrity input[type="file"]').change(function (e) {
            var input = $(this)[0];
            if (input.files && input.files[0]) {
                if (input.files[0].type.match('image.*')) {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        $('#add-celebrity div.thumbnail img').attr('src', e.target.result);
                        $('#add-celebrity div.thumbnail span').hide();
                    }
                    reader.readAsDataURL(input.files[0]);
                } else console.log('is not image mime type');
            } else console.log('not isset files data or files API not supordet');
        });

        $('#add-celebrity .add-field').click(function (e) {
            e.preventDefault();

            var field = $('#add-celebrity input[name="social_network"]').first(),
                wrapper = $('#add-celebrity .social-network');

            wrapper.append(field.clone().val(''));
        });

        $('.short-description .btn').click(function(e){
            e.preventDefault();

            var full_description = $('.short-description .full-description').clone();

            $('.short-description').replaceWith(full_description);
        });

        // Celebrity subscribe/unsubscribe
        /*$(document).on('click', '.celebrity-subscribe, .celebrity-unsubscribe', function(e){
            e.preventDefault();

            $.get($(this).attr('href'), {}, function(response){
                console.log(response);
            });
        });*/

        // Login and register forms
        $('#login-modal form, #registration-modal form').submit(function(e){
            e.preventDefault();

            var form = $(this);

            $('.has-error', form).removeClass('has-error');
            $('.error-section *', form).remove();

            $.post(form.attr('action'), form.serialize(), function(response){
                if (response['authenticated']) {
                    var redirect_url = get_query_string_param('next');

                    if (!redirect_url) {
                        redirect_url = response['redirect_to'];
                    }

                    window.location = redirect_url;
                } else {
                    $.each(response['errors'], function(k, v){
                        $('input[name="' + k + '"]', form).parent().addClass('has-error');

                        if (k == 'all') {
                            $('.error-section', form).append('<p class="error">' + 'form-error: ' + v + '</p>');
                        } else {
                            $('.error-section', form).append('<p class="error">' + k + ': '+ v + '</p>');
                        }
                    });
                }
            });
        });

        // Account settings form
        $('#account-settings .account-avatar .btn').click(function(e){
            $('#account-settings .account-avatar input[type="file"]').click();
        });

        $('#account-settings .account-avatar input[type="file"]').change(function (e) {
            var input = $(this)[0];
            if (input.files && input.files[0]) {
                if (input.files[0].type.match('image.*')) {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        $('#account-settings .account-avatar img').attr('src', e.target.result);
                    }
                    reader.readAsDataURL(input.files[0]);
                } else console.log('is not image mime type');
            } else console.log('not isset files data or files API not supordet');
        });

        $('#account-settings').submit(function(e){
            e.preventDefault();

            var form = $(this);

            $('.has-error', form).removeClass('has-error');
            $('.error', form).remove();
            $('.messages *', form).remove();

            var options = {
                beforeSubmit: function() {
                    if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
                        alert("Please upgrade your browser, because your current browser lacks some new features we need!");
                    }
                },
                success: function(response) {
                    if (response['errors']) {
                        $.each(response['errors'], function(k, v){
                            $('input[name="' + k + '"]', form).parent().addClass('has-error');
                            $('input[name="' + k + '"]', form).after('<p class="error">' + k + ': '+ v + '</p>');
                        });
                    }

                    if (response['success']) {
                        var message_html = '<div class="alert alert-info alert-dismissible" role="alert">';
                            message_html += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">';
                            message_html += '<span aria-hidden="true">&times;</span></button>';
                            message_html += response['message'] + '</div>';

                        $('.messages', form).append(message_html);
                    }
                }
            };

            form.ajaxSubmit(options);
        });

        //Helpers
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

        function modal_handler(){
            var modal = get_query_string_param('modal');

            if (modal) {
                $('#' + modal).modal();
            }
        }
    });
})(jQuery)