from fastapi import FastAPI
from kubernetes import client, config
from prometheus_client import Prometheus

app = FastAPI()

config.load_kube_config()

@app.post("/createDeployment/{deployment_name}")
def create_deployment(deployment_name: str):
    # Define the deployment
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector={"matchLabels": {"app": deployment_name}},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": deployment_name}),
                spec=client.V1PodSpec(containers=[
                    client.V1Container(
                        name=deployment_name,
                        image="nginx",  # Example application
                        ports=[client.V1ContainerPort(container_port=80)]
                    )
                ])
            )
        )
    )

    # Create the deployment
    api_instance = client.AppsV1Api()
    api_instance.create_namespaced_deployment(
        namespace="default",
        body=deployment
    )

    return {"message": f"Deployment '{deployment_name}' created successfully"}

@app.get("/getPromdetails")
def get_prometheus_details():
    # Fetch the Prometheus metrics
    prom = Prometheus('http://localhost:9090')
    metrics = prom.query('kube_pod_info')

    return {"metrics": metrics}
