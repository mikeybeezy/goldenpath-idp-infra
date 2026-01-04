---
id: deploy-stateful-app
title: Stateful Application Deployment (MySQL & WordPress)
type: documentation
category: apps
version: 1.0
owner: platform-team
status: active
dependencies:
- module:aws_eks
- module:kubernetes
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 09_ARCHITECTURE
---

# deploy mysql

## create secret which stores mysql pw, to be injected as env var into container

```
kubectl create secret generic mysql-pass --from-literal=password=eks-course-mysql-pw --namespace=ns-eks-course
```

check:

```
kubectl get secrets --namespace=ns-eks-course
```

## launch mysql deployment

```
kubectl apply -f deploy-mysql.yaml --namespace=ns-eks-course
```

## checks

* persistent volumes
* persistent volume claims
* pods

```
kubectl get pv --namespace=ns-eks-course
kubectl get pvc --namespace=ns-eks-course
kubectl get pods -o wide --namespace=ns-eks-course
```

* EBS volumes
goto AWS mgm console => EC2 => Elastic Block store => volumes

# deploy wordpress

```
kubectl apply -f deploy-wordpress.yaml --namespace=ns-eks-course
```

get URL of the app:

```
kubectl describe service wordpress --namespace=ns-eks-course | grep Ingress
```

or goto AWS console => EC2

# cleanup

delete Wordpress _deployment_

```
kubectl delete -f deploy-wordpress-by-deployment.yaml --namespace=ns-eks-course
kubectl delete -f deploy-wordpress-by-statefulset.yaml --namespace=ns-eks-course
```

delete MySQL _deployment_

```
kubectl delete -f deploy-mysql.yaml --namespace=ns-eks-course
```

delete EBS volumes
since we specified policy _retain_ for the pv's, we have to delete them manually after deleting the pods, which had them in use.
For that go to AWS mgm console => EC2 => Volumes => select and delete the detached ones
