

class WebPage:
    def __init__(self):
        self.bg_color = "#FFFFFF"  # Default background color is white
        self.content = "Hello, World!"  # Default text
        self.font_size = "48px"  # Default font size
        
    def color(self, hex_color):
        """Update background color using hex color code (#XXXXXX format)"""
        self.bg_color = hex_color
        return self.generate_html()
        
    def text(self, content, size):
        """Update text content and font size"""
        self.content = content
        self.font_size = f"{size}px"
        return self.generate_html()
        
    def generate_html(self):
        """Generate the HTML page with current settings"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            background-color: {self.bg_color};
            margin: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .content {{
            font-family: Arial, sans-serif;
            font-size: {self.font_size};
            color: #000000;
        }}
    </style>
</head>
<body>
    <div class="content">{self.content}</div>
</body>
</html>
"""
        return html

    def save_html(self, filename="index.html"):
        """Save the HTML content to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.generate_html())




if __name__ == '__main__':
    # Create a new WebPage object
    page = WebPage()
    
    # Update the background color and text content
    page.color("#FFA07A")
    page.text("Hello, World!", 100)
    
    # Save the HTML content to a file
    page.save_html("logs/index.html")
    
    print("HTML file generated successfully!")