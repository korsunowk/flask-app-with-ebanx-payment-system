$(document).ready(function() {

    $('#pay-type').on('change', function () {
        var type = $(this).val();

        if (type !== '' && type !== undefined ) {
            $.ajax({
                url: $(this).data('url'),
                type: 'get',
                data: {
                    'pay-type': type
                },
                success: function (data) {
                    if (data.success === 'true') {
                        if ($('.open').get(0)) {
                            $('.open').remove();
                        }
                        $('#submit').before(data.template);
                        $('#submit').removeAttr('disabled');
                    }
                }
            })
        }
        else {
            $('.open').remove();
            $('#submit').attr('disabled', 'disabled');
        }
    });

    $('#submit').on('click', function () {
        var valid = true;

        $.each($('form').serializeArray(), function (i, val) {
           if (val.value === '' || val.value === undefined)
               valid = false;
        });

        if (!valid) {
            alert('Fill all inputs, please.')
        }

        return valid;
    })
});