<!DOCTYPE html>
<html>
<head><title>GeoPortal API Documentation</title></head>
<body>
<h1>GeoPortal API v3.2.1</h1>
<h2>Proxy Endpoint</h2>
<p>The <code>/proxy/</code> endpoint allows fetching content from external geographic data sources.</p>
<h3>Usage</h3>
<pre>GET /proxy/?url=&lt;external_url&gt;</pre>
<h3>Security</h3>
<p>For security, only whitelisted domains are permitted. Attempting to access non-whitelisted hosts will return a 403 error.</p>
<h3>Allowed Hosts</h3>
<ul>
    <li>openstreetmap.org</li>
    <li>geoserver.org</li>
    <li>mapbox.com</li>
    <li>arcgisonline.com</li>
    <li>tile.openstreetmap.org</li>
    <li>localhost</li>
    <li>127.0.0.1</li>
</ul>
<h3>Example</h3>
<pre>GET /proxy/?url=http://tile.openstreetmap.org/0/0/0.png</pre>
</body>
</html>
