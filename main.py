from flask import Flask, jsonify, request
import json
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
        return f'Color updated to {hex_color}, you must visit {github_handler.request_url} to see it!'
        
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
        return f'Text updated to {content}, Size: {size}, you must visit {github_handler.request_url} to see it!'
    
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)