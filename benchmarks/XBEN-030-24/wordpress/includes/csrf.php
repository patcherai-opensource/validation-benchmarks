<?php

require_once __DIR__.'/functions.php';
require_once __DIR__.'/session.php';
require_once __DIR__.'/config.php';
require_once __DIR__.'/authenticate.php';

ensureCSRFSessionToken();

if (csrfValidateRequest() && !CSRFValidate()) {
    handleInvalidCSRFToken();
}
