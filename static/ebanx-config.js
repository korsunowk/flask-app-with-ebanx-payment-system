/**
 * Created by base on 31.05.17.
 */
EBANX.config.setMode('test');
EBANX.config.setPublishableKey(document.getElementById('public-key').value);
EBANX.config.setCountry(document.getElementById('country').value.toLowerCase());