

## 30 Second Summary
Imagine asking a single question about a stock and getting back live prices, analyst trends, and a clear summary of what it all means. That is the kind of research assistant we are about to build.  

In this project, we will deploy an AI-powered finance research agent on a local Kubernetes cluster using the kagent framework. Our agent will fetch real-time stock market data from Finnhub and respond with informed analysis powered by Google Gemini.  


## What We'll Build
We'll type a question like "What's the current price of AAPL and how does it compare to MSFT?" into a chat interface, and our agent calls out to Finnhub for live market data, then delivers a structured analysis with real numbers.  

By the end of this project, we'll have:  
• A running AI agent you can chat with through a dashboard or CLI to ask market research questions and get back answers grounded in live data. kagent  
• A custom [MCP](https://theaiengineer.substack.com/p/what-is-mcp) tool server that fetches real-time stock quotes, company profiles, and analyst recommendation trends from Finnhub's API.  
• A fully declarative deployment defined in YAML, with your agent and tool server running as proper Kubernetes workloads with secrets managed securely.  
• Extra Credit: Add a company news analysis tool that lets your agent fetch and summarize the latest headlines for any stock ticker.  

Please note that I'm using my Ubuntu24 machine running in Oracle Virtual Box for this project and I already have an existing Kubernetes cluster deployed using kubeadm with 1 controlplane node and 1 worker node. I'll use my existing Kubernetes cluster instead of Minikube for this project. If you want to install and build your own local Kubernetes cluster using kubeadm from scratch with min specifications inside Oracle Virtual Box, checkout my github repo: [Build-your-local-Kubernetes-cluster](https://github.com/CoyApilado18/Build-your-local-Kubernetes-cluster) Otherwise, follow the steps to install `Minikube` below if you want to launch a Kubernetes cluster out of the box. All commands used in this project are Linux commands. I'll update this repo in the future once I tested this out in Windows.  


## Step 1. Install Docker, Minikube, and Python 

### Install Docker 
You can refer to the official documentation from Docker to install [Docker in Ubuntu](https://docs.docker.com/engine/install/ubuntu/). You may want to checkout `Uninstall old versions` first. As the Docker documentation states, "Your Linux distribution may provide unofficial Docker packages, which may conflict with the official packages provided by Docker. You must uninstall these packages before you install the official version of Docker Engine."  

Here's the official documentation steps installing Docker in Ubuntu and there are different ways to install Docker as the documentation suggests. We'll just follow this step [Install using the apt repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and we should be good to go. 


### Install Python 3
Our agent code and MCP tool server are both written in Python. We need Python 3.10 or later on our `PATH`.

• Most Linux distributions include Python 3. Confirm it is installed, or install it by running:
```bash
sudo apt install python3 python3-pip python3-venv
```

• Verify the install by running:
```bash
python3 --version
```

Confirm all three tools are available in a single check. 
```bash
docker --version && minikube version && python3 --version
```

You should see three version numbers printed one after the other. Each line confirms one of your tools is installed and on your PATH.  


## Step 2. Start Your Cluster and Install Kagent
We have Docker and Python installed and I have my local Kubernetes cluster running and this is where our AI agent will live.  

In this step, you will start a local Kubernetes cluster with Minikube, install the agent runtime (kagent), and connect it to Google's Gemini API. By the end, your cluster will be a fully operational AI agent platform with demo agents already running.


### Install Helm
`Kagent` uses Helm (a Kubernetes package manager) under the hood, and `kubectl` is how you interact with your cluster directly. You need both installed before proceeding.  

• Install both Helm and kubectl by running the commands for your platform:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
sudo snap install kubectl --classic
```

• Verify both installed correctly and confirm the cluster is running:
```bash
helm version
kubectl cluster-info
```

You should see a Helm version number and the Kubernetes control plane address 
![alt images](helm-kubectl.png)


### Install kagent and deploy it to the cluster
With our cluster running, we now need the agent runtime = `kagent`. `Kagent` turns your generic Kubernetes cluster into an AI agent platform by adding Custom Resource Definitions (CRDs) for agents, tools, and model configs.  

Install the kagent CLI by running the command for your platform:
```bash
curl https://raw.githubusercontent.com/kagent-dev/kagent/refs/heads/main/scripts/get-kagent | bash
```

• Verify the CLI is available by running:
```bash
kagent version
```

`Kagent` needs access to a large language model (LLM) to power its agents. You will use Google's Gemini API, which provides a free tier with no billing setup required.  

• Open your browser and go to aistudio.google.com.  
• Sign in with your Google account.  
• Click Get API key in the left sidebar.  
• Click Create API key and copy the generated key.  

💡 What is this API key for?  
This key lets your agents call Google's Gemini model to generate responses. The free tier includes generous limits for personal projects. No credit card is needed.  


• Tell kagent to use Gemini as its model provider by exporting these environment variables:
```bash
export KAGENT_DEFAULT_MODEL_PROVIDER=gemini
export GOOGLE_API_KEY=your-gemini-api-key-here
```

💡 What do these exports do?  
By default, `kagent install` looks for an OpenAI key. Setting `KAGENT_DEFAULT_MODEL_PROVIDER=gemini` tells kagent to use Gemini instead. `GOOGLE_API_KEY` passes your key so kagent can configure the Gemini model during installation.


• Install kagent onto your cluster with the demo profile by running the command below. This command takes 2-3 minutes. It installs the kagent controller, dashboard, and demo agents as Kubernetes pods.
```bash
kagent install --profile demo
```

💡 What does the demo profile include?  
The `--profile demo` flag preloads your cluster with sample agents and MCP tools so you can explore kagent immediately. You will see agents like helm-agent, observability-agent, and istio-agent already running. Make sure the cluster is healthy otherwise you might see install timing out and pods stuck.  

### Create the Kubernetes secret and verify kagent is running
Your agents also need the key stored as a Kubernetes secret so they can access it at runtime without exposing it in your code. 

Create the secret by running:
```bash
kubectl create secret generic kagent-gemini -n kagent --from-literal GOOGLE_API_KEY=your-gemini-api-key-here
```

💡 What does this command do?  
This creates a Kubernetes Secret called `kagent-gemini` in the kagent namespace. It stores your API key under the key name `GOOGLE_API_KEY`. Kagent's Gemini provider looks for this exact secret name and key by default. You should see `secret/kagent-gemini` created in the output.  

Your Kubernetes cluster is now a live AI agent platform. Next up, you will scaffold your own finance research agent and see it respond to your first message.  


## Step 3. Scaffold and Run Your Finance Agent Locally
Our cluster is running and kagent is installed, but we have no custom agents yet. Before deploying anything to Kubernetes, we want to see our agent come alive fast and get immediate feedback that it works.  

The kagent CLI scaffolds a complete agent project in seconds. We will customize it with a finance research persona, then run it locally to chat with it. There is a catch though: without real tools connected, the agent can only talk generically about finance. That limitation is exactly what you will fix in the next step.  

In this step, we'll:  
• Scaffold a finance agent project using the kagent CLI.  
• Customize the agent with a finance research system prompt.  
• Run the agent locally and chat with it.  


### Scaffold your finance agent project
The `kagent init` command creates a ready-to-run agent project with all the boilerplate wired up. You choose the framework (ADK), language (Python), model provider (Gemini), and give your agent a name.  

• Move to your Desktop by running this command:
```bash
cd ~/Desktop
```

• Scaffold your finance agent project by running this command:
```bash
kagent init adk python finance_agent --model-provider Gemini --model-name gemini-3.6-flash
```

💡 What does this command do?  
• `adk` selects the Agent Development Kit framework (Google's ADK for Python).  
• `python` sets the language.  
• `finance_agent` is the project name and directory.  
• `--model-provider Gemini --model-name gemini-3.6-flash` configures the agent to use Google's Gemini 3.6 Flash model.  

You will see output confirming the project was created, including a file tree and next-step hints.
![alt images](kagent-init.png)


• Move into your new project folder and list the files by running:
```bash
cd finance_agent/
ls
```  

You should see files including `kagent.yaml`, `pyproject.toml`, `docker-compose.yaml`, and a `finance_agent/` subdirectory containing your agent code.  

💡 What is in the scaffolded project?  
• `finance_agent/agent.py` contains the main agent logic (currently a dice-rolling placeholder).  
• `finance_agent/mcp_tools.py` wires up MCP tool discovery so the agent can use external tools. It is auto-generated from the MCP servers listed in `kagent.yaml`, so you never edit it by hand.  
• `finance_agent/agent-card.json` is the agent's [A2A](https://a2a-protocol.org) "business card": its name, description, version, capabilities and skills. Other agents and the kagent dashboard read it to discover what your agent can do.  
• `kagent.yaml` is the project configuration that tells the kagent CLI which model provider, model and MCP servers to use.  
• `pyproject.toml` describes our Python project: its name, version and dependencies.  
• `Dockerfile` builds the agent image on top of kagent's `kagent-adk` base image, which already contains the ADK runtime.  
• `docker-compose.yaml` is used by `kagent run` to start the agent container (and, later, our Finnhub MCP tool server container) side by side on our machine so we can debug and test locally. It passes our API keys into the containers from the `.env` file we create below. Once the agent works locally, we will deploy it to our Kubernetes cluster, where Kubernetes manifests (YAML files and CRDs) take over the orchestration and docker-compose is no longer needed.  


### Configure the agent with a finance persona
The scaffolded `agent.py` has a generic dice-rolling prompt. You will replace it entirely with a finance research persona that instructs the agent how to behave when answering market questions.  

• Open `finance_agent/agent.py` in VS Code.  
• Select all the existing content and delete it.  
• Paste the following code, which defines the system prompt:  
```python
from google.adk.agents import Agent

from .mcp_tools import get_mcp_tools

SYSTEM_PROMPT = """You are a finance research assistant that helps users analyze stocks and market data.

# Instructions
- Use your available tools to fetch real-time stock data when users ask about prices, companies, or market trends
- Always provide context with your data: explain what the numbers mean
- If a user asks about a stock, fetch the current quote before answering
- Compare stocks when asked by fetching data for each ticker
- If you don't have a tool for something, say so clearly rather than guessing
- Format responses in Markdown with clear sections

# Response format
- Start with a brief summary of what you found
- Include specific numbers (price, change %, volume) when available
- Add your analysis of what the data suggests
- End with any caveats (e.g., "this is real-time data, not investment advice")
"""
```

💡 What does this system prompt do?  
The `SYSTEM_PROMPT` is a set of instructions that shapes how the agent behaves. It tells the agent to use tools for real data, format responses in Markdown, and never guess when tools are unavailable.  

The imports pull in the `Agent` class from Google's ADK and the `get_mcp_tools()` helper from the auto-generated `mcp_tools.py`. Calling it returns one toolset per MCP server declared in `kagent.yaml`.  


• Below the `SYSTEM_PROMPT` string, add the agent instantiation and save it:
```python
mcp_tools = get_mcp_tools()

root_agent = Agent(
    name="finance_agent",
    model="gemini-3.6-flash",
    description="A finance research agent that fetches real-time stock data and provides market analysis.",
    instruction=SYSTEM_PROMPT,
    tools=mcp_tools,
)
```

💡 What does this code do?  
• `root_agent` is the entry point kagent looks for when running your agent.  
• `model` tells it which LLM to call (Gemini 3.6 Flash).  
• `instruction` passes your system prompt so every conversation uses these rules.  
• `tools=mcp_tools` connects any MCP tool servers declared in `kagent.yaml`. Right now there are none, so the list is empty.  


### Update the project configuration
• Open `kagent.yaml` in VS Code. The scaffold already filled in the framework, language and model. Only fill in the empty `description` field, then save it. Your file should look like this (minus the `updatedAt` timestamp line, which the CLI manages):  
```yaml
agentName: finance-agent
language: python
framework: adk
modelProvider: gemini
modelName: gemini-3.6-flash
description: "A finance research agent that fetches real-time stock data and provides market analysis."
```

💡 Why don't we add the MCP server here yet?  
`kagent.yaml` uses the exact keys the kagent CLI expects (`agentName`, `modelProvider`, `modelName`, ...), so don't rename them. MCP servers go in an `mcpServers` section, but we won't write it by hand. In the next step, the `kagent add-mcp` command adds it for us once the Finnhub tool server exists. If we declared a server that doesn't exist yet, the agent would try to connect to it and fail.  

• Now open `finance_agent/agent-card.json`, replace its content with the below and save it:
```json
{
  "name": "finance_agent",
  "description": "A finance research agent that fetches real-time stock data and provides market analysis.",
  "url": "localhost:8080",
  "version": "0.1.0",
  "capabilities": {
    "streaming": true
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "skills": [
    {
      "id": "stock_research",
      "name": "Stock Research",
      "description": "Looks up stock quotes, company profiles, and analyst trends, then explains what the numbers mean.",
      "tags": ["finance", "stocks", "market-data"]
    }
  ]
}
```

💡 Why so many fields?  
At startup the kagent runtime validates this file against the A2A `AgentCard` schema. `url`, `capabilities`, `defaultInputModes`, `defaultOutputModes` and `skills` are all **required**. If you trim the card down to just name, description and version, the agent crashes on startup with `5 validation errors for AgentCard`. Keep `name` the same as the agent and project name (`finance_agent`).  

• Confirm your updated files exist by running:
```bash
ls finance_agent/
```
You should see `__init__.py`, `agent.py`, `agent-card.json` and `mcp_tools.py`.  


### Fix the Dockerfile (kagent v0.10.2)
`kagent run` and `kagent build` both build a Docker image from the scaffolded `Dockerfile`. With kagent v0.10.2, that build fails at the `RUN uv sync` line:
```
runc run failed: ... exec: "/bin/sh": stat /bin/sh: no such file or directory
failed to solve: process "/bin/sh -c uv sync" did not complete successfully: exit code: 1
```

💡 Why does it fail?  
The `kagent-adk` base image is *distroless*: for security, it contains only Python and the agent runtime, with no shell (`/bin/sh`) and no `uv`. A shell-form `RUN` instruction needs `/bin/sh`, so it can't run. We don't need it anyway: the base image already ships `google-adk` in its own virtualenv (`/.kagent/.venv`), and that's the only dependency our agent has.  

• Open `Dockerfile` in VS Code, replace the `RUN uv sync` line with the comment below, and save it:
```dockerfile
# The kagent-adk base image is distroless (no /bin/sh, no uv) and already ships
# google-adk in /.kagent/.venv, so there is nothing to install here.
```

⚠️ The Dockerfile header says `AUTOGENERATED FILE: DO NOT EDIT`. Re-running `kagent init` would overwrite our fix, so re-apply it if you ever re-scaffold.  


### Create the environment file and run the agent
The agent needs our Gemini API key to call the LLM. We keep both API keys in a single `.env` file inside the `finance_agent/` project folder. `kagent run` starts the agent with docker compose, which automatically loads a file named exactly `.env` from the project folder. Later, we pass the same file to `kagent deploy --env-file .env` when deploying to Kubernetes.  

• From inside the `finance_agent/` project folder, create the `.env` file by running:
```bash
cat > .env << 'EOF'
GOOGLE_API_KEY=your-gemini-api-key-here
FINNHUB_API_KEY=your-finnhub-api-key-here
EOF
```

• I opened `.env` in VS Code and replaced `your-gemini-api-key-here` with the actual Gemini API key we obtained from Google AI Studio in the previous step.  
• I left `your-finnhub-api-key-here` as a placeholder for now. We will get the Finnhub key in the next step.  


💡 Why `.env` and not `.env.local`?  
docker compose only auto-loads a file named exactly `.env`. If you name it `.env.local`, `kagent run` starts the agent with an empty `GOOGLE_API_KEY`, and the chat replies `No API key was provided. Please pass a valid API key.` Never commit `.env`. Add it to your `.gitignore`.  

💡 Why two keys?  
`GOOGLE_API_KEY` authenticates with Gemini so the agent can generate responses.  
`FINNHUB_API_KEY` authenticates with the Finnhub stock data API once we build the MCP tool server in the next step.  

Time to see our agent in action. Before we run it, let's think about this first: we told the agent to use its tools for fetching stock data, but we haven't given it any tools yet. What do you think will happen when you ask it about stock prices?  


• From inside the `finance_agent/` project folder, build and run your agent locally by running:
```bash
kagent build . && kagent run .
```

💡 What happens when we run this?  
• `kagent build` packages our agent into a Docker image named `localhost:5001/finance_agent:latest`, using the `Dockerfile` we fixed above. The first build takes a minute or two while the `kagent-adk` base image downloads.  
• `kagent run` starts the agent locally using `docker compose`, which loads our keys from `.env`, and opens a terminal chat interface where we can type messages.  
• No MCP servers are declared in `kagent.yaml` yet, so the agent starts with an empty tool list and answers using Gemini alone.  

💡 Changed your code later? Run `kagent build .` again (or `kagent run . --build`) so the image picks up your edits. Otherwise `kagent run` reuses the image it already built.  


• In the terminal chat interface, type:  
```bash
Hello, what can you do?
```

The agent responds by describing its finance research capabilities. Mine replied: *"I am a financial research assistant that fetches real-time stock market data, compares company metrics, and provides clear market analysis to help you understand stock trends."*  

• Now ask it something that requires real data:
```bash
What is the current price of AAPL?
```

You should get a nicely structured Markdown answer (summary, market data, analysis, caveat) that politely says it **can't** fetch the live price, because it has no stock quote tool yet.


### Summary
I am unable to retrieve the real-time stock price for AAPL (Apple Inc.) because I currently
do not have access to an active live stock quote tool or external market API integration.


### Market Data
* Ticker: AAPL
* Current Price: Unavailable (Real-time data tool required)
...
### Caveat
Disclaimer: ... does not constitute financial or investment advice.

This is exactly what we want at this stage. The agent follows the persona's response format and, as instructed, says it lacks a tool instead of inventing a price.  


## Step 4. Build the Finnhub MCP Tool Server
In the last step, we chatted with our agent and saw its limitation firsthand. When we asked about stock prices, it could only tell us it had no way to look them up, because it has no access to real market data.  

An LLM without tools is just a chatbot. In this step, we will build a custom MCP tool server that connects to Finnhub's free stock data API. This gives our agent the ability to fetch live prices, company profiles, and analyst recommendations on command.  

In this step, get ready to:  
• Get a free Finnhub API key for real-time stock data.  
• Scaffold an MCP server project and implement three stock data tools.  
• Test the MCP server locally and see real price data returned.  


### Get your Finnhub API key
Finnhub provides free real-time stock market data with 60 API calls per minute. No credit card is required.  

• I'll open a browser and navigate to [finnhub.io](https://finnhub.io/).  
• Click Get free API key and create an account with my email.  
• After signing in, copy your API key from the dashboard.  

Your `.env` file already has a placeholder for this key from the previous step.  
• In VS Code, open .env.local.  
• I replaced <your-finnhub-api-key-here> with the API key I just copied from Finnhub then save.
```bash
FINNHUB_API_KEY=your-finnhub-api-key-here
```  

### Scaffold and implement the MCP server
The kagent CLI includes dedicated MCP commands for building tool servers. We will scaffold a new server project, then replace the boilerplate with your custom Finnhub integration.  

• In our project directory finance_agent (where the kagent.yaml is located), we'll scaffold the MCP server project by running:
```bash
kagent mcp init python finnhub-tools --no-git
```

Why python and `--no-git` is in the command?  
• `python` is required. In kagent 0.10.2, kagent mcp init needs a language (go, java, python or typescript) before the name. Our server is Python.  
• `--no-git` stops a repo inside our repo. Without it, kagent runs `git init` inside `finnhub-tools/`, our repo would then treat that folder as a separate embedded repository, and its files wouldn't be committed with the rest of your project.  

Why this directory? the generated `docker-compose.yaml` looks for the server at `./finnhub-tools`, relative to the project folder. Running the command anywhere else breaks that path.  


It generated files like `Dockerfile`, `pyproject.toml`, and a `src/` directory listed in the output.  
I replaced the scaffolded code with our custom Finnhub tool implementation. The target structure is a simple Python package with three files.  

• Create the main tools file at finnhub-tools/tools.py in VS Code and paste the following setup code:
```bash
import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("finnhub-tools")

FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
```

💡 What does this setup do?  
• `FastMCP("finnhub-tools")` creates a new MCP server instance named `finnhub-tools`.  
• `FINNHUB_API_KEY` reads your API key from the environment variable at runtime.  
• `FINNHUB_BASE_URL` sets the base URL for all Finnhub API calls so you do not repeat it in every function.


• Add the first tool function below the setup code in finnhub-tools/tools.py:
```bash
@mcp.tool()
async def get_stock_quote(symbol: str) -> dict:
    """Get the current stock quote for a given ticker symbol.

    Args:
        symbol: The stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

    Returns:
        A dictionary with current price (c), change (d), percent change (dp),
        high (h), low (l), open (o), previous close (pc), and timestamp (t).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FINNHUB_BASE_URL}/quote",
            params={"symbol": symbol.upper(), "token": FINNHUB_API_KEY},
        )
        response.raise_for_status()
        data = response.json()
        return {
            "symbol": symbol.upper(),
            "current_price": data["c"],
            "change": data["d"],
            "percent_change": data["dp"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "previous_close": data["pc"],
        }
```  

💡 What does `get_stock_quote` do?  
The `@mcp.tool()` decorator registers this function as a tool your agent can call. When invoked, it sends an HTTP GET request to Finnhub's `/quote` endpoint with the stock ticker symbol.  
The docstring is important because the agent reads it to understand when and how to use the tool. Finnhub returns single-letter keys like `c` for current price, so the function maps them to readable names.  


• Before adding more tools, set up the package wiring files so you can test shortly. Create `finnhub-tools/src/tools/__init__.py` with this content:  
```bash
from .tools import mcp
```

• Create/modify `finnhub-tools/src/toos/__main__.py` with this content:
```bash
from .tools import mcp

mcp.run()
```

💡 Why `__init__.py` and `__main__.py`?

`__init__.py` imports the mcp server instance so other modules can access it.  
`__main__.py` makes the package executable with `python -m finnhub_tools`. This is exactly how `kagent.yaml` is configured to start the MCP server.  


• Save all three files (`tools.py`, `__init__.py`, `__main__.py`).  


Before we run this, let's think about what we will expect. We have one tool registered (`get_stock_quote`), a Finnhub API key in our environment, and a server that starts with `mcp.run()`. Do you think calling the tool with `AAPL` will return a real price?  

• Lets test your MCP server by running the command below.:  
```bash
cd finnhub-tools/
kagent mcp run
```

💡 What happens when you run this?  
This command builds our MCP server into a Docker image and launches the MCP Inspector tool in a browser. The Inspector lets us connect to our server and call tools manually to verify they work.

It may take a few seconds for the connection to establish. If you do not have the MCP Inspector installed, the command will prompt you to install it first.  

• In the MCP Inspector, click Connect to connect to your server.  
• Click the `Tools` tab, then click `List Tools`.  
• Select the `get_stock_quote` tool.  
• Enter `AAPL` in the symbol field and click `Run Tool`.  

You should see real-time JSON data returned with Apple's current stock price, change amount, percent change, daily high, low, open, and previous close.  
[alt images](test-mcp-server-aapl.png)  


I'll stop the MCP server by pressing `Ctrl+C` in our terminal. Our first tool works. Now we'll add the remaining two tools to give our agent a fuller picture of any stock.  

• I'll add this second tool function below `get_stock_quote` to `finnhub-tools/src/tools.py`:
```bash
@mcp.tool()
async def get_company_profile(symbol: str) -> dict:
    """Get the company profile for a given ticker symbol.

    Args:
        symbol: The stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

    Returns:
        A dictionary with company name, industry, market cap, and other details.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FINNHUB_BASE_URL}/stock/profile2",
            params={"symbol": symbol.upper(), "token": FINNHUB_API_KEY},
        )
        response.raise_for_status()
        return response.json()
```  

💡 What does get_company_profile do?  
This tool calls Finnhub's `/stock/profile2` endpoint. It returns information like company name, industry, market capitalization, and exchange listing. Your agent uses this to provide context when comparing stocks.  


• I'll add the third and final tool function below `get_company_profile` in `finnhub-tools/src/tools.py`:  
```bash
@mcp.tool()
async def get_recommendation_trends(symbol: str) -> list:
    """Get analyst recommendation trends for a given ticker symbol.

    Args:
        symbol: The stock ticker symbol (e.g., AAPL, MSFT, GOOGL)

    Returns:
        A list of monthly recommendation data with buy, hold, sell, strongBuy, strongSell counts.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FINNHUB_BASE_URL}/stock/recommendation",
            params={"symbol": symbol.upper(), "token": FINNHUB_API_KEY},
        )
        response.raise_for_status()
        return response.json()
```  

• Save the added codes in `tools.py`.  


💡 What does get_recommendation_trends do?  
This tool fetches analyst consensus data from Finnhub's `/stock/recommendation` endpoint. It returns monthly counts of buy, hold, sell, strong buy, and strong sell recommendations. Our agent can use this to provide market sentiment analysis.  


### Test the complete MCP server
Our `kagent.yaml` already references the `finnhub-tools` MCP server from the scaffolding in Step 3. Add the wiring below in kagent.yaml before the final test.  

• Open `kagent.yaml` and confirm you see this section under `mcp_servers`:`
```bash
mcp_servers:
  - name: finnhub-tools
    command: python
    args: ["-m", "finnhub_tools"]
```

• final `kagent.yaml`:
```bash
agentName: finance-agent
language: python
framework: adk
modelProvider: gemini
modelName: gemini-3.6-flash
description: "A finance research agent that fetches real-time stock data and provides market analysis."

mcp_servers:
  - name: finnhub-tools
    command: python
    args: ["-m", "finnhub_tools"]
```

💡 How does wiring work?  
This YAML tells kagent to start your MCP server by running `python -m finnhub_tools`. The agent automatically discovers all tools registered with `@mcp.tool()` on that server and makes them available for use.  


• Now let's run the server one more time to verify all three tools appear. Start the MCP server again by running:
```bash
kagent mcp run
```

• In the MCP Inspector, under "Servers - finnhub tools" enable connection by clicking the "Disconnected" button. It will automatically turn on the connection and see the status to "Connected".  
• Click the `Tools` tab, and you'll see the 3 tools under Tools; `get_stock_quote`, `get_company_profile`, and `get_recommendation_trends`.
• Select `get_stock_quote`, enter `AAPL` in the symbol field, and click `Execute Tool`. You should see real price data returned as JSON with fields like `current_price`, `change`, and `percent_change`.  
[alt images](get_stock_quote_json.png)


## Step 5. Deploy to Kubernetes and Chat
Our agent works locally and fetches live market data from Finnhub. That proves our code is solid. Now we will deploy it to our local K8s cluster so it runs as a real Kubernetes workload. The kagent CLI packages our agent and MCP server into container images, pushes them to the cluster registry, and creates the proper Custom Resource Definitions (CRDs) that tell Kubernetes how to manage them.  

In this step, we'll:  
• Build and push Docker images for your agent and MCP server to the Minikube registry.  
• Deploy everything to the cluster and verify with kubectl.  
• Chat with your deployed agent using the dashboard and CLI.  

### Build and push images to the Minikube registry
Kubernetes runs containers, not raw Python files. Before our cluster can run the agent, it needs container images stored in a registry it can access.  We can use docker images either using docker command or via kagent CLI. The "Kagent CLI" is the fast track but I listed the Docker way too if you prefer this method.  

Docker way:  
• Build & Push your MCP Server (finnhub-tools)
```bash
cd finance_agent/finnhub-tools/
docker build -t your_dockerhub_username/finnhub-tools:v1 .
docker push your_dockerhub_username/finnhub-tools:v1
```

• Build & Push your Finance Agent (finance_agent)
```bash
cd finance_agent/
docker build -t your_dockerhub_username/finance-agent:v1 .
docker push your_dockerhub_username/finance-agent:v1
```   

The Kagent CLI way (The Fast Track)  
We'll let Kagent manage the Docker build and push commands and we need to pass the `--image` override flag directly to `kagent build`. From inside the `finance_agent` root directory:
```bash
kagent build . --image your_dockerhub_username/finance-agent:latest --push
```  

💡 What does this command do?  
The `kagent build` command reads our kagent.yaml and builds Docker images for our agent and every MCP server listed in it.  
The `--push` flag uploads the built images to the localhost:5001 registry that Minikube exposes.  


• Update `kagent.yaml` to Link our Docker Hub Images. Since our images live securely in the cloud, we need to tell our cluster to pull them from Docker Hub instead of trying to compile them locally at runtime. We'll need to update our `kagent.yaml` file in VS Code and update the `mcp_servers` section. Replace the `command` and `args` lines with our new Docker Hub image tag:
```bash
agentName: finance_agent
language: python
framework: adk
modelProvider: gemini
modelName: gemini-3.6-flash
description: "A finance research agent that fetches real-time stock data and provides market analysis."

mcp_servers:
  - name: finnhub-tools
    image: your_dockerhub_username/finance-agent:latest
``` 

### Deploy to our kubeadm Cluster
To run the final deployment, run `kagent deploy`. We need to pass the  `--image` flag so Kagent deploys our Docker Hub agent image instead of searching for a local one:  
```bash
kagent deploy . --env-file .env --image your_dockerhub_username/finance-agent:latest
```

💡 What does this command do?  
This reads our kagent.yaml manifest and creates Kubernetes CRDs for our agent and MCP server. The `--env-file .env` flag injects our API keys as Kubernetes secrets in the kagent namespace so our pods can access them securely. This will generate a fully compliant Kubernetes Secret named `finance-agent-env`. The kagent controller running on our cluster picks up these CRDs and spins up pods for both the agent and the finnhub-tools MCP server. Under the hood, the `Scheduler` then places the pods to our worker nodes and the kubelet instructs the runtime engine (containerd) to pull our newly built image `testyoc/finance-agent:v1` directly from Docker Hub. 


### Verification

```bash
kubectl get agents,mcpservers,pods -n kagent
```
[alt images](k-get-agents-mcpserver-pods.png)