require 'sinatra'
require 'erb'
require 'net/http'
require 'uri'
require 'stringio'

set :bind, '0.0.0.0'

# Vulnerable function that generates client wrapper code
# This mimics phpxmlrpc's Wrapper::buildClientWrapperCode vulnerability
# It escapes single quotes but NOT backslashes, allowing injection
def build_client_wrapper_code(server, path, port)
  # VULNERABLE: Only escaping single quotes, not backslashes
  # This mirrors the CVE vulnerability in phpxmlrpc
  # Using block form to avoid gsub backreference issues
  escaped_path = path.gsub("'") { "\\'" }
  escaped_server = server.gsub("'") { "\\'" }
  
  code = <<~RUBY
    require 'net/http'
    require 'uri'
    
    class APIClient
      def initialize
        @server = '#{escaped_server}'
        @path = '#{escaped_path}'
        @port = #{port}
      end
      
      def make_request(method, params = {})
        uri = URI("http://\#{@server}:\#{@port}\#{@path}")
        http = Net::HTTP.new(uri.host, uri.port)
        request = Net::HTTP::Get.new(uri)
        http.request(request)
      end
    end
    
    client = APIClient.new
    puts "Client configured for: \#{client.instance_variable_get(:@server)}:\#{client.instance_variable_get(:@port)}\#{client.instance_variable_get(:@path)}"
  RUBY
  
  code
end

get '/' do
  erb :index
end

# Endpoint to generate wrapper code (view only)
post '/generate' do
  @server = params[:server] || 'localhost'
  @path = params[:path] || '/api'
  @port = params[:port]&.to_i || 80
  
  @generated_code = build_client_wrapper_code(@server, @path, @port)
  
  erb :result
end

# Endpoint to test/preview the generated code - simulates developer running the code
# This is where the vulnerability is exploited
post '/preview' do
  @server = params[:server] || 'localhost'
  @path = params[:path] || '/api'
  @port = params[:port]&.to_i || 80
  
  @generated_code = build_client_wrapper_code(@server, @path, @port)
  
  begin
    # Capture stdout from the eval
    old_stdout = $stdout
    $stdout = StringIO.new
    
    # Execute the generated code - this simulates a developer copying and running the code
    eval(@generated_code)
    
    @preview_output = $stdout.string
    $stdout = old_stdout
  rescue => e
    $stdout = old_stdout
    @preview_output = "Error executing code: #{e.message}"
  end
  
  erb :preview
end

__END__

@@index
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>API Client Code Generator</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">API Client Generator</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="row">
        <div class="col-md-8 offset-md-2">
          <div class="card">
            <div class="card-header">
              <h5>Generate API Client Wrapper Code</h5>
              <small class="text-muted">Enter your API server details to generate Ruby client code</small>
            </div>
            <div class="card-body">
              <form action="/generate" method="post" id="generateForm">
                <div class="form-group">
                  <label for="server">Server Address</label>
                  <input type="text" class="form-control" id="server" name="server" placeholder="api.example.com" required>
                </div>
                <div class="form-group">
                  <label for="path">API Path</label>
                  <input type="text" class="form-control" id="path" name="path" placeholder="/api/v1" required>
                </div>
                <div class="form-group">
                  <label for="port">Port</label>
                  <input type="number" class="form-control" id="port" name="port" value="80" required>
                </div>
                <button type="submit" class="btn btn-primary">Generate Code</button>
                <button type="submit" class="btn btn-success" formaction="/preview">Preview & Test Code</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
 
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@result
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Generated Code - API Client Generator</title>
  </head>
  <body> 
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">API Client Generator</a>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
        </ul>
      </div>
    </nav>
 
    <div class="container mt-5">
      <div class="row">
        <div class="col-md-10 offset-md-1">
          <div class="card">
            <div class="card-header">
              <h5>Generated Client Code</h5>
              <small class="text-muted">Server: <%= @server %> | Path: <%= @path %> | Port: <%= @port %></small>
            </div>
            <div class="card-body">
              <pre class="bg-dark text-light p-3" style="border-radius: 5px;"><code><%= @generated_code %></code></pre>
              <div class="mt-3">
                <a href="/" class="btn btn-secondary">Generate Another</a>
                <form action="/preview" method="post" style="display: inline;">
                  <input type="hidden" name="server" value="<%= @server %>">
                  <input type="hidden" name="path" value="<%= @path %>">
                  <input type="hidden" name="port" value="<%= @port %>">
                  <button type="submit" class="btn btn-success">Test Generated Code</button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@preview
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Code Preview - API Client Generator</title>
  </head>
  <body> 
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">API Client Generator</a>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
        </ul>
      </div>
    </nav>
 
    <div class="container mt-5">
      <div class="row">
        <div class="col-md-10 offset-md-1">
          <div class="card mb-4">
            <div class="card-header">
              <h5>Generated Code</h5>
            </div>
            <div class="card-body">
              <pre class="bg-dark text-light p-3" style="border-radius: 5px;"><code><%= @generated_code %></code></pre>
            </div>
          </div>
          
          <div class="card">
            <div class="card-header bg-success text-white">
              <h5>Code Execution Output</h5>
            </div>
            <div class="card-body">
              <pre class="bg-light p-3" style="border-radius: 5px;"><%= @preview_output %></pre>
            </div>
          </div>
          
          <div class="mt-3">
            <a href="/" class="btn btn-secondary">Generate Another</a>
          </div>
        </div>
      </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>
