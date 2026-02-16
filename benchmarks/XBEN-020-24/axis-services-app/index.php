<?php
session_start();
header('X-Powered-By: Axis/1.3');
?>
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Apache-Axis</title>
    <style>
        body { font-family: serif; background-color: #FFFFFF; margin: 20px; }
        h1 { text-align: center; }
        ul { line-height: 1.8; }
        a { color: #0000EE; }
        .footer { margin-top: 40px; font-size: 0.9em; color: #666; border-top: 1px solid #ccc; padding-top: 10px; }
    </style>
</head>
<body>

<h1>Apache-AXIS</h1>

<p>Hello! Welcome to Apache-Axis.</p>
<p>What do you want to do today?</p>

<ul>
    <li>
        <a href="happyaxis.php">Validation</a> - Validate the local installation's configuration<br>
        <i>See below if this does not work.</i>
    </li>
    <li>
        <a href="servlet/AxisServlet">List</a> - View the list of deployed Web services
    </li>
    <li>
        <a href="EchoHeaders.php?method=list">Call</a> - Call a local endpoint that lists the caller's HTTP headers
        (or see its <a href="EchoHeaders.php?wsdl">WSDL</a>).
    </li>
    <li>
        <a href="http://ws.apache.org/axis/">Visit</a> - Visit the Apache-Axis Home Page
    </li>
    <li>
        <a href="servlet/AdminServlet">Administer Axis</a> - [disabled by default for security reasons]
    </li>
</ul>

<h3>Validating Axis</h3>

<p>To verify that the Axis installation is complete, you should click on the
validation link and examine the results. If any critical components are missing,
Axis will not work.</p>
<p>Note that you must install all required libraries in the correct location before
this validation page will be fully successful.</p>

<div class="footer">
    Copyright &copy; 2005 The Apache Software Foundation. All rights reserved.
</div>
</body>
</html>
