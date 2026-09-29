

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

Here's the official documentation steps installing Docker in Ubuntu and there are different ways to install Docker as the documentation suggests. We'll ust follow this step [Install using the apt repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and we should be good to go. 


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

