import re
from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)

# A basic interpreter for Flo
class FloInterpreter:
    def __init__(self):
        self.variables = {}

    def parse(self, code):
        lines = code.strip().split('\n')
        output = []
        for line in lines:
            line = line.strip()
            if line.startswith("print"):
                output.append(self.handle_print(line))
            elif "=" in line:
                self.handle_assignment(line)
            else:
                output.append(f"Unknown command: {line}")
        return "\n".join(output)

    def handle_print(self, line):
        match = re.match(r"print\s+(.+)", line)
        if match:
            expression = match.group(1)
            try:
                result = eval(expression, {}, self.variables)
                return str(result)
            except Exception as e:
                return f"Error: {e}"
        else:
            return "Syntax error in print statement"

    def handle_assignment(self, line):
        match = re.match(r"(\w+)\s*=\s*(.+)", line)
        if match:
            var_name = match.group(1)
            value = eval(match.group(2), {}, self.variables)
            self.variables[var_name] = value

# Function to process .flo files and execute Flo code
def process_flo_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        
    # Define a pattern to match Flo code inside <?flo ... ?>
    flo_code_pattern = re.compile(r"<\?flo(.*?)\?>", re.DOTALL)
    
    interpreter = FloInterpreter()

    # Function to replace each Flo block with its output
    def execute_flo(match):
        flo_code = match.group(1).strip()
        result = interpreter.parse(flo_code)
        return result
    
    # Replace all Flo code blocks with their interpreted output
    processed_content = re.sub(flo_code_pattern, execute_flo, content)
    return processed_content

# Route to serve .flo files as HTML after processing Flo code
@app.route('/<path:filename>')
def serve_flo_file(filename):
    if filename.endswith('.flo'):
        try:
            file_path = os.path.join('templates', filename)
            rendered_content = process_flo_file(file_path)
            return rendered_content, 200, {'Content-Type': 'text/html'}
        except Exception as e:
            return f"Error processing Flo file: {e}", 500
    else:
        return send_from_directory('templates', filename)

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
