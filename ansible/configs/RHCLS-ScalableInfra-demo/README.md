# RHCLS_ScalableInfrastructure

This is a set of playbooks that can be used for deploying Red Hat Cloud Suite's Scalable Infrastructure demonstration. The Scalable Infrastructure demonstration.

=== Overview
This is demonstration of how Red Hat is delivering scalable infrastructure with the capabilities that enterprises demand. Red Hat OpenStack Platform delivers scale-out private cloud capabilities with a stable lifecycle and large ecosystem of supported hardware platforms. Many organizations are building their next generation cloud infrastructures on OpenStack because it provides an asynchronous architecture and is API centric allowing for greater scale and greater efficiency in platform management. OpenStack does not, however, provide functionality such as chargeback, reporting, and policy driven automation for tenant workloads and those projects that aspire to do so are generally focused solely on OpenStack. This is not realistic in an increasingly hybrid world – and enterprises that are serious about OpenStack need these capabilities. By using Red Hat CloudForms together with Red Hat OpenStack Platform it’s possible to provide capabilities such as reporting, chargeback, and auditing of tenant workloads across a geographically diverse deployment. In the demo we demonstrate how chargeback across a multi-site OpenStack deployment works.

=== Structure
 * ./env holds playbooks for creating environments. For example, creating a blueprint in Ravello or heatstack on OpenStack.
 * ./cfg holds playbooks for configuring the demonstration on the created environments.
