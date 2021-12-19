# RabbitMQ - Python App on KinD Cluster

## Install requirements

Install KinD from [here.](https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries)

Install Docker from [here.](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)

Install Helm from [here.](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)

## Deploy the components for the cluster

First create the cluster using `kind-cluster.yaml` which sets up cluster with ingress-specific values.

    kind create cluster --name rabbit-app --config kind-cluster.yaml

Enable NGINX Ingress Controller for the cluster

    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

Add Helm repos

    helm repo add elastic https://helm.elastic.co
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add fluent https://fluent.github.io/helm-charts

Install ElasticSearch + Kibana and enable Ingress for Kibana

Note: Ingress in Kibana chart is not used since it uses deprecated Ingress API

    helm install elasticsearch elastic/elasticsearch -n monitoring --create-namespace -f es-values.yaml
    helm install kibana elastic/kibana -n monitoring
    kubectl apply -f kibana-ingress.yaml

Install RabbitMQ as 2 node cluster

    helm install rabbitmq bitnami/rabbitmq -n messaging  -f rabbitmq-values.yaml


Install Fluent-bit for logging

    helm install fluent-bit fluent/fluent-bit -n monitoring -f fluent-values.yaml

Deploy application (which checks RabbitMQ cluster and produces random strigs), RabbitMQ producer and RabbitMQ consumer

    kubectl apply -f rabbit-check.yaml
    kubectl apply -f rabbit-producer.yaml
    kubectl apply -f rabbit-consumer.yaml

Edit /etc/hosts to acces the pods from outside of the cluster using hostname. This step is neccesarry to use Ingress.

    cat <<EOL >> /etc/hosts
    127.0.0.1 kibana.local
    127.0.0.1 rabbit-check.local
    127.0.0.1 rabbit-producer.local
    EOL

Visit `rabbit-check.local/automatapi/v1/rabbitmqConnection` to check RabbitMQ connection status. 

Visit `rabbit-producer.local` to push messages to RabbitMQ.

Visit `kibana.local` to interract with the ElasticSearch. Cluster logs can be seen from `logstash-` index pattern. (Fluentbit defaults to this index name.). Documents created by RabbitMQ consumer are stored at `rabbitmq-output` index.

If any changes are made to Python code, containers should be builded again and deployment yamls shouls be changed accordingly. 

Note: This should not be used in production enviorenment since this repository is intended as PoC.  
