require 'sinatra'
require 'erb'
require 'json'
require 'securerandom'

set :bind, '0.0.0.0'

# In-memory storage for appointments
$appointments = []

# Read flag from file (written at startup from env var)
def get_flag
  File.read('/app/flag.txt').strip rescue 'FLAG_NOT_FOUND'
end

get '/' do
  erb :index
end

# Public booking form - no authentication required (like Easy!Appointments public booking)
get '/booking' do
  erb :booking
end

# Submit a new appointment - no authentication required
post '/booking' do
  appointment = {
    id: SecureRandom.hex(8),
    customer_name: params[:customer_name],
    customer_email: params[:customer_email],
    service: params[:service],
    notes: params[:notes],
    date: params[:date],
    time: params[:time],
    created_at: Time.now.to_s
  }
  $appointments << appointment
  @appointment_id = appointment[:id]
  erb :booking_confirmation
end

# View appointment details and generate confirmation email preview
# This endpoint renders stored appointment data through ERB template
# VULNERABLE: User-supplied data from booking form is rendered without escaping
get '/appointment/:id/email_preview' do
  @appointment = $appointments.find { |a| a[:id] == params[:id] }
  halt 404, 'Appointment not found' unless @appointment
  
  # Generate email notification content - renders user data unescaped (vulnerable)
  # Similar to application/views/emails/appointment_saved_email.php in Easy!Appointments
  email_template = <<-TEMPLATE
Dear <%= @appointment[:customer_name] %>,

Thank you for booking an appointment with us!

Appointment Details:
- Service: <%= @appointment[:service] %>
- Date: <%= @appointment[:date] %>
- Time: <%= @appointment[:time] %>

Your Notes: #{@appointment[:notes]}

If you have any questions, please contact us.

Best regards,
Easy Appointments Team
  TEMPLATE
  
  # The vulnerability: user input in 'notes' field is interpolated directly into the template
  # and then processed by ERB, allowing template injection
  begin
    template = ERB.new(email_template)
    @email_content = template.result(binding)
  rescue => e
    @email_content = "Error generating email: #{e.message}"
  end
  
  erb :email_preview
end

# Admin dashboard showing all appointments
get '/admin/appointments' do
  @appointments = $appointments
  erb :admin_appointments
end

__END__

@@index
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Easy Appointments</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <a class="navbar-brand" href="#">Easy Appointments</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="/booking">Book Appointment</a></li>
          <li class="nav-item"><a class="nav-link" href="/admin/appointments">Admin</a></li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="jumbotron">
        <h1 class="display-4">Welcome to Easy Appointments</h1>
        <p class="lead">Book your appointments online quickly and easily.</p>
        <hr class="my-4">
        <p>Click the button below to schedule your next appointment.</p>
        <a class="btn btn-primary btn-lg" href="/booking" role="button">Book Now</a>
      </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@booking
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Book Appointment - Easy Appointments</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <a class="navbar-brand" href="#">Easy Appointments</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
          <li class="nav-item"><a class="nav-link active" href="/booking">Book Appointment</a></li>
          <li class="nav-item"><a class="nav-link" href="/admin/appointments">Admin</a></li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="row">
        <div class="col-md-8 offset-md-2">
          <div class="card">
            <div class="card-header bg-primary text-white">
              <h4>Book an Appointment</h4>
            </div>
            <div class="card-body">
              <form action="/booking" method="post">
                <div class="form-group">
                  <label for="customer_name">Your Name</label>
                  <input type="text" class="form-control" id="customer_name" name="customer_name" required>
                </div>
                <div class="form-group">
                  <label for="customer_email">Email Address</label>
                  <input type="email" class="form-control" id="customer_email" name="customer_email" required>
                </div>
                <div class="form-group">
                  <label for="service">Service</label>
                  <select class="form-control" id="service" name="service" required>
                    <option value="">Select a service...</option>
                    <option value="General Consultation">General Consultation</option>
                    <option value="Follow-up Visit">Follow-up Visit</option>
                    <option value="Specialist Appointment">Specialist Appointment</option>
                  </select>
                </div>
                <div class="form-row">
                  <div class="form-group col-md-6">
                    <label for="date">Preferred Date</label>
                    <input type="date" class="form-control" id="date" name="date" required>
                  </div>
                  <div class="form-group col-md-6">
                    <label for="time">Preferred Time</label>
                    <input type="time" class="form-control" id="time" name="time" required>
                  </div>
                </div>
                <div class="form-group">
                  <label for="notes">Additional Notes</label>
                  <textarea class="form-control" id="notes" name="notes" rows="3" placeholder="Any special requirements or information..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Submit Booking</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@booking_confirmation
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Booking Confirmed - Easy Appointments</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <a class="navbar-brand" href="#">Easy Appointments</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="/booking">Book Appointment</a></li>
          <li class="nav-item"><a class="nav-link" href="/admin/appointments">Admin</a></li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="row">
        <div class="col-md-8 offset-md-2">
          <div class="alert alert-success">
            <h4 class="alert-heading">Booking Confirmed!</h4>
            <p>Your appointment has been successfully booked.</p>
            <hr>
            <p class="mb-0">Appointment ID: <strong><%= @appointment_id %></strong></p>
          </div>
          <div class="card">
            <div class="card-body">
              <p>A confirmation email will be sent to your email address.</p>
              <a href="/appointment/<%= @appointment_id %>/email_preview" class="btn btn-info">Preview Confirmation Email</a>
              <a href="/booking" class="btn btn-primary">Book Another Appointment</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@email_preview
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Email Preview - Easy Appointments</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <a class="navbar-brand" href="#">Easy Appointments</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="/booking">Book Appointment</a></li>
          <li class="nav-item"><a class="nav-link" href="/admin/appointments">Admin</a></li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <div class="row">
        <div class="col-md-10 offset-md-1">
          <div class="card">
            <div class="card-header bg-info text-white">
              <h4>Email Notification Preview</h4>
            </div>
            <div class="card-body">
              <pre class="bg-light p-3" style="white-space: pre-wrap;"><%= @email_content %></pre>
            </div>
          </div>
          <div class="mt-3">
            <a href="/" class="btn btn-primary">Back to Home</a>
          </div>
        </div>
      </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>

@@admin_appointments
<!doctype html>
<html lang="en">
  <head> 
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> 
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Admin - Easy Appointments</title>
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <a class="navbar-brand" href="#">Easy Appointments</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="/booking">Book Appointment</a></li>
          <li class="nav-item"><a class="nav-link active" href="/admin/appointments">Admin</a></li>
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      <h2>All Appointments</h2>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Customer</th>
            <th>Service</th>
            <th>Date</th>
            <th>Time</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <% @appointments.each do |apt| %>
          <tr>
            <td><%= apt[:id] %></td>
            <td><%= apt[:customer_name] %></td>
            <td><%= apt[:service] %></td>
            <td><%= apt[:date] %></td>
            <td><%= apt[:time] %></td>
            <td><a href="/appointment/<%= apt[:id] %>/email_preview" class="btn btn-sm btn-info">Email Preview</a></td>
          </tr>
          <% end %>
        </tbody>
      </table>
      <% if @appointments.empty? %>
      <div class="alert alert-info">No appointments yet.</div>
      <% end %>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>
