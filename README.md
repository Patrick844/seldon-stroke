# Seldon with stroke prediction dataset 

## Dataset

https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset



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

create your environment (I use conda): 
    <ul>
        <li> <code>conda create -n  stroke python=3.8 </code></li>
        <li> <code> pip install -r requirement.txt</code></li>
    </ul>
</br>

## Code setup and config
<ol>
<li> Build Docker Image with python3.8 seldon: <code> docker build . -f Dockerfile -t seldonio/seldon-core-titanic:1.4</code> in titanic wrapper folder
<li> Use s2i to build docker image with required files and config required by seldon: <code> s2i build . seldonio/seldon-core-titanic:0.4  seldonio/titanic:1.4 </code>
<li> Load image into kind: <code> kind load docker-image seldonio/titanic:1.4 --name seldon </code></li>
<li> Apply Seldon Deployment yml file: <code>kubectl apply -f sdpl.yml</code></li> in Seldon_Deployment folder
<li> Check if pod running: <code> kubectl get pods</code></li>
<li> Port Forwarding: <code> kubectl port-forward -n istio-system svc/istio-ingressgateway 8081:80 </code>
<li> Run seldon notebook
</ol>

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
</li>
</ul>

## Prometheus and Grafana

<ol>
   
 <li> Install Prometheus on Kubernetes cluster <code>kubectl create namespace seldon-monitoring

helm upgrade --install seldon-monitoring kube-prometheus \
    --version 6.9.5 \
    --set fullnameOverride=seldon-monitoring \
    --namespace seldon-monitoring \
    --repo https://charts.bitnami.com/bitnami </code></li>

<li>  Apply prometheus and graphana yaml in prometheus_grafana folder <code> kubectl apply -f prometheus.yml </code> and <code> grafana.yml </code> </li>
<li><code>kubectl port-forward -n seldon-monitoring svc/seldon-monitoring-prometheus 9090:9090</code></li>
<li><code>kubectl port-forward service/grafana 3000:3000</code></li>
<li> port forward grafana and prometheus for <strong> grafana use admin, admin as password </strong>
<li> Grafana UI: connect to a data source, chose prometheus and as <strong>host the cluster IP of prometheus port 9090</strong> that can be found by ...


