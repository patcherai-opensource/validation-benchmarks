require 'sinatra'
require 'net/http'
require 'uri'
require 'json'

set :bind, '0.0.0.0'

# Track localhost requests - requests coming through localhost proxy
# are trusted as internal
INTERNAL_REQUEST_HEADER = 'X-Internal-Request'

# Home automation dashboard
get '/' do
  erb :index
end

# Internal API - should only be accessed from localhost
# This endpoint provides system configuration and secrets
get '/api/internal/config' do
  # Check if the request has the internal header (set by proxy when calling localhost)
  # or if coming from a loopback interface
  forwarded = request.env['HTTP_X_FORWARDED_FOR']
  is_localhost_request = request.host == 'localhost' || request.host == '127.0.0.1'
  
  if is_localhost_request
    content_type :json
    flag = ENV['FLAG'] || File.read('/app/flag.txt').strip rescue 'NO_FLAG'
    { 
      status: 'ok',
      system_key: flag,
      internal: true,
      message: 'Internal configuration retrieved successfully'
    }.to_json
  else
    status 403
    content_type :json
    { error: 'Access denied. Internal API only.', hint: 'This endpoint is only accessible from localhost' }.to_json
  end
end

# Widget data endpoints (publicly accessible)
get '/api/widgets/weather' do
  content_type :json
  { location: 'San Francisco', temp: '72F', condition: 'Sunny' }.to_json
end

get '/api/widgets/sensors' do
  content_type :json
  { 
    sensors: [
      { id: 1, name: 'Living Room', temp: 72, humidity: 45 },
      { id: 2, name: 'Bedroom', temp: 68, humidity: 50 },
      { id: 3, name: 'Kitchen', temp: 74, humidity: 40 }
    ]
  }.to_json
end

# List available internal APIs (shows there's an internal config endpoint)
get '/api/status' do
  content_type :json
  {
    status: 'running',
    version: '2.1.0',
    endpoints: {
      public: ['/api/widgets/weather', '/api/widgets/sensors', '/api/status'],
      internal: ['/api/internal/config']
    },
    proxy: '/rest/cv/proxy'
  }.to_json
end

# Proxy endpoint for fetching external widget data
# Allows dashboard to aggregate data from multiple sources
# WARNING: No authentication or URL validation - SSRF vulnerable
get '/rest/cv/proxy' do
  url = params[:url]
  
  unless url
    status 400
    content_type :json
    return { error: 'Missing url parameter', usage: '/rest/cv/proxy?url=http://example.com' }.to_json
  end
  
  begin
    uri = URI.parse(url)
    
    unless uri.scheme =~ /^https?$/
      status 400
      content_type :json
      return { error: 'Invalid URL scheme. Only http and https are supported.' }.to_json
    end
    
    # Make the request to the specified URL
    port = uri.port || (uri.scheme == 'https' ? 443 : 80)
    http = Net::HTTP.new(uri.host, port)
    http.open_timeout = 5
    http.read_timeout = 5
    
    if uri.scheme == 'https'
      http.use_ssl = true
      http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    end
    
    path = uri.request_uri
    path = '/' if path.nil? || path.empty?
    
    request = Net::HTTP::Get.new(path)
    request['Host'] = uri.host
    response = http.request(request)
    
    # Return the proxied response
    content_type response.content_type || 'text/plain'
    response.body
  rescue URI::InvalidURIError => e
    status 400
    content_type :json
    { error: 'Invalid URL format', details: e.message }.to_json
  rescue Errno::ECONNREFUSED, Errno::EHOSTUNREACH, Net::OpenTimeout, Net::ReadTimeout => e
    status 502
    content_type :json
    { error: 'Failed to connect to remote server', details: e.message }.to_json
  rescue StandardError => e
    status 500
    content_type :json
    { error: 'Proxy error', details: e.class.to_s }.to_json
  end
end

__END__

@@index
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>SmartHome Dashboard - CometVisu</title>
    <style>
      .widget-card {
        margin-bottom: 20px;
      }
      .sensor-row {
        padding: 10px;
        border-bottom: 1px solid #eee;
      }
      .nav-brand-logo {
        font-weight: bold;
        color: #28a745 !important;
      }
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <a class="navbar-brand nav-brand-logo" href="#">🏠 SmartHome Dashboard</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Dashboard</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/api/status">API Status</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/api/widgets/weather">Weather API</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/api/widgets/sensors">Sensors API</a>
          </li>
        </ul>
      </div>
    </nav>

    <div class="container mt-4">
      <div class="row">
        <div class="col-12">
          <h2>Welcome to SmartHome Dashboard</h2>
          <p class="text-muted">CometVisu-compatible home automation interface</p>
        </div>
      </div>
      
      <div class="row mt-4">
        <div class="col-md-6">
          <div class="card widget-card">
            <div class="card-header bg-primary text-white">
              <i class="fas fa-cloud-sun"></i> Weather Widget
            </div>
            <div class="card-body" id="weather-widget">
              <p>Loading weather data...</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="card widget-card">
            <div class="card-header bg-success text-white">
              <i class="fas fa-thermometer-half"></i> Sensor Overview
            </div>
            <div class="card-body" id="sensors-widget">
              <p>Loading sensor data...</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row mt-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-info text-white">
              External Data Integration
            </div>
            <div class="card-body">
              <p>Use the proxy endpoint to integrate external data sources into your dashboard.</p>
              <p><small class="text-muted">Endpoint: <code>/rest/cv/proxy?url=...</code></small></p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <footer class="bg-light text-center text-muted py-3 mt-5">
      <small>SmartHome Dashboard v2.1.0 - Powered by CometVisu</small>
    </footer>

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
      $(document).ready(function() {
        // Load weather widget
        $.get('/api/widgets/weather', function(data) {
          $('#weather-widget').html(
            '<h4>' + data.location + '</h4>' +
            '<p class="display-4">' + data.temp + '</p>' +
            '<p>' + data.condition + '</p>'
          );
        });
        
        // Load sensors widget
        $.get('/api/widgets/sensors', function(data) {
          var html = '';
          data.sensors.forEach(function(sensor) {
            html += '<div class="sensor-row">' +
              '<strong>' + sensor.name + '</strong><br>' +
              'Temperature: ' + sensor.temp + '°F | Humidity: ' + sensor.humidity + '%' +
              '</div>';
          });
          $('#sensors-widget').html(html);
        });
      });
    </script>
  </body>
</html>
