$(document).ready(function() {

    $('#pay-type').on('change', function () {
        var type = $(this).val();

        if (type === 'credit-card') {
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
                        $('#btnSubmit').before(data.template);
                        $('#btnSubmit').removeAttr('disabled');
                    }
                }
            })
        }
        else if (type === 'boleto') {
            $('.open').remove();
            $('#btnSubmit').removeAttr('disabled');
        }
        else {
            $('.open').remove();
            $('#btnSubmit').attr('disabled', 'disabled');
        }
    });

    $('#btnSubmit').on('click', function (e) {
        $(this).text('Loading...');
        $(this).attr('disabled', 'disabled');

        var valid = true;

        $.each($('form').serializeArray(), function (i, val) {
           if (val.value === '' || val.value === undefined)
               valid = false;
        });

        if (!valid) {
            alert('Fill all inputs, please.')
        }
        if ($('#pay-type').val() == 'boleto'){
            $('form[name="pay_form"]').submit();
            return true;
        }
        EBANX.card.createToken({
            card_number: $('#card-number').val(),
            card_name: $('#card-name').val(),
            card_due_date: $('#card-date').val(),
            card_cvv: $('#card-cvv').val()
        }, createTokenCallback);

        e.preventDefault();
        e.stopPropagation();
        return false;
    });

var createTokenCallback = function(ebanxResponse) {
    if (ebanxResponse.error.err)
        $('#error-message').val(ebanxResponse.error.err.message);
    else
        $('#card-token').val(ebanxResponse.data.token);

    $('form[name="pay_form"]').submit();
  };

});