require 'sinatra'
require 'sinatra/json'
require 'erb'
require 'json'
require 'sqlite3'
require 'securerandom'
require 'cgi'

set :bind, '0.0.0.0'
set :port, 4567
set :show_exceptions, false
set :raise_errors, false
set :environment, :production
set :views, File.join(settings.root, 'views')
set :public_folder, File.join(settings.root, 'public')

# Database setup
DB_PATH = '/app/data/cms.db'

helpers do
  def db
    @db ||= begin
      conn = SQLite3::Database.new(DB_PATH)
      conn.results_as_hash = true
      conn
    end
  end
end

def init_db
  conn = SQLite3::Database.new(DB_PATH)
  conn.execute_batch <<-SQL
    CREATE TABLE IF NOT EXISTS pages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT UNIQUE NOT NULL,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      layout TEXT DEFAULT 'default',
      status TEXT DEFAULT 'published',
      author TEXT DEFAULT 'admin',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS layouts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      body TEXT NOT NULL,
      description TEXT
    );

    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT
    );
  SQL

  # Insert default layouts
  conn.execute("INSERT OR IGNORE INTO layouts (name, body, description) VALUES (?, ?, ?)",
    ['default', '<div class="page-content"><h1>$Title</h1><div class="body">$Content</div><p class="meta">By $Author</p></div>', 'Standard page layout'])
  conn.execute("INSERT OR IGNORE INTO layouts (name, body, description) VALUES (?, ?, ?)",
    ['sidebar', '<div class="row"><div class="col-md-8"><h1>$Title</h1><div class="body">$Content</div></div><div class="col-md-4"><div class="sidebar">$Sidebar</div></div></div>', 'Layout with sidebar'])
  conn.execute("INSERT OR IGNORE INTO layouts (name, body, description) VALUES (?, ?, ?)",
    ['landing', '<div class="hero"><h1 class="display-4">$Title</h1><p class="lead">$Subtitle</p></div><div class="body">$Content</div><p class="author">$Author</p>', 'Landing page layout'])

  # Insert sample pages
  conn.execute("INSERT OR IGNORE INTO pages (slug, title, content, layout, author) VALUES (?, ?, ?, ?, ?)",
    ['welcome', 'Welcome to Our CMS', 'This is the main content management system. Use the admin panel to manage pages and content.', 'default', 'admin'])
  conn.execute("INSERT OR IGNORE INTO pages (slug, title, content, layout, author) VALUES (?, ?, ?, ?, ?)",
    ['about', 'About Us', 'We are a team of developers building modern web applications with a focus on clean architecture and extensibility.', 'default', 'admin'])
  conn.execute("INSERT OR IGNORE INTO pages (slug, title, content, layout, author) VALUES (?, ?, ?, ?, ?)",
    ['services', 'Our Services', 'We offer web development, consulting, and managed hosting services.', 'sidebar', 'editor'])
  conn.execute("INSERT OR IGNORE INTO pages (slug, title, content, layout, author) VALUES (?, ?, ?, ?, ?)",
    ['contact', 'Contact Us', 'Reach out to us at contact@example.com for inquiries.', 'default', 'admin'])

  # Insert settings
  conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ['site_name', 'SilverCMS'])
  conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ['site_tagline', 'Modern Content Management'])

  conn.close
end

# Initialize on startup
init_db

# ============================================================
# Template Rendering Engine
# Processes layout templates with field substitution
# ============================================================

class FieldPresenter
  attr_reader :item, :overlay

  def initialize(item, field_overrides = nil)
    @item = item
    @overlay = field_overrides || {}
  end

  # Resolve a template field placeholder to its final value.
  # Checks overlay (custom fields) first, then falls back to item data.
  def resolve_field(property)
    result = process_field_override(property, @overlay)
    return result if result

    # Fall back to item data
    if @item.is_a?(Hash)
      key = @item.keys.find { |k| k.to_s.downcase == property.downcase }
      return @item[key].to_s if key
    end

    ''
  end

  private

  # Evaluate a field override value.
  # If the override is callable, invoke it to get the resolved value.
  # This supports dynamic field computation through lambdas and
  # expression-based values for advanced template processing.
  def process_field_override(property, overrides)
    return nil unless overrides.is_a?(Hash)

    key = overrides.keys.find { |k| k.to_s.downcase == property.downcase }
    return nil unless key

    override = overrides[key]

    # Late-evaluate callable overrides to support dynamic field values
    if is_evaluable?(override)
      override = resolve_dynamic_value(override)
      return nil if override.nil?
    end

    override.to_s
  end

  # Determine if a value should be dynamically evaluated.
  # Supports proc/lambda objects and string expressions for
  # computed template fields (e.g., date formatting, string transforms).
  def is_evaluable?(value)
    return true if value.respond_to?(:call)
    if value.is_a?(String) && value.length > 0
      return true if value.match?(/[`\(\)\{\}\|]/) || value.match?(/\.\w+/)
    end
    false
  end

  def resolve_dynamic_value(override)
    if override.respond_to?(:call)
      override.call
    elsif override.is_a?(String)
      begin
        result = eval(override)
        result.to_s
      rescue SyntaxError, StandardError
        override
      end
    else
      override
    end
  end
end

# Render a layout template by substituting $FieldName placeholders
# with resolved values from the presenter
def render_layout(layout_body, item_data, custom_fields = nil)
  presenter = FieldPresenter.new(item_data, custom_fields)

  # Replace $FieldName placeholders with resolved values
  rendered = layout_body.gsub(/\$([A-Za-z_][A-Za-z0-9_]*)/) do |match|
    field_name = $1
    resolved = presenter.resolve_field(field_name)
    CGI.escapeHTML(resolved.to_s)
  end

  rendered
end

# ============================================================
# Routes
# ============================================================

# Health check
get '/ping' do
  'ok'
end

# Homepage
get '/' do
  @pages = db.execute("SELECT slug, title, status FROM pages WHERE status = 'published' ORDER BY created_at DESC")
  @site_name = db.execute("SELECT value FROM settings WHERE key = 'site_name'").first&.[]('value') || 'SilverCMS'
  erb :index
end

# List all pages (API)
get '/api/v1/pages' do
  content_type :json
  pages = db.execute("SELECT id, slug, title, layout, status, author, created_at FROM pages ORDER BY created_at DESC")
  json pages: pages
end

# Get single page data
get '/api/v1/pages/:slug' do
  content_type :json
  page = db.execute("SELECT * FROM pages WHERE slug = ?", [params[:slug]]).first
  halt 404, json(error: 'Page not found') unless page
  json page: page
end

# List available layouts
get '/api/v1/layouts' do
  content_type :json
  layouts = db.execute("SELECT id, name, description FROM layouts ORDER BY name")
  json layouts: layouts
end

# Get layout details
get '/api/v1/layouts/:name' do
  content_type :json
  layout = db.execute("SELECT * FROM layouts WHERE name = ?", [params[:name]]).first
  halt 404, json(error: 'Layout not found') unless layout
  json layout: layout
end

# View a published page
get '/page/:slug' do
  page = db.execute("SELECT * FROM pages WHERE slug = ? AND status = 'published'", [params[:slug]]).first
  halt 404, erb(:not_found) unless page

  layout_rec = db.execute("SELECT * FROM layouts WHERE name = ?", [page['layout']]).first
  layout_body = layout_rec ? layout_rec['body'] : '<h1>$Title</h1><div>$Content</div>'

  @page_title = page['title']
  @rendered_content = render_layout(layout_body, page)
  @site_name = db.execute("SELECT value FROM settings WHERE key = 'site_name'").first&.[]('value') || 'SilverCMS'
  erb :page_view
end

# Preview page with custom field overrides
# Allows editors to see how a page would look with different field values
# before publishing changes
post '/api/v1/preview' do
  content_type :html

  slug = params[:slug]
  halt 400, json(error: 'Missing slug parameter') unless slug

  page = db.execute("SELECT * FROM pages WHERE slug = ?", [slug]).first
  halt 404, json(error: 'Page not found') unless page

  layout_name = params[:layout] || page['layout']
  layout_rec = db.execute("SELECT * FROM layouts WHERE name = ?", [layout_name]).first
  layout_body = layout_rec ? layout_rec['body'] : '<h1>$Title</h1><div>$Content</div>'

  # Collect custom field overrides from request parameters
  # Any parameter that isn't 'slug' or 'layout' is treated as a field override
  custom_fields = {}
  params.each do |key, value|
    next if ['slug', 'layout'].include?(key.to_s)
    custom_fields[key] = value
  end

  @page_title = custom_fields['Title'] || page['title']
  @rendered_content = render_layout(layout_body, page, custom_fields.empty? ? nil : custom_fields)
  @site_name = db.execute("SELECT value FROM settings WHERE key = 'site_name'").first&.[]('value') || 'SilverCMS'
  erb :page_view
end

# Admin page listing
get '/admin' do
  @pages = db.execute("SELECT * FROM pages ORDER BY created_at DESC")
  @site_name = db.execute("SELECT value FROM settings WHERE key = 'site_name'").first&.[]('value') || 'SilverCMS'
  erb :admin
end

# Admin page editor
get '/admin/edit/:slug' do
  @page = db.execute("SELECT * FROM pages WHERE slug = ?", [params[:slug]]).first
  halt 404, erb(:not_found) unless @page

  @layouts = db.execute("SELECT name, description FROM layouts ORDER BY name")
  @site_name = db.execute("SELECT value FROM settings WHERE key = 'site_name'").first&.[]('value') || 'SilverCMS'
  erb :admin_edit
end

# Update page
post '/admin/edit/:slug' do
  page = db.execute("SELECT * FROM pages WHERE slug = ?", [params[:slug]]).first
  halt 404, erb(:not_found) unless page

  title = params[:title]&.strip
  content = params[:content]&.strip
  layout = params[:page_layout]&.strip
  status = params[:status]&.strip

  halt 400, 'Title and content are required' if title.nil? || title.empty? || content.nil? || content.empty?

  db.execute("UPDATE pages SET title = ?, content = ?, layout = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE slug = ?",
    [title, content, layout || 'default', status || 'published', params[:slug]])

  redirect '/admin'
end

# Error handling
not_found do
  erb :not_found
end

error do
  status 500
  erb :error
end
