require 'sinatra'
require 'json'
require 'securerandom'
require 'cgi'

set :bind, '0.0.0.0'
set :port, 4567
set :show_exceptions, false
set :environment, :production

# Simulated CMS page data store
PAGES = {
  'home' => {
    'Title' => 'Welcome to SilverCMS',
    'Content' => 'A modern content management system for building websites and web applications.',
    'MetaDescription' => 'SilverCMS - Enterprise content management',
    'Author' => 'Admin',
    'template' => 'page'
  },
  'about' => {
    'Title' => 'About Us',
    'Content' => 'SilverCMS is built with flexibility and security in mind. Our platform powers thousands of websites worldwide.',
    'MetaDescription' => 'About SilverCMS',
    'Author' => 'Content Team',
    'template' => 'page'
  },
  'contact' => {
    'Title' => 'Contact',
    'Content' => 'Get in touch with our team for support, partnerships, or general inquiries.',
    'MetaDescription' => 'Contact SilverCMS',
    'Author' => 'Support',
    'template' => 'page'
  },
  'docs' => {
    'Title' => 'Documentation',
    'Content' => 'Explore our comprehensive documentation to get started with SilverCMS templates and data models.',
    'MetaDescription' => 'SilverCMS Documentation',
    'Author' => 'Dev Team',
    'template' => 'page'
  }
}

SESSIONS = {}

# -------------------------------------------------------
# ViewableData - Template rendering engine
# Mirrors SilverStripe's ViewableData/SSViewer architecture
# -------------------------------------------------------
class ViewableData
  attr_reader :data

  def initialize(data = {})
    @data = data
  end

  # Renders the object using a named template and optional custom field overrides.
  # custom_fields: hash of field name => value overrides for the template
  def render_with(template_name, custom_fields = nil)
    overlay = custom_fields || {}
    presenter = SSViewerDataPresenter.new(@data, overlay)
    TemplateEngine.render(template_name, presenter)
  end
end

# -------------------------------------------------------
# SSViewerDataPresenter - Resolves template placeholders
# Mirrors SilverStripe's SSViewer_DataPresenter
# -------------------------------------------------------
class SSViewerDataPresenter
  def initialize(base_data, overlay)
    @base_data = base_data
    @overlay = overlay
  end

  def get_field(property)
    if @overlay.key?(property)
      process_template_override(property, @overlay)
    elsif @base_data.key?(property)
      @base_data[property]
    else
      nil
    end
  end

  # Internal helpers used for dynamic template field resolution
  def site_name
    'SilverCMS'
  end

  def site_version
    '4.13.14'
  end

  def current_date
    Time.now.strftime('%Y-%m-%d')
  end

  def site_config
    File.read('/app/config/site.yml').strip rescue 'Configuration unavailable'
  end

  def cache_key
    SecureRandom.hex(8)
  end

  private

  # Process a template override value.
  # If the override is callable, invoke it to get the resolved value.
  # This supports dynamic field resolution via closures, method references,
  # or named method lookups for template helper functions.
  def process_template_override(property, overrides)
    override = overrides[property]

    if callable?(override)
      result = invoke_callable(override)
      return result.to_s
    end

    override
  end

  # Check whether a value is callable - supports Proc, Method, and
  # string references to instance methods (for template helper resolution)
  def callable?(value)
    return false if value.nil?
    return true if value.is_a?(Proc) || value.is_a?(Method)
    if value.is_a?(String) && !value.empty?
      return respond_to?(value.to_sym, true)
    end
    false
  end

  # Invoke a callable value and return its result
  def invoke_callable(value)
    if value.is_a?(Proc)
      return value.call
    end
    if value.is_a?(Method)
      return value.call
    end
    if value.is_a?(String)
      return send(value.to_sym)
    end
    value
  rescue ArgumentError, NoMethodError => e
    value
  end
end

# -------------------------------------------------------
# TemplateEngine - Simple template processor
# -------------------------------------------------------
module TemplateEngine
  TEMPLATES = {}

  def self.register(name, content)
    TEMPLATES[name] = content
  end

  def self.render(template_name, presenter)
    tmpl = TEMPLATES[template_name]
    return "Template not found: #{template_name}" unless tmpl

    # Replace $FieldName placeholders with presenter-resolved values
    result = tmpl.gsub(/\$([A-Za-z_][A-Za-z0-9_]*)/) do |match|
      field = $1
      val = presenter.get_field(field)
      val.nil? ? '' : CGI.escapeHTML(val.to_s)
    end
    result
  end
end

# Register CMS templates (Silverstripe-style .ss template syntax adapted)
TemplateEngine.register('page', <<~TEMPLATE
  <div class="cms-page">
    <article>
      <h1>$Title</h1>
      <div class="meta">
        <span class="author">By $Author</span>
      </div>
      <div class="content">
        <p>$Content</p>
      </div>
    </article>
  </div>
TEMPLATE
)

TemplateEngine.register('preview', <<~TEMPLATE
  <div class="preview-panel">
    <div class="preview-header">
      <h2>$Title</h2>
      <small>$MetaDescription</small>
    </div>
    <div class="preview-body">
      <p>$Content</p>
    </div>
    <div class="preview-meta">
      <span>Author: $Author</span>
      <span>Greeting: $Greeting</span>
    </div>
  </div>
TEMPLATE
)

# Simple session helper
def get_session(req)
  session_id = req.cookies['cms_session']
  if session_id && SESSIONS[session_id]
    SESSIONS[session_id]
  else
    nil
  end
end

def create_session(username)
  session_id = SecureRandom.hex(16)
  SESSIONS[session_id] = { 'username' => username, 'created' => Time.now.to_i }
  session_id
end

# CMS Admin users
ADMIN_USERS = {
  'editor' => 'editor',
  'admin' => 'admin'
}

# -------------------------------------------------------
# Routes
# -------------------------------------------------------

# Public pages
get '/' do
  content_type :html
  render_public_page('home')
end

get '/page/:slug' do
  slug = params[:slug]
  unless PAGES.key?(slug)
    status 404
    return render_error_page(404, 'Page not found')
  end
  content_type :html
  render_public_page(slug)
end

# Admin login
get '/admin/login' do
  content_type :html
  render_login_page
end

post '/admin/login' do
  username = params[:username].to_s.strip
  password = params[:password].to_s

  if ADMIN_USERS[username] && ADMIN_USERS[username] == password
    session_id = create_session(username)
    response.set_cookie('cms_session', {
      value: session_id,
      path: '/',
      httponly: true
    })
    redirect '/admin/pages'
  else
    status 401
    content_type :html
    render_login_page('Invalid credentials')
  end
end

get '/admin/logout' do
  session_id = request.cookies['cms_session']
  SESSIONS.delete(session_id) if session_id
  response.delete_cookie('cms_session', path: '/')
  redirect '/admin/login'
end

# Admin pages list
get '/admin/pages' do
  session = get_session(request)
  unless session
    redirect '/admin/login'
    return
  end

  content_type :html
  render_admin_pages_list(session)
end

# Page preview with custom field overrides
# This endpoint allows editors to preview pages with customised template fields.
# Custom field values are passed as query/form parameters prefixed with "field_"
get '/admin/pages/:slug/preview' do
  session = get_session(request)
  unless session
    redirect '/admin/login'
    return
  end

  slug = params[:slug]
  page = PAGES[slug]
  unless page
    status 404
    return render_error_page(404, 'Page not found')
  end

  # Collect custom field overrides from query parameters
  custom_fields = {}
  params.each do |key, value|
    if key.start_with?('field_')
      field_name = key.sub('field_', '')
      custom_fields[field_name] = value
    end
  end

  content_type :html
  viewable = ViewableData.new(page)
  rendered = viewable.render_with('preview', custom_fields.empty? ? nil : custom_fields)

  render_admin_preview(slug, rendered, session)
end

post '/admin/pages/:slug/preview' do
  session = get_session(request)
  unless session
    redirect '/admin/login'
    return
  end

  slug = params[:slug]
  page = PAGES[slug]
  unless page
    status 404
    return render_error_page(404, 'Page not found')
  end

  # Collect custom field overrides from form body
  custom_fields = {}
  params.each do |key, value|
    if key.start_with?('field_')
      field_name = key.sub('field_', '')
      custom_fields[field_name] = value
    end
  end

  content_type :html
  viewable = ViewableData.new(page)
  rendered = viewable.render_with('preview', custom_fields.empty? ? nil : custom_fields)

  render_admin_preview(slug, rendered, session)
end

# API endpoint for template field info
get '/api/v1/schema' do
  content_type :json
  {
    fields: ['Title', 'Content', 'MetaDescription', 'Author', 'Greeting'],
    templates: ['page', 'preview'],
    version: '4.13.14'
  }.to_json
end

# Health check
get '/ping' do
  'ok'
end

# Catch-all for 404
not_found do
  render_error_page(404, 'Page not found')
end

error do
  render_error_page(500, 'Internal server error')
end

# -------------------------------------------------------
# HTML Renderers
# -------------------------------------------------------

def page_layout(title, body, nav_active = nil)
  <<~HTML
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <title>#{CGI.escapeHTML(title)} - SilverCMS</title>
      <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
      <style>
        .navbar-brand { font-weight: bold; }
        .cms-page .meta { color: #666; margin-bottom: 1rem; }
        .footer { margin-top: 3rem; padding: 1rem 0; border-top: 1px solid #eee; color: #999; font-size: 0.85rem; }
      </style>
    </head>
    <body>
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="/">SilverCMS</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item#{nav_active == 'home' ? ' active' : ''}">
              <a class="nav-link" href="/">Home</a>
            </li>
            <li class="nav-item#{nav_active == 'about' ? ' active' : ''}">
              <a class="nav-link" href="/page/about">About</a>
            </li>
            <li class="nav-item#{nav_active == 'docs' ? ' active' : ''}">
              <a class="nav-link" href="/page/docs">Documentation</a>
            </li>
            <li class="nav-item#{nav_active == 'contact' ? ' active' : ''}">
              <a class="nav-link" href="/page/contact">Contact</a>
            </li>
          </ul>
          <ul class="navbar-nav ml-auto">
            <li class="nav-item">
              <a class="nav-link" href="/admin/login">Admin</a>
            </li>
          </ul>
        </div>
      </nav>
      <div class="container mt-4">
        #{body}
      </div>
      <div class="container footer">
        <p>&copy; 2024 SilverCMS. Powered by SilverCMS v4.13.14</p>
      </div>
      <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
  HTML
end

def render_public_page(slug)
  page = PAGES[slug]
  viewable = ViewableData.new(page)
  rendered = viewable.render_with(page['template'])
  page_layout(page['Title'], rendered, slug)
end

def render_error_page(code, message)
  body = <<~HTML
    <div class="text-center mt-5">
      <h1>#{code}</h1>
      <p class="lead">#{CGI.escapeHTML(message)}</p>
      <a href="/" class="btn btn-primary">Go Home</a>
    </div>
  HTML
  page_layout("#{code} Error", body)
end

def render_login_page(error = nil)
  error_html = error ? "<div class='alert alert-danger'>#{CGI.escapeHTML(error)}</div>" : ''
  body = <<~HTML
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card mt-5">
          <div class="card-header bg-dark text-white">
            <h5 class="mb-0">CMS Admin Login</h5>
          </div>
          <div class="card-body">
            #{error_html}
            <form action="/admin/login" method="post">
              <div class="form-group">
                <label for="username">Username</label>
                <input type="text" class="form-control" id="username" name="username" required>
              </div>
              <div class="form-group">
                <label for="password">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
              </div>
              <button type="submit" class="btn btn-dark btn-block">Sign In</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  HTML
  page_layout('Admin Login', body)
end

def render_admin_pages_list(session)
  rows = PAGES.map do |slug, page|
    <<~ROW
      <tr>
        <td><a href="/page/#{slug}">#{CGI.escapeHTML(page['Title'])}</a></td>
        <td>#{CGI.escapeHTML(slug)}</td>
        <td>#{CGI.escapeHTML(page['Author'])}</td>
        <td>
          <a href="/admin/pages/#{slug}/preview" class="btn btn-sm btn-outline-secondary">Preview</a>
        </td>
      </tr>
    ROW
  end.join

  body = <<~HTML
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Pages</h3>
      <div>
        <span class="badge badge-secondary">Logged in as #{CGI.escapeHTML(session['username'])}</span>
        <a href="/admin/logout" class="btn btn-sm btn-outline-dark ml-2">Logout</a>
      </div>
    </div>
    <table class="table table-bordered table-hover">
      <thead class="thead-light">
        <tr>
          <th>Title</th>
          <th>Slug</th>
          <th>Author</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        #{rows}
      </tbody>
    </table>
    <div class="card mt-3">
      <div class="card-body">
        <h6>Preview with Custom Fields</h6>
        <p class="text-muted small">
          Use the Preview button or navigate to <code>/admin/pages/{slug}/preview?field_Title=Custom+Title&amp;field_Content=Custom+Content</code>
          to preview pages with overridden template fields.
        </p>
      </div>
    </div>
  HTML
  page_layout('Admin - Pages', body)
end

def render_admin_preview(slug, rendered_content, session)
  body = <<~HTML
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Preview: #{CGI.escapeHTML(slug)}</h3>
      <div>
        <a href="/admin/pages" class="btn btn-sm btn-outline-dark">Back to Pages</a>
        <a href="/admin/logout" class="btn btn-sm btn-outline-dark ml-2">Logout</a>
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <strong>Template Preview</strong>
      </div>
      <div class="card-body">
        #{rendered_content}
      </div>
    </div>
    <div class="card mt-3">
      <div class="card-body">
        <h6>Customise Preview</h6>
        <form action="/admin/pages/#{CGI.escapeHTML(slug)}/preview" method="post">
          <div class="form-group">
            <label>Title</label>
            <input type="text" class="form-control" name="field_Title" placeholder="Override title...">
          </div>
          <div class="form-group">
            <label>Content</label>
            <textarea class="form-control" name="field_Content" rows="3" placeholder="Override content..."></textarea>
          </div>
          <div class="form-group">
            <label>Author</label>
            <input type="text" class="form-control" name="field_Author" placeholder="Override author...">
          </div>
          <div class="form-group">
            <label>Greeting</label>
            <input type="text" class="form-control" name="field_Greeting" placeholder="Custom greeting field...">
          </div>
          <button type="submit" class="btn btn-dark">Update Preview</button>
        </form>
      </div>
    </div>
  HTML
  page_layout("Preview - #{slug}", body)
end
