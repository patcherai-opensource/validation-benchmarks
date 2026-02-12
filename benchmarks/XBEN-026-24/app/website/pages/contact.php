<?php
$submitted = false;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['name'], $_POST['email'], $_POST['message'])) {
    $name = htmlspecialchars(trim($_POST['name']));
    $email = htmlspecialchars(trim($_POST['email']));
    $message = htmlspecialchars(trim($_POST['message']));
    if (!empty($name) && !empty($email) && !empty($message)) {
        $submitted = true;
    }
}
?>
<section class="py-5">
    <div class="container">
        <h2 class="text-center mb-4">Contact Us</h2>
        <div class="row">
            <div class="col-md-6 mx-auto">
                <?php if ($submitted): ?>
                <div class="alert alert-success">
                    Thank you, <?php echo $name; ?>. We've received your message and will get back to you shortly.
                </div>
                <?php endif; ?>
                <form method="POST" action="/?page=contact">
                    <div class="form-group">
                        <label for="name">Name</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="subject">Subject</label>
                        <select class="form-control" id="subject" name="subject">
                            <option>General Inquiry</option>
                            <option>Project Consultation</option>
                            <option>Partnership Opportunity</option>
                            <option>Support Request</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="message">Message</label>
                        <textarea class="form-control" id="message" name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Send Message</button>
                </form>
            </div>
        </div>
        <div class="row mt-5">
            <div class="col-md-4 text-center">
                <h5>Email</h5>
                <p>contact@devcore-solutions.com</p>
            </div>
            <div class="col-md-4 text-center">
                <h5>Phone</h5>
                <p>+1 (555) 234-5678</p>
            </div>
            <div class="col-md-4 text-center">
                <h5>Address</h5>
                <p>742 Innovation Drive, Suite 300<br>San Francisco, CA 94107</p>
            </div>
        </div>
    </div>
</section>
