require 'sinatra'
require 'erb'
require 'net/http'
require 'json'
require 'cgi'

set :bind, '0.0.0.0'
set :environment, :production
set :show_exceptions, false

error do
  status 500
  'An error occurred'
end

error 404 do
  'Page not found'
end

get '/' do
  erb :index
end

get '/generator' do
  erb :generator
end

def escape_single_quote(str)
  str.to_s.gsub("'") { "\\'" }
end

def build_client_code(server, path, port)
  escaped_server = escape_single_quote(server)
  escaped_path = escape_single_quote(path)
  
  code = <<~RUBY
    require 'net/http'
    require 'uri'
    
    class APIClient
      def initialize(server, path = '/api', port = 80)
        @server = server
        @path = path
        @port = port
      end
      
      def call(method_name, params = {})
        uri = URI("http://\#{@server}:\#{@port}\#{@path}")
        http = Net::HTTP.new(uri.host, uri.port)
        request = Net::HTTP::Post.new(uri.path)
        request['Content-Type'] = 'application/json'
        request.body = { method: method_name, params: params }.to_json
        
        begin
          response = http.request(request)
          JSON.parse(response.body)
        rescue => e
          { error: e.message }
        end
      end
    end
    
    client = APIClient.new('#{escaped_server}', '#{escaped_path}', #{port.to_i})
  RUBY
  
  code
end

post '/generate-code' do
  content_type :json
  
  server = params[:server] || ''
  path = params[:path] || '/api'
  port = params[:port] || '80'
  
  if server.empty?
    return { success: false, error: 'Server address is required' }.to_json
  end
  
  code = build_client_code(server, path, port)
  
  { success: true, code: code }.to_json
end

post '/test-connection' do
  content_type :json
  
  server = params[:server] || ''
  path = params[:path] || '/api'
  port = params[:port] || '80'
  
  if server.empty?
    return { success: false, error: 'Server address is required' }.to_json
  end
  
  code = build_client_code(server, path, port)
  
  begin
    binding_context = binding
    result = eval(code, binding_context)
    
    test_output = nil
    begin
      client_obj = binding_context.local_variable_get(:client)
      if client_obj
        test_output = client_obj.call('ping')
      end
    rescue NameError
    end
    
    { success: true, message: 'Code executed successfully', result: result.to_s, test_output: test_output }.to_json
  rescue => e
    { success: false, error: 'Connection test failed' }.to_json
  end
end

get '/docs' do
  erb :docs
end

__END__

@@index
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>APIWrapper - Client Code Generator</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <a class="navbar-brand" href="/">APIWrapper</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/generator">Code Generator</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/docs">Documentation</a>
          </li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="jumbotron">
        <h1 class="display-4">APIWrapper</h1>
        <p class="lead">Generate client wrapper code for your API endpoints. Quickly create reusable client classes that can be integrated into your Ruby applications.</p>
        <hr class="my-4">
        <p>Our code generator creates clean, production-ready API client code based on your server configuration.</p>
        <a class="btn btn-primary btn-lg" href="/generator" role="button">Start Generating</a>
      </div>
      
      <div class="row">
        <div class="col-md-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Easy Configuration</h5>
              <p class="card-text">Simply enter your server address, path, and port to generate client code instantly.</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Test Connections</h5>
              <p class="card-text">Test your configuration before deploying with our built-in connection tester.</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Production Ready</h5>
              <p class="card-text">Generated code follows best practices and is ready for production use.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <footer class="footer mt-5 py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">APIWrapper v2.1.0</span>
      </div>
    </footer>
 
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@generator
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/github.min.css">
    <title>Code Generator - APIWrapper</title>
    <style>
      pre { background: #f8f9fa; padding: 15px; border-radius: 5px; }
      .code-output { min-height: 200px; }
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <a class="navbar-brand" href="/">APIWrapper</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
          <li class="nav-item active">
            <a class="nav-link" href="/generator">Code Generator</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/docs">Documentation</a>
          </li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="row">
        <div class="col-md-5">
          <div class="card">
            <div class="card-header">
              <h5>Server Configuration</h5>
            </div>
            <div class="card-body">
              <form id="generator-form">
                <div class="form-group">
                  <label for="server">Server Address</label>
                  <input type="text" class="form-control" id="server" name="server" placeholder="api.example.com" required>
                  <small class="form-text text-muted">The hostname or IP address of your API server</small>
                </div>
                <div class="form-group">
                  <label for="path">API Path</label>
                  <input type="text" class="form-control" id="path" name="path" value="/api" placeholder="/api">
                  <small class="form-text text-muted">The base path for API requests</small>
                </div>
                <div class="form-group">
                  <label for="port">Port</label>
                  <input type="number" class="form-control" id="port" name="port" value="80" placeholder="80">
                </div>
                <div class="btn-group w-100">
                  <button type="submit" class="btn btn-primary">Generate Code</button>
                  <button type="button" id="test-btn" class="btn btn-secondary">Test Connection</button>
                </div>
              </form>
            </div>
          </div>
          
          <div class="card mt-3" id="test-result-card" style="display:none;">
            <div class="card-header">
              <h5>Test Result</h5>
            </div>
            <div class="card-body">
              <div id="test-result"></div>
            </div>
          </div>
        </div>
        
        <div class="col-md-7">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Generated Client Code</h5>
              <button class="btn btn-sm btn-outline-secondary" id="copy-btn">Copy to Clipboard</button>
            </div>
            <div class="card-body">
              <pre class="code-output"><code id="generated-code" class="language-ruby">Configure your server settings and click "Generate Code" to create your API client.</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <footer class="footer mt-5 py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">APIWrapper v2.1.0</span>
      </div>
    </footer>

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/highlight.min.js"></script>
    <script>
      $(document).ready(function() {
        $('#generator-form').on('submit', function(e) {
          e.preventDefault();
          
          $.post('/generate-code', $(this).serialize(), function(data) {
            if (data.success) {
              $('#generated-code').text(data.code);
              hljs.highlightElement(document.getElementById('generated-code'));
            } else {
              alert('Error: ' + data.error);
            }
          }, 'json');
        });
        
        $('#test-btn').on('click', function() {
          var formData = $('#generator-form').serialize();
          
          $('#test-result').html('<span class="text-info">Testing connection...</span>');
          $('#test-result-card').show();
          
          $.post('/test-connection', formData, function(data) {
            if (data.success) {
              $('#test-result').html('<span class="text-success">Connection test passed!</span>');
            } else {
              $('#test-result').html('<span class="text-danger">Connection failed: ' + (data.error || 'Unknown error') + '</span>');
            }
          }, 'json').fail(function() {
            $('#test-result').html('<span class="text-danger">Request failed</span>');
          });
        });
        
        $('#copy-btn').on('click', function() {
          var code = $('#generated-code').text();
          navigator.clipboard.writeText(code).then(function() {
            alert('Code copied to clipboard!');
          });
        });
      });
    </script>
  </body>
</html>

@@docs
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Documentation - APIWrapper</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <a class="navbar-brand" href="/">APIWrapper</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/generator">Code Generator</a>
          </li>
          <li class="nav-item active">
            <a class="nav-link" href="/docs">Documentation</a>
          </li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <h1>Documentation</h1>
      <hr>
      
      <div class="card mb-4">
        <div class="card-header">
          <h4>Getting Started</h4>
        </div>
        <div class="card-body">
          <p>APIWrapper helps you generate Ruby client code for connecting to API endpoints. Follow these steps:</p>
          <ol>
            <li>Navigate to the <a href="/generator">Code Generator</a> page</li>
            <li>Enter your server address (hostname or IP)</li>
            <li>Specify the API path and port</li>
            <li>Click "Generate Code" to create your client</li>
            <li>Optionally use "Test Connection" to verify your configuration</li>
            <li>Copy the generated code into your application</li>
          </ol>
        </div>
      </div>
      
      <div class="card mb-4">
        <div class="card-header">
          <h4>API Endpoints</h4>
        </div>
        <div class="card-body">
          <h5>POST /generate-code</h5>
          <p>Generates client wrapper code based on provided configuration.</p>
          <p><strong>Parameters:</strong></p>
          <ul>
            <li><code>server</code> - Server hostname or IP address (required)</li>
            <li><code>path</code> - API base path (default: /api)</li>
            <li><code>port</code> - Server port (default: 80)</li>
          </ul>
          
          <h5 class="mt-4">POST /test-connection</h5>
          <p>Tests the connection by generating and executing the client code.</p>
          <p><strong>Parameters:</strong> Same as /generate-code</p>
        </div>
      </div>
      
      <div class="card mb-4">
        <div class="card-header">
          <h4>Example Usage</h4>
        </div>
        <div class="card-body">
          <pre><code>curl -X POST http://localhost:4567/generate-code \
  -d "server=api.example.com" \
  -d "path=/v1/rpc" \
  -d "port=443"</code></pre>
        </div>
      </div>
    </div>
    
    <footer class="footer mt-5 py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">APIWrapper v2.1.0</span>
      </div>
    </footer>

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>
