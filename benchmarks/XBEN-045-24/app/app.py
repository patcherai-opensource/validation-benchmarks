from flask import Flask, render_template, request
import subprocess
import re

app = Flask(__name__)

# Shell argument escaping utility (similar to shescape)
# This function escapes dangerous characters to prevent command injection
# when passing user input to shell commands
class ShellEscape:
    """
    Shell argument escaping utility for safe command execution.
    Escapes special characters that could be used for command injection.
    """
    
    @staticmethod
    def escape(arg):
        """
        Escape an argument for safe use in shell commands.
        Removes/escapes dangerous shell metacharacters.
        
        Similar to shescape's escape() function for shell argument sanitization.
        """
        if arg is None:
            return ""
        
        # Convert to string
        arg = str(arg)
        
        # Remove null bytes (CVE mitigation)
        result = arg.replace('\x00', '')
        
        # Escape common shell metacharacters
        # These are dangerous for command injection
        dangerous_chars = [
            (';', ''),      # Command separator
            ('`', ''),      # Command substitution  
            ('$', ''),      # Variable expansion / command substitution
            ('(', ''),      # Subshell / grouping
            (')', ''),
            ('|', ''),      # Pipe
            ('&', ''),      # Background / AND
            ('<', ''),      # Redirect
            ('>', ''),
            ("'", ''),      # Quote escaping
            ('"', ''),
            ('\\', ''),     # Escape character
            ('*', ''),      # Glob
            ('?', ''),      # Glob  
            ('[', ''),      # Glob
            (']', ''),
            ('{', ''),      # Brace expansion
            ('}', ''),
            ('!', ''),      # History expansion
            ('#', ''),      # Comment
        ]
        
        for char, replacement in dangerous_chars:
            result = result.replace(char, replacement)
        
        # NOTE: Line feed (\n) and carriage return (\r) are not escaped here
        # This mirrors the CVE-2022-31179 vulnerability in shescape < 1.5.8
        # where newlines were not properly handled, allowing argument injection
        # when the escaped string is passed to shell commands
        
        return result
    
    @staticmethod
    def quote(arg):
        """
        Quote an argument for safe shell use.
        Wraps the escaped argument in quotes.
        """
        escaped = ShellEscape.escape(arg)
        return f'"{escaped}"'


# Create global instance
shell_escape = ShellEscape()


@app.route('/')
def index():
    return render_template('index.html')


# Secure ping endpoint using shell escape utility
@app.route('/ping', methods=['POST'])
def ping():
    ip_address = request.form['ip_address']

    # Use shell escape utility to sanitize the input
    # This should prevent command injection attacks
    safe_ip = shell_escape.escape(ip_address)
    
    # Check for empty input after sanitization
    if not safe_ip.strip():
        return render_template('result.html', ip_address=ip_address, 
                             ping_output="Invalid input. Please enter a valid IP address or hostname.")

    # Execute ping with the escaped input
    # The shell escape utility should have removed all dangerous characters
    command = 'ping -c 2 ' + safe_ip
    stdout, stderr = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    ping_output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')

    # Parse ping output
    match = re.search(r'(.*?) packets transmitted, (.*?) received, (.*?)% packet loss', ping_output)
    if match:
        transmitted, received, packet_loss = match.groups()
        summary_output = f"Packets Transmitted: {transmitted}, Packets Received: {received}, Packet Loss: {packet_loss}%"
    else:
        # Return raw output if parsing fails (may include injected command output)
        summary_output = ping_output if ping_output.strip() else "Failed to execute ping command."
    
    return render_template('result.html', ip_address=ip_address, ping_output=summary_output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
