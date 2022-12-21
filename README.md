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
<li> <code> export POD_NAME=$(kubectl get pods --namespace minio-system -l "release=minio" -o jsonpath="{.items[0].metadata.name}" </code>
</li>
<li> <code> kubectl port-forward $POD_NAME 9000 --namespace minio-system </code>
</li>
<li> Now you can access MinIO on your local machine via http://localhost:9000 use "minioadmin" as access-key and secret-key </li>
<li> Next Step is to create two buckets named modelclf and modeltree and in each of them upload their respective files from the github repository </li>
</ul>


## Code setup and config
<ol>
<li> cd into class wrapper folder
<li> Build Docker Image with python3.8 seldon: <code> docker build . -f Dockerfile -t seldonio/&ltname&gt:&ltversion&gt</code> in titanic wrapper folder
<li> Use s2i to build docker image with required files and config required by seldon: <code> s2i build . &ltdocker-build-name&gt  seldonio/&ltname&gt:&ltversion&gt </code>
<li> Load image into kind: <code> kind load docker-image &lts2i-build-name&gt --name seldon </code></li>
<li> Repeat steps 3-4 for the two wrapper folder giving a different name for the s2i image
<li> Verify the seldon_deployment.yml and change the <strong> image </strong> node
<li> Apply Seldon Deployment yml file: <code>kubectl apply -f seldon_deployment.yml</code></li> in Seldon_Deployment folder
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
<li> Grafana UI: connect to a data source, chose prometheus and as <strong>host the cluster IP of prometheus port 9090</strong> that can be found by doing <code> kubectl get services -A </code>


