---
id: enable-efs
title: click through AWS console to create EFS
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# click through AWS console to create EFS
login to AWS console and search for service _EFS_
click through wizard , use our course VPC and all 3 AZs
*specify the security group of your EC2-worker-nodes, to be applied to EFS as well*

# add amazon-efs-utils
install the package *amazon-efs-utils* on all worker nodes


```
ssh -i <<eks-course.pem>> ec2-user@<<ec2-workernode>> "sudo yum install -y amazon-efs-utils"
```
