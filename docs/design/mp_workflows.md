
## Mizar Management Workflows

When creating any object, there are **two states** that must be persisted to the API Server.

These states are **Object Init** and **Object Provisioned**.
Any other states may be communicated between  operators by the Inter-Operators Communication methods mentioned previously.

An object's state may be *watched* by many operators, that will take certain actions when the state is changed.
However, a general guidline is, only **one operator** may mutate the state of any given object per state.

For example:
   1. A VPC object is in state **Init**
   2. There is only one Operator that may mutate its state to the next state of **Provisioned**, the VPC Operator.

When creating any object, there are **two states** that must be persisted to the API Server.

These states are **Object Init** and **Object Provisioned**.
Any other states may be communicated between  operators by the Inter-Operators Communication methods mentioned previously.

An object's state may be *watched* by many operators, that will take certain actions when the state is changed.
However, a general guidline is, only **one operator** may mutate the state of any given object per state.

For example:
   1. A VPC object is in state **Init**
   2. There is only one Operator that may mutate its state to the next state of **Provisioned**, the VPC Operator.

### VPC Object Create Workflow


![VPC](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/create_vpc_workflow.puml)

1. The VPC Operator sees that a VPC has been created with status, **Init**.
2. The VPC Operator creates a Divider Object and persists its state to the API Server.
3. The Droplet Operator sees that a Divider has been created with status, **Init**.
4. The Droplet Operator picks a droplet to place the Divider on..
5. The Droplet Operator calls tells the Bouncer Operator that it has placed the Divider.
6. The Bouncer Operator Updates all Bouncers with the new Divider. (Note: there are currently no Bouncers.)
7. The Bouncer Operator updates the Divider object with all Bouncers. (Note: there are currently no Bouncers.)
8. The Bouncer Operator updates the status of the Divider to **Provisioned** and persists its state to the API Server.
9. The Divider Operator sees that the Divider Object is now Provisioned.
10. The Divider Operator updates its state store with the newly provisioned Divider Object.
11. The VPC Operator sees that the Divider has been provisioned.
12. The VPC Operator updates the state of the VPC to **Provisioned** and persists its state to the API Server.

### Network Object Create Workflow

![Net](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/create_network_workflow.puml)

1. The Network Operator sees that a Network Object has been created with status, **Init**.
2. The Network Operator creates a Bouncer Object with state **Init** and persists its state to the API Server.
3. The Droplet Operator sees that a new Bouncer has been created.
4. The Droplet Operator picks a Droplet to place the Bouncer on.
5. The Droplet Operator tells the Endpoint Operator that a Bouncer has been placed.
6. The Endpoint Operator updates the newly created Bouncer with all Endpoints in the Network. (Note: There are currently no Endpoints)
7. The Endpoint Operator tells the Divider Operator that the Bouncer is "Endpoint-Ready"
8. The Divider Operator updates the Bouncer with all Dividers in the VPC.
9. The Divider Operator updates all Dividers with the new Bouncer.
10. The Divider Operator updates the status of the Bouncer Object to **Provisioned** and persists its state to the API Server.
11. The Bouncer Operator sees that the Bouncer has been provisioned.
12. The Bouncer Operator updates its own state store with the newly provisioned Bouncer.
13. The Endpoint Operator sees that the Bouncer status is now Provisioned.
14. The Endpoint Operator updates all Endpoints with the new Bouncer (Note: There are currently no Endpoints)
15. The Network Operator sees that the Bouncer is Provisioned.
16. The Network Operator updates the status of the Network Object to **Provisioned** and persists its state to the API Server.


### Endpoint Object Create Workflow

![Endpoint](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/create_endpoint_workflow.puml)

1. The Network Operator sees that an Endpoint Object with state **Init** has been created.
2. The Network Operator allocates an ip address, gw, etc for the newly created Endpoint.
3. The Network Operator tells the Bouncer Operator that an Endpoint has been created.
4. The Bouncer Operator updates all Bouncers with the newly created Endpoint.
5. The Endpoint Operator updates the newly created Endpoint with all Bouncers in the Network.
6. The Bouncer Operator tells the CNI Service that the Endpoint has been provisioned.
7. The CNI Services writes to a file all of the Endpoint information.
8. The Bouncer Operator updates the status of the Endpoint to **Provisioned** and persists its state to the API Server.
9. The Endpoint Operator sees that the Endpoint's state is now provisioned.
10. The Endpoint Operator updates its own state store with the newly provisioned Endpoint.

### Divider Object Create Workflow (Mizar Specific)

![Divider](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/create_divider_workflow.puml)

1. The VPC Operator creates a new Divider with state **Init** and persists it to the API Server.
2. The Droplet Operator sees that a Divider has been created with status, **Init**.
3. The Droplet Operator picks a droplet to place the Divider on..
4. The Droplet Operator calls tells the Bouncer Operator that it has placed the Divider.
5. The Bouncer Operator Updates all Bouncers with the new Divider.
6. The Bouncer Operator updates the Divider object with all Bouncers.
7. The Bouncer Operator updates the status of the Divider to **Provisioned** and persists its state to the API Server.
8. The Divider Operator sees that the Divider Object is now Provisioned.
9. The Divider Operator updates its state store with the newly provisioned Divider Object.

### Bouncer Object Create Workflow (Mizar Specific)

![Bouncer](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/create_bouncer_workflow.puml)

1. The Network Operator creates a new Bouncer Object with state **Init** and persists it to the API Server.
2. The Droplet Operator sees that a new Bouncer has been created.
3. The Droplet Operator picks a Droplet to place the Bouncer on.
4. The Droplet Operator tells the Endpoint Operator that a Bouncer has been placed.
5. The Endpoint Operator updates the newly created Bouncer with all Endpoints in the Network. (Note: There are currently no Endpoints)
6. The Endpoint Operator tells the Divider Operator that the Bouncer is "Endpoint-Ready"
7. The Divider Operator updates the Bouncer with all Dividers in the VPC.
8. The Divider Operator updates all Dividers with the new Bouncer.
9. The Divider Operator updates the status of the Bouncer Object to **Provisioned** and persists its state to the API Server.
10. The Bouncer Operator sees that the Bouncer has been provisioned.
11. The Bouncer Operator updates its own state store with the newly provisioned Bouncer.
12. The Endpoint Operator sees that the Bouncer status is now Provisioned.
13. The Endpoint Operator updates all Endpoints with the new Bouncer (Note: There are currently no Endpoints)

### Droplet Object Create Workflow

![Droplet](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/create_droplet_workflow.puml)

1. The CNI Services creates A Droplet Object with state **Init** for each Node and persists them to the API Server.
2. The Droplet Operator sees that a new Droplet has been created.
3. The Droplet Operator updates its state store cache with the Droplet.
4. The Droplet Operator updats the status of the Droplet to **Provisioned** and persists its state to the API Server.
5. The Droplet Operator sees that the Droplet is now Provisioned.
6. The Droplet Operator updater its state store with the Droplet


### VPC Object Delete Workflow
![VPC](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/delete_vpc_workflow.puml)
### Network Object Delete Workflow
![Network](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/delete_network_workflow.puml)
### Endpoint Object Delete Workflow
![Endpoint](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/delete_endpoint_workflow.puml)
### Divider Object Delete Workflow
![Divider](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/delete_divider_workflow.puml)
### Bouncer Object Delete Workflow
![Bouncer](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/phudtran/mizar/dev-k8s/Documentation/design/figures/delete_bouncer_workflow.puml)