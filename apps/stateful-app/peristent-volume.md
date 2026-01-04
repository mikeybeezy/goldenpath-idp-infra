---
id: STATEFUL_APP_PVC
title: Persistent Volume Claims for Stateful Apps
type: documentation
category: apps
version: 1.0
owner: platform-team
status: active
dependencies:
  - module:ebs
  - module:kubernetes
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: kubectl-delete
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - STATEFUL_APP_README
  - STATEFUL_APP_NAMESPACE
  - STATEFUL_APP_DEPLOY
---

# persistent volume

in AWS EKS a persistent volume (PV) is implemented via a EBS volume, which has to be declared as a _storage class_ first.
A stateful app can then request a volume, by specifying a _persistent volume claim_ (PVC) and mount it in its corresponding pod.

## **!!Only execute step 1. if you are running Kubernetes version 1.10 in EKS...which is outdated. Since Jan 2019 EKS is using v1.11 and the gp2 storageclass is created automatically there...by default!!**

>    1. define a storage class
>    ```
>    kubectl apply -f gp2-storage-class.yaml --namespace=ns-eks-course
>    ```
>    If you receive the following error, then there is already gp2 storageclass available and you can skip above command:
>
>>    *The StorageClass "gp2" is invalid:*
>>    *parameters: Forbidden: updates to parameters are forbidden.*
>>    *reclaimPolicy: Forbidden: updates to reclaimPolicy are forbidden.*
>
>    ...and set this storage class as *default* !
>    check current situation:
>    ```
>    kubectl get storageclasses --namespace=ns-eks-course
>    ```
>    set default:
>    ```
>    kubectl patch storageclass gp2 -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}' --namespace=ns-eks-course
>    ```
>    check again:
>    ```
>    kubectl get storageclasses --namespace=ns-eks-course
>    ```

2. define a persistent volume claim
```
kubectl apply -f pvcs.yaml --namespace=ns-eks-course
```
and check:
```
kubectl get pvc --namespace=ns-eks-course
```
