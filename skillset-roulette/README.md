# Roulette Play

| **Version** | **Update Notes** | **Date** |
| ----------- | ---------------- | -------- |
| 1.0    | create           | 20250112 |
| 1.1    | update doc       | 20250113 |

# Table of contents
- [Why Built This](#why-built-this)
- [Quick Try](#quick-try)
- [Create Your Own Extension](#create-your-own-extension)
   - [Deploy Backend Service](#deploy-backend-service)
      - [Source Code Mode](#source-code-mode)
      - [Docker Mode](#docker-mode)
   - [Create GitHub App & Following Steps](#create-github-app--following-steps)
      - [Copilot](#copilot)
      - [Try Your Own Extension](#try-your-own-extension)


# Why Built This
From a management perspective
- The purpose of this extension is for **GitHub Copilot administrators to promote Copilot Chat and Extensions within their company**.
- When you install this GitHub App in your GitHub Organization, users in the Organization can play this game and have chances to win prizes!! 🎉🎉🎉 (each GitHub user can only play for one time).
- So as a GitHub Copilot administrator, you can use this extension to **encourage users to use Copilot Chat and Extensions**, not only code completion.

From technically perspective
- This program is a web-based roulette application built with Flask. It presents users with an interactive spinning wheel and displays real-time results using Server-Sent Events (SSE). 
- When a user plays, the app logs winners in a history file and shows them in the interface. 
- Each prize is assigned a weight, and the system uses those probabilities for every spin. 


# Quick Try
- I've created a public GitHub App [**Roulette Play**](https://github.com/apps/roulette-play) based on this project that you can install in your account and try it out. You can refer to [Website Updater Quick Try](https://github.com/satomic/copilot-funny-extensions/tree/main/skillset-website-updater#quick-try) to set it up, it is almost exactly the same.
- Visit online [**Roulette Play**](https://demo.softrin.com/roulette).
- In GitHub Copilot Chat, `@roulette-play` say something like `I want to play the developer's roulette game` to start the game.
  ![](/image/roulette.gif)

# Create Your Own Extension

## Deploy Backend Service

### Source Code Mode

1. Download source code
   ```bash
   git clone https://github.com/satomic/copilot-funny-extensions.git
   cd skillset-roulette
   ```
1. Set your own configurations in `prizes.json`
   - key: the name of the prize
   - `color`: the color of the prize
   - `index`: The winning index of a specific prize, for example, with the following configuration, the probability of winning Banana is `2/(1+2+3+4+10)*100% = 10%`
   ```json
   {
        "Apple": { "color": "#FFA500", "index": 1 },
        "Banana": { "color": "#FF4500", "index": 2 },
        "Cherry": { "color": "#FFD700", "index": 3 },
        "Durian": { "color": "#7FFF00", "index": 4 },
        "thanks": { "color": "#1E90FF", "index": 10 }
   }
   ```
   Based on this configuration, the resulting Roulette is
   ![](/image/roulette.png)
1. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
1. Set environment variables (Optional)
   - `VERIFY_REQUEST_FROM_GITHUB`: for debug use, when set to `True`, the request from GitHub will be verified, otherwise, it will not be verified, then you can use `curl` to send requests to the backend service directly.
        ```bash
        curl -X POST http://127.0.0.1:8082/play -H "Content-Type: application/json" -d '{"name": "player1"}'
        ```
   - `DEBUG_USERS`: for debug use, the user setted here can play the game for multiple times

   Set environment variables
   - Windows
        ```PowerShell
        $Env:VERIFY_REQUEST_FROM_GITHUB="True" # default is True
        $Env:DEBUG_USERS="your_github_id" # default is satomic
        ```
   - Linux/Mac
        ```bash
        export VERIFY_REQUEST_FROM_GITHUB="True" # default is True
        export DEBUG_USERS="your_github_id" # default is satomic
        ```
1. Run
   ```bash
   python3 main.py
   ```
1. Publish this service, it should be [publicly accessible via HTTPS](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension/building-copilot-skillsets#prerequisites). The easiest way is using **VSCode Ports Forwarding** (you can use anyway you like). Remember set the **Visibility** to **Public**.

   ![](/image/8082-port-forwarding.png)

### Docker Mode

1. Download source code in to a Linux with docker installed.
1. Set your own configurations in `prizes.json`.
1. Build docker
   ```bash
   bash docker_build.sh
   ```
1. Run docker (I published my docker image `satomic/roulette` already, you can just use it directly).
   ```bash
   docker run -itd \
    --net=host \
    --restart=always \
    --name roulette \
    -v /srv/roulette-logs:/app/logs \
    -e VERIFY_REQUEST_FROM_GITHUB=True \
    -e DEBUG_USERS=your_github_id \
   satomic/roulette # change this to your own image
   ```
1. You need to fix the HTTPS problem by yourself 🙂. Because backend service should be [publicly accessible via HTTPS](https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-skillset-for-your-copilot-extension/building-copilot-skillsets#prerequisites).

## Create GitHub App & Following Steps
You can refer to [Create GitHub App](https://github.com/satomic/copilot-funny-extensions/tree/main/skillset-website-updater#Create-GitHub-App) to set it up, it is almost exactly the same. The only differences are the following:

### Copilot
1. **Skill definitions**
   1. **message**
      - Name: `message`
      - Inference description: `the message that user send to the extension, to be used for play a game for developers, and tell the participants the results of the game.`
      - URL: you need to use your own URL, if you are using VSCode Ports Forwarding, it should be like `https://2npk0g6z-8081.asse.devtunnels.ms/play`
      - Parameters:
      ```json
      {
          "type": "object",
          "properties": {
              "message ": {
              "type": "string",
              "description": "the original message that user send to the extension, to be used for play a game for developers"
              }
          }
      }
      ```

### Try Your Own Extension
1. Check your own website. If you use VSCode Ports Forwarding, it should be like `https://2npk0g6z-8082.asse.devtunnels.ms`.
2. In GitHub Copilot Chat, `@YOUR_EXTENSION_NAME` say something like `I want to play the developer's roulette game` to start the game.
  ![](/image/roulette.gif)
