/**
 * Created by base on 31.05.17.
 */
EBANX.config.setMode('test');
EBANX.config.setPublishableKey($('#public-key').val());
EBANX.config.setCountry($('#country').val().toLowerCase());