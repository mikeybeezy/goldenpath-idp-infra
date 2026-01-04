---
id: enable-efs
title: Enable EFS for WordPress on EKS
type: documentation
category: apps
version: 1.0
owner: platform-team
status: active
dependencies:
  - module:efs
  - module:vpc
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: manual
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - WORDPRESS_ON_EFS_README
  - STATEFUL_APP_ON_EFS
  - STATEFUL_APP_PVC
---

# click through AWS console to create EFS

login to AWS console and search for service _EFS_
click through wizard , use our course VPC and all 3 AZs
_specify the security group of your EC2-worker-nodes, to be applied to EFS as well_

# add amazon-efs-utils

install the package _amazon-efs-utils_ on all worker nodes

```
ssh -i <<eks-course.pem>> ec2-user@<<ec2-workernode>> "sudo yum install -y amazon-efs-utils"
```
