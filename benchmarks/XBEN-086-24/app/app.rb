require 'sinatra'
require 'erb'
require 'json'
require 'securerandom'

set :bind, '0.0.0.0'
set :port, 4567
set :public_folder, File.dirname(__FILE__) + '/public'

# In-memory storage for appointments
$appointments = {}
$services = [
  { id: 1, name: "General Consultation", duration: 30, price: 50 },
  { id: 2, name: "Health Checkup", duration: 60, price: 100 },
  { id: 3, name: "Specialist Visit", duration: 45, price: 150 },
  { id: 4, name: "Follow-up Appointment", duration: 20, price: 30 }
]
$providers = [
  { id: 1, name: "Dr. Smith", specialty: "General Practice" },
  { id: 2, name: "Dr. Johnson", specialty: "Cardiology" },
  { id: 3, name: "Dr. Williams", specialty: "Pediatrics" }
]

# Home page
get '/' do
  erb :index
end

# API endpoint for services
get '/api/services' do
  content_type :json
  $services.to_json
end

# API endpoint for providers
get '/api/providers' do
  content_type :json
  $providers.to_json
end

# Public booking form
get '/booking' do
  erb :booking
end

# About page
get '/about' do
  erb :about
end

# Contact page
get '/contact' do
  erb :contact
end

# Process booking submission
post '/booking/submit' do
  appointment_id = SecureRandom.hex(8)
  
  # Store the appointment data - no sanitization/escaping (vulnerable!)
  $appointments[appointment_id] = {
    id: appointment_id,
    customer_name: params[:customer_name],
    customer_email: params[:customer_email],
    customer_phone: params[:customer_phone],
    service_id: params[:service_id].to_i,
    provider_id: params[:provider_id].to_i,
    appointment_date: params[:appointment_date],
    appointment_time: params[:appointment_time],
    notes: params[:notes],
    created_at: Time.now.strftime("%Y-%m-%d %H:%M:%S")
  }
  
  redirect "/booking/confirmation/#{appointment_id}"
end

# Appointment confirmation - renders stored data via ERB (vulnerable!)
get '/booking/confirmation/:id' do
  @appointment = $appointments[params[:id]]
  halt 404, "Appointment not found" unless @appointment
  
  @service = $services.find { |s| s[:id] == @appointment[:service_id] }
  @provider = $providers.find { |p| p[:id] == @appointment[:provider_id] }
  
  erb :confirmation
end

# View appointment details (for email preview simulation)
get '/appointment/:id/details' do
  @appointment = $appointments[params[:id]]
  halt 404, "Appointment not found" unless @appointment
  
  @service = $services.find { |s| s[:id] == @appointment[:service_id] }
  @provider = $providers.find { |p| p[:id] == @appointment[:provider_id] }
  
  erb :appointment_details
end

# Email notification preview (mimics email template rendering)
get '/appointment/:id/email-preview' do
  @appointment = $appointments[params[:id]]
  halt 404, "Appointment not found" unless @appointment
  
  @service = $services.find { |s| s[:id] == @appointment[:service_id] }
  @provider = $providers.find { |p| p[:id] == @appointment[:provider_id] }
  
  # Vulnerable: renders appointment data including notes without escaping through ERB
  erb :email_preview
end

# Admin area (placeholder - not functional)
get '/admin' do
  erb :admin_login
end

# Health check endpoint
get '/health' do
  "OK"
end

__END__

@@layout
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>QuickBook Appointments</title>
    <style>
      .navbar-brand { font-weight: bold; color: #007bff !important; }
      .footer { background-color: #f8f9fa; padding: 20px 0; margin-top: 50px; }
      .btn-book { background-color: #28a745; border-color: #28a745; }
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">QuickBook</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="/booking">Book Appointment</a></li>
          <li class="nav-item"><a class="nav-link" href="/about">About</a></li>
          <li class="nav-item"><a class="nav-link" href="/contact">Contact</a></li>
        </ul>
      </div>
    </nav>
    <%= yield %>
    <footer class="footer">
      <div class="container text-center">
        <span class="text-muted">&copy; 2024 QuickBook Appointments - Online Scheduling Made Easy</span>
      </div>
    </footer>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@index
<div class="container mt-5">
  <div class="jumbotron">
    <h1 class="display-4">Welcome to QuickBook</h1>
    <p class="lead">The easiest way to schedule appointments online. Book your appointment in minutes!</p>
    <hr class="my-4">
    <p>Choose from our qualified healthcare providers and convenient time slots.</p>
    <a class="btn btn-primary btn-lg" href="/booking" role="button">Book Now</a>
  </div>
  
  <div class="row mt-4">
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Easy Booking</h5>
          <p class="card-text">Book appointments 24/7 from anywhere. No phone calls needed.</p>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Email Confirmations</h5>
          <p class="card-text">Receive instant confirmation emails with all appointment details.</p>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Expert Providers</h5>
          <p class="card-text">Access to qualified healthcare professionals.</p>
        </div>
      </div>
    </div>
  </div>
</div>

@@booking
<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <div class="card">
        <div class="card-header bg-primary text-white">
          <h4>Book Your Appointment</h4>
        </div>
        <div class="card-body">
          <form action="/booking/submit" method="post" id="bookingForm">
            <h5>Personal Information</h5>
            <div class="form-row">
              <div class="form-group col-md-6">
                <label for="customer_name">Full Name *</label>
                <input type="text" class="form-control" id="customer_name" name="customer_name" required>
              </div>
              <div class="form-group col-md-6">
                <label for="customer_email">Email Address *</label>
                <input type="email" class="form-control" id="customer_email" name="customer_email" required>
              </div>
            </div>
            <div class="form-group">
              <label for="customer_phone">Phone Number</label>
              <input type="tel" class="form-control" id="customer_phone" name="customer_phone">
            </div>
            
            <hr>
            <h5>Appointment Details</h5>
            
            <div class="form-group">
              <label for="service_id">Service *</label>
              <select class="form-control" id="service_id" name="service_id" required>
                <option value="">Select a service...</option>
                <option value="1">General Consultation (30 min) - $50</option>
                <option value="2">Health Checkup (60 min) - $100</option>
                <option value="3">Specialist Visit (45 min) - $150</option>
                <option value="4">Follow-up Appointment (20 min) - $30</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="provider_id">Provider *</label>
              <select class="form-control" id="provider_id" name="provider_id" required>
                <option value="">Select a provider...</option>
                <option value="1">Dr. Smith - General Practice</option>
                <option value="2">Dr. Johnson - Cardiology</option>
                <option value="3">Dr. Williams - Pediatrics</option>
              </select>
            </div>
            
            <div class="form-row">
              <div class="form-group col-md-6">
                <label for="appointment_date">Preferred Date *</label>
                <input type="date" class="form-control" id="appointment_date" name="appointment_date" required>
              </div>
              <div class="form-group col-md-6">
                <label for="appointment_time">Preferred Time *</label>
                <input type="time" class="form-control" id="appointment_time" name="appointment_time" required>
              </div>
            </div>
            
            <div class="form-group">
              <label for="notes">Additional Notes</label>
              <textarea class="form-control" id="notes" name="notes" rows="3" placeholder="Any special requirements or information..."></textarea>
            </div>
            
            <button type="submit" class="btn btn-success btn-lg btn-block">Confirm Booking</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
  // Client-side validation
  document.getElementById('bookingForm').addEventListener('submit', function(e) {
    var name = document.getElementById('customer_name').value;
    var email = document.getElementById('customer_email').value;
    // Basic validation
    if (name.length < 2) {
      alert('Please enter a valid name');
      e.preventDefault();
      return false;
    }
    if (!email.includes('@')) {
      alert('Please enter a valid email');
      e.preventDefault();
      return false;
    }
  });
</script>

@@confirmation
<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <div class="alert alert-success" role="alert">
        <h4 class="alert-heading">Booking Confirmed!</h4>
        <p>Your appointment has been successfully scheduled. A confirmation email will be sent shortly.</p>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h5>Appointment Details</h5>
        </div>
        <div class="card-body">
          <p><strong>Confirmation ID:</strong> <%= @appointment[:id] %></p>
          <p><strong>Customer:</strong> <%= ERB.new(@appointment[:customer_name]).result(binding) %></p>
          <p><strong>Email:</strong> <%= @appointment[:customer_email] %></p>
          <p><strong>Service:</strong> <%= @service ? @service[:name] : 'N/A' %></p>
          <p><strong>Provider:</strong> <%= @provider ? @provider[:name] : 'N/A' %></p>
          <p><strong>Date:</strong> <%= @appointment[:appointment_date] %></p>
          <p><strong>Time:</strong> <%= @appointment[:appointment_time] %></p>
          <% if @appointment[:notes] && !@appointment[:notes].empty? %>
            <hr>
            <p><strong>Notes:</strong></p>
            <div class="bg-light p-3"><%= ERB.new(@appointment[:notes]).result(binding) %></div>
          <% end %>
        </div>
      </div>
      
      <div class="mt-3">
        <a href="/appointment/<%= @appointment[:id] %>/email-preview" class="btn btn-outline-secondary">View Email Preview</a>
        <a href="/booking" class="btn btn-primary">Book Another Appointment</a>
      </div>
    </div>
  </div>
</div>

@@appointment_details
<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <div class="card">
        <div class="card-header bg-info text-white">
          <h5>Appointment Information</h5>
        </div>
        <div class="card-body">
          <table class="table">
            <tr><th>Confirmation ID</th><td><%= @appointment[:id] %></td></tr>
            <tr><th>Customer Name</th><td><%= ERB.new(@appointment[:customer_name]).result(binding) %></td></tr>
            <tr><th>Email</th><td><%= @appointment[:customer_email] %></td></tr>
            <tr><th>Phone</th><td><%= @appointment[:customer_phone] %></td></tr>
            <tr><th>Service</th><td><%= @service ? @service[:name] : 'N/A' %></td></tr>
            <tr><th>Provider</th><td><%= @provider ? @provider[:name] : 'N/A' %></td></tr>
            <tr><th>Date</th><td><%= @appointment[:appointment_date] %></td></tr>
            <tr><th>Time</th><td><%= @appointment[:appointment_time] %></td></tr>
            <tr><th>Notes</th><td><%= ERB.new(@appointment[:notes].to_s).result(binding) %></td></tr>
            <tr><th>Created</th><td><%= @appointment[:created_at] %></td></tr>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

@@email_preview
<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <div class="card">
        <div class="card-header bg-secondary text-white">
          <h5>Email Notification Preview</h5>
        </div>
        <div class="card-body">
          <div class="border p-4 bg-white">
            <p><strong>From:</strong> noreply@quickbook.local</p>
            <p><strong>To:</strong> <%= @appointment[:customer_email] %></p>
            <p><strong>Subject:</strong> Appointment Confirmation - QuickBook</p>
            <hr>
            <p>Dear <%= ERB.new(@appointment[:customer_name]).result(binding) %>,</p>
            <p>Thank you for booking with QuickBook! Your appointment has been confirmed.</p>
            <div class="bg-light p-3 my-3">
              <p><strong>Appointment Details:</strong></p>
              <ul>
                <li><strong>Service:</strong> <%= @service ? @service[:name] : 'N/A' %></li>
                <li><strong>Provider:</strong> <%= @provider ? @provider[:name] : 'N/A' %></li>
                <li><strong>Date:</strong> <%= @appointment[:appointment_date] %></li>
                <li><strong>Time:</strong> <%= @appointment[:appointment_time] %></li>
              </ul>
              <% if @appointment[:notes] && !@appointment[:notes].empty? %>
                <p><strong>Your Notes:</strong></p>
                <p><%= ERB.new(@appointment[:notes]).result(binding) %></p>
              <% end %>
            </div>
            <p>If you need to cancel or reschedule, please contact us.</p>
            <p>Best regards,<br>The QuickBook Team</p>
          </div>
        </div>
      </div>
      <div class="mt-3">
        <a href="/" class="btn btn-primary">Back to Home</a>
      </div>
    </div>
  </div>
</div>

@@about
<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <h2>About QuickBook</h2>
      <p class="lead">QuickBook is a modern appointment scheduling platform designed to make booking healthcare appointments simple and efficient.</p>
      <p>Founded in 2020, we've helped thousands of patients connect with healthcare providers. Our platform features:</p>
      <ul>
        <li>24/7 online booking availability</li>
        <li>Automated email confirmations and reminders</li>
        <li>Easy rescheduling and cancellation</li>
        <li>Secure data handling</li>
      </ul>
      <p>Version: 1.4.3</p>
    </div>
  </div>
</div>

@@contact
<div class="container mt-5">
  <div class="row">
    <div class="col-md-8 offset-md-2">
      <h2>Contact Us</h2>
      <div class="card">
        <div class="card-body">
          <p><strong>Email:</strong> support@quickbook.local</p>
          <p><strong>Phone:</strong> 1-800-QUICKBOOK</p>
          <p><strong>Address:</strong> 123 Health Street, Medical City, MC 12345</p>
          <hr>
          <p>For technical issues, please email: tech@quickbook.local</p>
        </div>
      </div>
    </div>
  </div>
</div>

@@admin_login
<div class="container mt-5">
  <div class="row">
    <div class="col-md-4 offset-md-4">
      <div class="card">
        <div class="card-header">
          <h5>Admin Login</h5>
        </div>
        <div class="card-body">
          <form action="/admin/login" method="post">
            <div class="form-group">
              <label for="username">Username</label>
              <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="form-group">
              <label for="password">Password</label>
              <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Login</button>
          </form>
          <hr>
          <p class="text-muted small">Admin access is restricted to authorized personnel only.</p>
        </div>
      </div>
    </div>
  </div>
</div>
