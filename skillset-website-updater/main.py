from flask import Flask, jsonify, request, Response
import json
import sys, os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import utils.github_utils as github_utils
from utils.log_utils import *
from app import WebPage


logger = configure_logger(with_date_folder=False)
logger.info('-----------------Starting-----------------')

app = Flask(__name__)

webapp = WebPage()

@app.route('/', methods=['GET'])
def default():
    logger.info(f"Route: /")
    github_handler = github_utils.GitHubHandler(request)
    return f"""
    <html>
        <head>
            <title>Default Page</title>
        </head>
        <body>
            <h1>Status: OK</h1>
            <p>Demos:</p>
            <ul>
                <li><a href="{github_handler.request_url}/skillset">Skillset</a></li>
            </ul>
        </body>
    </html>
    """


@app.route('/skillset', methods=['GET'])
def skillset():
    logger.info(f"Route: /skillset")
    return webapp.generate_html()

@app.route('/color', methods=['GET', 'POST'])
def color():

    if request.method == 'POST':
        github_handler = github_utils.GitHubHandler(request)
        if not github_handler.verify_github_signature():
            return jsonify({"error": "Request must be from GitHub"}), 403

        user_login = github_handler.get_user_login()
        post_data = json.loads(request.data)
        hex_color = post_data.get('hex_color', '#FFFFFF')
        webapp.color(hex_color)
        logger.info(f"Route: /color, User: {user_login} set Color: {hex_color}")
        
        message = f'Color updated to {hex_color}, you must visit {github_handler.request_url} to see it!'
        return Response(f"data: {message}\n\n", 
                       headers={"Content-Type": "text/event-stream"})
        
    return jsonify({"status": "ok"})


@app.route('/text', methods=['GET', 'POST'])
def text():

    if request.method == 'POST':
        github_handler = github_utils.GitHubHandler(request)
        if not github_handler.verify_github_signature():
            return jsonify({"error": "Request must be from GitHub"}), 403

        user_login = github_handler.get_user_login()
        post_data = json.loads(request.data)
        content= post_data.get('content', 'Hello, World!')
        size = post_data.get('size', 48)
        webapp.text(f"{user_login}: {content}", size)
        logger.info(f"Route: /text, User: {user_login} set Text: {content}, Size: {size}")
        
        message = f'Text updated to {content}, Size: {size}, you must visit {github_handler.request_url} to see it!'
        return Response(f"data: {message}\n\n", 
                       headers={"Content-Type": "text/event-stream"})
    
    return jsonify({"status": "ok"})


@app.route('/query', methods=['GET', 'POST'])
def query():

    if request.method == 'POST':
        github_handler = github_utils.GitHubHandler(request)
        if not github_handler.verify_github_signature():
            return jsonify({"error": "Request must be from GitHub"}), 403

        user_login = github_handler.get_user_login()
        post_data = json.loads(request.data)
        logger.info(f"Route: /query, User: {user_login} post_data: {post_data}")
        
        message = """
# Create Your Own Skillset

## Key Features

- This repo can [verify that payloads are coming from GitHub](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-agent-for-your-copilot-extension/configuring-your-copilot-agent-to-communicate-with-github#verifying-that-payloads-are-coming-from-github), will protect your backend's security and privacy.
- Get information about the GitHub user who called this Skillset.

## Deploy Backend Service


### Source Code Mode

1. Download source code
   ```bash
   git clone https://github.com/satomic/copilot-funny-extensions.git
   cd skillset-website-updater
   ```
2. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
3. Run
   ```bash
   python3 main.py
   ```
4. Publish this service, it should be [publicly accessible via HTTPS](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension/building-copilot-skillsets#prerequisites). The easiest way is using **VSCode Ports Forwarding** (you can use anyway you like). Remember set the **Visibility** to **Public**.

   ![](/image/image_HnzGovKRNF.png)

### Docker Mode

1. Download source code in to a Linux with docker installed.
2. Build docker
   ```bash
   bash docker_build.sh
   ```
3. Run docker (I published my docker image `satomic/skillset` already, you can just use it directly).
   ```bash
   docker run -itd \
   --net=host \
   --restart=always \
   --name skillset \
   -v /srv/skillset-logs:/app/logs \
   satomic/skillset # change this to your own image
   ```
4. You need to fix the HTTPS problem by yourself 🙂. Because backend service should be [publicly accessible via HTTPS](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension/building-copilot-skillsets#prerequisites)."""
        return Response(f"data: {message}\n\n", 
                       headers={"Content-Type": "text/event-stream"})
    
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)