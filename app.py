from flask import Flask, request, render_template_string
import re
import dns.resolver
import smtplib
import socket

app = Flask(__name__)

# HTML template for the home page with Bootstrap styling
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Validator</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h3 class="mb-0">Email Verification</h3>
                    </div>
                    <div class="card-body">
                        <form method="post">
                            <div class="form-group">
                                <label for="email">Enter your email:</label>
                                <input type="text" class="form-control" id="email" name="email">
                            </div>
                            <button type="submit" class="btn btn-primary">Verify Email</button>
                            <button type="button" class="btn btn-secondary" onclick="window.location.href='/retry'">Try Again</button>
                        </form>
                        {% if result %}
                            <div class="mt-3 alert alert-{{ result_class }}" role="alert">
                                <strong>Result:</strong> {{ result }}
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/', methods=['POST'])
def verify_email():
    email = request.form['email']
    is_valid, message = validate_email(email)
    result_class = "success" if is_valid else "danger"
    return render_template_string(HTML_TEMPLATE, result=message, result_class=result_class)

@app.route('/', methods=['GET'])
def retry():
    return render_template_string(HTML_TEMPLATE)

def validate_email(email):
    regex = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if not re.search(regex, email):
        return False, "Invalid email syntax."
    domain = email.split('@')[1]
    dns_servers = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220', '64.6.64.6', '64.6.65.6', '77.88.8.8', '77.88.8.1', '84.200.69.80', '84.200.70.40', '8.26.56.26', '8.20.247.20', '195.46.39.39', '195.46.39.40', '69.195.152.204', '23.94.60.240', '74.82.42.42']
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 10
    resolver.timeout = 5
    for server in dns_servers:
        resolver.nameservers = [server]
        try:
            mx_records = resolver.resolve(domain, 'MX')
            mx_record = str(mx_records[0].exchange)
            break
        except Exception:
            continue
    else:
        return False, "MX record not found across all DNS servers."
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('you@example.com')
        code, message = server.rcpt(email)
        server.quit()
        if code == 250:
            return True, "Email is valid and exists."
        else:
            return False, "Email does not exist."
    except (socket.gaierror, socket.error, socket.herror, smtplib.SMTPException):
        return False, "Failed to connect to the email server."

if __name__ == '__main__':
    app.run(debug=True)
