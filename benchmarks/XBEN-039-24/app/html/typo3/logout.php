<?php
session_start();
session_destroy();
header('Location: /typo3/');
exit;
