require 'sinatra'
require 'erb'
require 'json'
require 'securerandom'

set :bind, '0.0.0.0'
set :show_exceptions, false
set :raise_errors, false

appointments = []
services = [
  { id: 1, name: 'General Consultation', duration: 30, price: 50 },
  { id: 2, name: 'Dental Checkup', duration: 45, price: 75 },
  { id: 3, name: 'Physical Therapy', duration: 60, price: 100 },
  { id: 4, name: 'Eye Examination', duration: 30, price: 60 }
]

providers = [
  { id: 1, name: 'Dr. Sarah Johnson', specialty: 'General Practice' },
  { id: 2, name: 'Dr. Michael Chen', specialty: 'Dentistry' },
  { id: 3, name: 'Dr. Emily Rodriguez', specialty: 'Physical Therapy' },
  { id: 4, name: 'Dr. James Wilson', specialty: 'Optometry' }
]

error 500 do
  'An error occurred. Please try again later.'
end

error 404 do
  'Page not found.'
end

get '/' do
  erb :index
end

get '/booking' do
  @services = services
  @providers = providers
  erb :booking
end

post '/booking' do
  first_name = params[:first_name] || ''
  last_name = params[:last_name] || ''
  email = params[:email] || ''
  phone = params[:phone] || ''
  service_id = params[:service_id].to_i
  provider_id = params[:provider_id].to_i
  appointment_date = params[:appointment_date] || ''
  appointment_time = params[:appointment_time] || ''
  notes = params[:notes] || ''

  service = services.find { |s| s[:id] == service_id }
  provider = providers.find { |p| p[:id] == provider_id }

  appointment = {
    id: SecureRandom.hex(8),
    first_name: first_name,
    last_name: last_name,
    email: email,
    phone: phone,
    service: service,
    provider: provider,
    date: appointment_date,
    time: appointment_time,
    notes: notes,
    created_at: Time.now
  }

  appointments << appointment

  @appointment = appointment
  erb :confirmation
end

get '/appointments/:id' do
  @appointment = appointments.find { |a| a[:id] == params[:id] }
  if @appointment
    erb :appointment_details
  else
    status 404
    'Appointment not found'
  end
end

get '/api/services' do
  content_type :json
  services.to_json
end

get '/api/providers' do
  content_type :json
  providers.to_json
end

__END__

@@index
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <title>QuickBook Appointments</title>
  <style>
    .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; }
    .feature-icon { font-size: 3rem; color: #667eea; margin-bottom: 1rem; }
    .card-service { transition: transform 0.3s; }
    .card-service:hover { transform: translateY(-5px); }
  </style>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #667eea;">
    <a class="navbar-brand" href="/"><i class="fas fa-calendar-check"></i> QuickBook</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ml-auto">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="/booking">Book Now</a></li>
      </ul>
    </div>
  </nav>

  <section class="hero-section text-center">
    <div class="container">
      <h1 class="display-4">Easy Online Appointment Booking</h1>
      <p class="lead">Schedule your appointments with our healthcare professionals in just a few clicks</p>
      <a href="/booking" class="btn btn-light btn-lg mt-3"><i class="fas fa-calendar-plus"></i> Book an Appointment</a>
    </div>
  </section>

  <section class="py-5">
    <div class="container">
      <h2 class="text-center mb-5">Our Services</h2>
      <div class="row">
        <div class="col-md-3 mb-4">
          <div class="card card-service h-100 text-center">
            <div class="card-body">
              <i class="fas fa-stethoscope feature-icon"></i>
              <h5 class="card-title">General Consultation</h5>
              <p class="card-text">Comprehensive health checkups and consultations</p>
              <p class="text-muted">30 min - $50</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card card-service h-100 text-center">
            <div class="card-body">
              <i class="fas fa-tooth feature-icon"></i>
              <h5 class="card-title">Dental Checkup</h5>
              <p class="card-text">Complete dental examination and cleaning</p>
              <p class="text-muted">45 min - $75</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card card-service h-100 text-center">
            <div class="card-body">
              <i class="fas fa-running feature-icon"></i>
              <h5 class="card-title">Physical Therapy</h5>
              <p class="card-text">Rehabilitation and recovery sessions</p>
              <p class="text-muted">60 min - $100</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card card-service h-100 text-center">
            <div class="card-body">
              <i class="fas fa-eye feature-icon"></i>
              <h5 class="card-title">Eye Examination</h5>
              <p class="card-text">Complete vision testing and assessment</p>
              <p class="text-muted">30 min - $60</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="bg-light py-5">
    <div class="container">
      <h2 class="text-center mb-5">Why Choose Us?</h2>
      <div class="row">
        <div class="col-md-4 text-center">
          <i class="fas fa-clock feature-icon"></i>
          <h5>Easy Scheduling</h5>
          <p>Book appointments online 24/7 at your convenience</p>
        </div>
        <div class="col-md-4 text-center">
          <i class="fas fa-user-md feature-icon"></i>
          <h5>Expert Providers</h5>
          <p>Experienced healthcare professionals</p>
        </div>
        <div class="col-md-4 text-center">
          <i class="fas fa-bell feature-icon"></i>
          <h5>Reminders</h5>
          <p>Email confirmations and reminders</p>
        </div>
      </div>
    </div>
  </section>

  <footer class="bg-dark text-white py-4">
    <div class="container text-center">
      <p class="mb-0">&copy; 2024 QuickBook Appointments. All rights reserved.</p>
    </div>
  </footer>

  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>

@@booking
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <title>Book Appointment - QuickBook</title>
  <style>
    .booking-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 0; }
  </style>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #667eea;">
    <a class="navbar-brand" href="/"><i class="fas fa-calendar-check"></i> QuickBook</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ml-auto">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item active"><a class="nav-link" href="/booking">Book Now</a></li>
      </ul>
    </div>
  </nav>

  <section class="booking-header text-center">
    <h2><i class="fas fa-calendar-plus"></i> Book Your Appointment</h2>
    <p>Fill out the form below to schedule your appointment</p>
  </section>

  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-body">
            <form action="/booking" method="post" id="bookingForm">
              <h5 class="mb-4"><i class="fas fa-user"></i> Personal Information</h5>
              <div class="form-row">
                <div class="form-group col-md-6">
                  <label for="first_name">First Name *</label>
                  <input type="text" class="form-control" id="first_name" name="first_name" required>
                </div>
                <div class="form-group col-md-6">
                  <label for="last_name">Last Name *</label>
                  <input type="text" class="form-control" id="last_name" name="last_name" required>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group col-md-6">
                  <label for="email">Email *</label>
                  <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="form-group col-md-6">
                  <label for="phone">Phone</label>
                  <input type="tel" class="form-control" id="phone" name="phone">
                </div>
              </div>

              <hr class="my-4">
              <h5 class="mb-4"><i class="fas fa-calendar"></i> Appointment Details</h5>
              
              <div class="form-group">
                <label for="service_id">Service *</label>
                <select class="form-control" id="service_id" name="service_id" required>
                  <option value="">Select a service...</option>
                  <% @services.each do |service| %>
                    <option value="<%= service[:id] %>"><%= service[:name] %> - <%= service[:duration] %> min ($<%= service[:price] %>)</option>
                  <% end %>
                </select>
              </div>

              <div class="form-group">
                <label for="provider_id">Provider *</label>
                <select class="form-control" id="provider_id" name="provider_id" required>
                  <option value="">Select a provider...</option>
                  <% @providers.each do |provider| %>
                    <option value="<%= provider[:id] %>"><%= provider[:name] %> - <%= provider[:specialty] %></option>
                  <% end %>
                </select>
              </div>

              <div class="form-row">
                <div class="form-group col-md-6">
                  <label for="appointment_date">Date *</label>
                  <input type="date" class="form-control" id="appointment_date" name="appointment_date" required>
                </div>
                <div class="form-group col-md-6">
                  <label for="appointment_time">Time *</label>
                  <select class="form-control" id="appointment_time" name="appointment_time" required>
                    <option value="">Select time...</option>
                    <option value="09:00">9:00 AM</option>
                    <option value="09:30">9:30 AM</option>
                    <option value="10:00">10:00 AM</option>
                    <option value="10:30">10:30 AM</option>
                    <option value="11:00">11:00 AM</option>
                    <option value="11:30">11:30 AM</option>
                    <option value="13:00">1:00 PM</option>
                    <option value="13:30">1:30 PM</option>
                    <option value="14:00">2:00 PM</option>
                    <option value="14:30">2:30 PM</option>
                    <option value="15:00">3:00 PM</option>
                    <option value="15:30">3:30 PM</option>
                    <option value="16:00">4:00 PM</option>
                    <option value="16:30">4:30 PM</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label for="notes">Additional Notes</label>
                <textarea class="form-control" id="notes" name="notes" rows="3" placeholder="Any additional information or special requests..."></textarea>
              </div>

              <button type="submit" class="btn btn-primary btn-lg btn-block">
                <i class="fas fa-check"></i> Confirm Booking
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer class="bg-dark text-white py-4">
    <div class="container text-center">
      <p class="mb-0">&copy; 2024 QuickBook Appointments. All rights reserved.</p>
    </div>
  </footer>

  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  <script>
    document.getElementById('appointment_date').min = new Date().toISOString().split('T')[0];
  </script>
</body>
</html>

@@confirmation
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <title>Booking Confirmed - QuickBook</title>
  <style>
    .confirmation-header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 40px 0; }
  </style>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #667eea;">
    <a class="navbar-brand" href="/"><i class="fas fa-calendar-check"></i> QuickBook</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ml-auto">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="/booking">Book Now</a></li>
      </ul>
    </div>
  </nav>

  <section class="confirmation-header text-center">
    <h2><i class="fas fa-check-circle"></i> Booking Confirmed!</h2>
    <p>Your appointment has been successfully scheduled</p>
  </section>

  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0"><i class="fas fa-calendar-check"></i> Appointment Details</h5>
          </div>
          <div class="card-body">
            <div class="row mb-3">
              <div class="col-sm-4"><strong>Confirmation #:</strong></div>
              <div class="col-sm-8"><%= @appointment[:id] %></div>
            </div>
            <hr>
            <h6 class="text-muted mb-3">Customer Information</h6>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Name:</strong></div>
              <div class="col-sm-8"><%= ERB.new(@appointment[:first_name]).result(binding) %> <%= ERB.new(@appointment[:last_name]).result(binding) %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Email:</strong></div>
              <div class="col-sm-8"><%= ERB.new(@appointment[:email]).result(binding) %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Phone:</strong></div>
              <div class="col-sm-8"><%= ERB.new(@appointment[:phone]).result(binding) %></div>
            </div>
            <hr>
            <h6 class="text-muted mb-3">Appointment Information</h6>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Service:</strong></div>
              <div class="col-sm-8"><%= @appointment[:service] ? @appointment[:service][:name] : 'N/A' %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Provider:</strong></div>
              <div class="col-sm-8"><%= @appointment[:provider] ? @appointment[:provider][:name] : 'N/A' %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Date:</strong></div>
              <div class="col-sm-8"><%= @appointment[:date] %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Time:</strong></div>
              <div class="col-sm-8"><%= @appointment[:time] %></div>
            </div>
            <% if @appointment[:notes] && !@appointment[:notes].empty? %>
            <hr>
            <h6 class="text-muted mb-3">Additional Notes</h6>
            <div class="p-3 bg-light rounded">
              <%= ERB.new(@appointment[:notes]).result(binding) %>
            </div>
            <% end %>
          </div>
          <div class="card-footer text-muted">
            <small>A confirmation email has been sent to your email address.</small>
          </div>
        </div>
        <div class="text-center mt-4">
          <a href="/" class="btn btn-primary"><i class="fas fa-home"></i> Return Home</a>
          <a href="/booking" class="btn btn-outline-primary"><i class="fas fa-calendar-plus"></i> Book Another</a>
        </div>
      </div>
    </div>
  </div>

  <footer class="bg-dark text-white py-4 mt-5">
    <div class="container text-center">
      <p class="mb-0">&copy; 2024 QuickBook Appointments. All rights reserved.</p>
    </div>
  </footer>

  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>

@@appointment_details
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <title>Appointment Details - QuickBook</title>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #667eea;">
    <a class="navbar-brand" href="/"><i class="fas fa-calendar-check"></i> QuickBook</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ml-auto">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="/booking">Book Now</a></li>
      </ul>
    </div>
  </nav>

  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0"><i class="fas fa-calendar"></i> Appointment Details</h5>
          </div>
          <div class="card-body">
            <div class="row mb-3">
              <div class="col-sm-4"><strong>Confirmation #:</strong></div>
              <div class="col-sm-8"><%= @appointment[:id] %></div>
            </div>
            <hr>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Name:</strong></div>
              <div class="col-sm-8"><%= ERB.new(@appointment[:first_name]).result(binding) %> <%= ERB.new(@appointment[:last_name]).result(binding) %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Email:</strong></div>
              <div class="col-sm-8"><%= ERB.new(@appointment[:email]).result(binding) %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Service:</strong></div>
              <div class="col-sm-8"><%= @appointment[:service] ? @appointment[:service][:name] : 'N/A' %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Provider:</strong></div>
              <div class="col-sm-8"><%= @appointment[:provider] ? @appointment[:provider][:name] : 'N/A' %></div>
            </div>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Date & Time:</strong></div>
              <div class="col-sm-8"><%= @appointment[:date] %> at <%= @appointment[:time] %></div>
            </div>
            <% if @appointment[:notes] && !@appointment[:notes].empty? %>
            <hr>
            <div class="row mb-2">
              <div class="col-sm-4"><strong>Notes:</strong></div>
              <div class="col-sm-8"><%= ERB.new(@appointment[:notes]).result(binding) %></div>
            </div>
            <% end %>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer class="bg-dark text-white py-4 mt-5">
    <div class="container text-center">
      <p class="mb-0">&copy; 2024 QuickBook Appointments. All rights reserved.</p>
    </div>
  </footer>

  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
