(function ($) {
    $(document).ready(function () {
        var page = 2;

        $(document).on('click', '.paginate a', function (e) {
            e.preventDefault();
            $.get(window.location.pathname, {page: page}, function (response) {
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

            filters = '/?filter_tags=' + filter.join(',');

            window.location = filters;
        });

        $('.currect-tags a').click(function (e) {
            e.preventDefault();

            var current_filters = get_param('filter_tags'),
                filters = '',
                remove_tags = $(this).attr('data-store-id');

            if (remove_tags != 'all') {
                current_filters = current_filters.split(',');
                current_filters.splice(current_filters.indexOf(remove_tags), 1);
            } else {
                current_filters = [];
            }

            filters = '/?filter_tags=' + current_filters.join(',');

            window.location = filters;
        });

        $('#add-celebrity').submit(function (e) {
            /*e.preventDefault();

            $.post($(this).attr('action'), $(this).serialize(), function(response){
                console.log(response);
            })*/
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

        $('#add-celebrity .add-field').click(function(e){
            e.preventDefault();

            var field = $('#add-celebrity input[name="social_network"]').first(),
                wrapper = $('#add-celebrity .social-network');

            wrapper.append(field.clone().val(''));
        });

        //Helpers
        function get_param(name) {
            if (name = (new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)')).exec(location.search)) {
                return decodeURIComponent(name[1]);
            } else {
                return false;
            }
        }
    });
})(jQuery)