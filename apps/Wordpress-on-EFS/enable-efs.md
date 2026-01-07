---
id: enable-efs
title: Enable EFS for WordPress on EKS
type: documentation
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: manual
  observability_tier: silver
schema_version: 1
relates_to:
  - WORDPRESS_ON_EFS_README
  - STATEFUL_APP_ON_EFS
  - STATEFUL_APP_PVC
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: 1.0
dependencies:
  - module:efs
  - module:vpc
supported_until: 2028-01-01
breaking_change: false
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
