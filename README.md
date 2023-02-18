## Techtrends


### Overview
TechTrends is an online website used as a news sharing platform, 
that enables consumers to access the latest news within the cloud-native ecosystem. 
In addition to accessing the available articles, readers are able to create new media articles and share them.

A flask application is packaged using docker, in a GitHub workflow using GitHub actions [link](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions), 
and is pushed to docker hub. 
This image is pulled from docker hub, and is deployed to a kubernetes cluster, the kubernetes cluster is running 
inside a vagrant box, the cluster is created using k3s [link](https://k3s.io/), and the deployments 
to the kubernetes cluster is handled by argocd [link](https://argo-cd.readthedocs.io/en/stable/),
using templated helm charts [link](https://helm.sh/).

There are separate helm charts for staging and production environments. 

Declarative manifests for kubernetes are also present in the `./kubernetes` folder.

### Technologies used
- Flask
- Docker
- kubernetes
- vagrant
- virtualbox
- k3s
- helm
- argocd
- sqlite
- GitHub actions
- docker hub

### Screenshots
#### Argocd production

<img width="750" alt="argocd-techtrends-prod" src="https://user-images.githubusercontent.com/19944703/219863730-d25341d8-b16e-4ac3-affa-248cc4e58edf.png">

### Argocd staging
<img width="750" alt="argocd-techtrends-staging" src="https://user-images.githubusercontent.com/19944703/219863765-b6be5b98-54ef-4748-a827-f2b6edf8d3bb.png">