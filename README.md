# Seldon with stroke prediction dataset 

## Dataset

https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset


<br>

## Prerequisite
<div> 
Make sure you have the following packages installed
    <ul>
        <li> Install <a href="https://kind.sigs.k8s.io/docs/user/quick-start/"> Kind </a> </li>
        <li> Install <a href="https://kubernetes.io/fr/docs/tasks/tools/install-kubectl/"> Kubectl </a> </li>
        <li> Install <a href="https://docs.docker.com/"> Docker </a> </li>
        <li> Install <a href="https://helm.sh/docs/intro/install/"> Helm </a> </li>
    <ul>
 </div>




<br>

## Folder Architecture
<ul>
    
<li> <ins> <strong>data</strong> </ins> :  Data of the dataset </li>

<li> <ins> <strong>model folders</strong> </ins> :  Contains the different scaler / model and transformers </li>

<li> <ins> <strong>notebook</strong> </ins> : 2 training notebook, split data notebook and seldon client notebook  </li>

<li> <ins> <strong>seldon</strong> </ins> :  Seldon Configuration files</li>
</ul>
</br>

## Environment

Create your environment (I use conda): 
    <ul>
        <li> <code>conda create -n  stroke python=3.8 </code></li>
        <li> <code> pip install -r requirements.txt</code></li>
    </ul>
</br>

## Create your cluster

<code> kind create cluster --name seldon --image kindest/node:v1.24.7@sha256:577c630ce8e509131eab1aea12c022190978dd2f745aac5eb1fe65c0807eb315</code>

## Define Kubectl Context

<code> kubectl cluster-info --context kind-seldon </code>

## Configure Istio and Ingress

<div>
<strong>To set up Istio:</strong>
    <ol>
        <li> <code>curl -L https://istio.io/downloadIstio | sh - </code></li>
        <li> <code> cd istio-&ltversion> </code> </li>
        <li> <code> export PATH=$PWD/bin:$PATH </code> </li>
        <li> <code> istioctl install --set profile=demo -y </code> </li>
        <li> <code> kubectl label namespace default istio-injection=enabled </code> </li>
    </ol>
</div>
<div> 
   <strong> To set up ingress:</strong>
    <code> kubectl apply -f seldon/ingress/ingress.yml </code>
</div>

## Install Seldon

<div> 
    <ol>
        <li> Create Seldon namespace <code>kubectl create namespace seldon-system</code></li>
        <li> Install Seldon <code> helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --set istio.enabled=true \
    --namespace seldon-system </code> </li>
    <li> Verify your installation <code> kubectl get pods -n seldon-system </code> </li>
    </ol>
</div>

## Install MinIO

MinIO is a storage platform that will allow us to access our different models and binary file, it's an alternative for AWS s3 bucket as I am working locally.
<ul>
<li> Install MinIO in cluster
<code>kubectl create ns minio-system
helm repo add minio https://helm.min.io/
helm install minio minio/minio \
    --set accessKey=minioadmin \
    --set secretKey=minioadmin \
    --namespace minio-system </code>
</li>
<li> Check MinIO status 
<code> kubectl rollout status deployment -n minio-system minio </code>
<li> Once Minio is installed forward the port to access it from a browser following these steps  
</li>
<li> <code> kubectl port-forward -n minio-system svc/minio 9000:9000  </code>
</li>
<li> Now you can access MinIO on your local machine via http://localhost:9000 use "minioadmin" as access-key and secret-key </li>
<li> Next Step is to create two buckets named modelclf and modeltree and in each of them upload their respective files from the github repository </li>
</ul>

## Python Class Wrapper

<div> For both of the wrappers ( stroke_wrapper_tree and stroke_wrapper_clf) Update the init functio by replacing the MinIO IP address with the one you got by doing <code> kubectl get services -n minio-system</code>

## Code setup and config
<ol>
<li> cd into seldon/stroke-wrapper-clf
<li> Build Docker Image with python3.8 seldon: <code> docker build . -f Dockerfile -t seldonio/&ltname&gt:&ltversion&gt</code> in titanic wrapper folder
<li> Create a .s2i folder and add your environment as follow, the MODEL_NAME is the name of your .py file <li>
<li> Use s2i to build docker image with required files and config required by seldon: <code> s2i build . &ltdocker-build-name&gt  seldonio/clf:0.0.1 </code>
<li> Load image into kind: <code> kind load docker-image seldonio/clf:0.0.1 --name seldon </code></li>
<li> Repeat steps 3-5 for stroke_wrapper_tree a different name for the s2i image (seldonio/tree:1.0.0)
<li> Verify the seldon_deployment.yml and change the <strong> image </strong> node
<li> Apply Seldon Deployment yml file: <code>kubectl apply -f seldon-deploy.yml</code></li> in Seldon_Deployment folder
<li> Check if pod running: <code> kubectl get pods</code></li>
<li> Port Forwarding: <code> kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80 </code>
<li> Run seldon notebook
</ol>



## Prometheus and Grafana

<ol>
   
 <li> Install Prometheus on Kubernetes cluster </li>
 <li> <code>kubectl create namespace seldon-monitoring</code></li>

<li> <code>helm upgrade --install seldon-monitoring kube-prometheus \
    --version 8.2.2 \
    --set fullnameOverride=seldon-monitoring \
    --set prometheus.scrapeInterval=1s \
    --namespace seldon-monitoring \
    --repo https://charts.bitnami.com/bitnami
    </code></li>

<li>  Apply prometheus and graphana yaml in prometheus_grafana folder <code> kubectl apply -f prometheus.yml </code> and <code> grafana.yml </code> </li>
<li><code>kubectl port-forward -n seldon-monitoring svc/seldon-monitoring-prometheus 9090:9090</code></li>
<li><code>kubectl port-forward service/grafana 3000:3000</code></li>
<li> port forward grafana and prometheus for <strong> grafana use admin, admin as password </strong>
<li> Grafana UI: connect to a data source, chose prometheus and as <strong>host the cluster IP of prometheus port 9090</strong> the IP address can be found can be found by doing <code> kubectl get services seldon-monitoring-prometheus -n seldon-monitoring  </code>  and in grafana data source url - http://ip-address:9090
</li>
</ol>


