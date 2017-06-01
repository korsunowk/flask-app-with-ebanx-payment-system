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

        EBANX.card.createToken({
            card_number: document.getElementById('card-number').value,
            card_name: document.getElementById('card-name').value,
            card_due_date: document.getElementById('card-date').value,
            card_cvv: document.getElementById('card-cvv').value
        }, createTokenCallback);

        e.preventDefault();
        e.stopPropagation();
        return false;
    });

var createTokenCallback = function(ebanxResponse) {
    if (ebanxResponse.error.err)
        document.getElementById('error-message').value = ebanxResponse.error.err.message;
    else
        document.getElementById('card-token').value = ebanxResponse.data.token;

    document.pay_form.submit();
  };

});