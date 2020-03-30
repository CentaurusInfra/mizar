When creating any object, there are **two states** that must persist to the API
Server. These states are **Object Init** and **Object Provisioned**. Any other
state may be communicated between operators by the Inter-Operators Communication
methods mentioned previously.

An object's state may be *watched* by many operators, that will take specific
actions when the state is changed. However, a general guideline is, only **one
operator** may mutate the state of any given object per state. For example, when
a  VPC object is in state **Init**, there is only one Operator that may mutate
its state to **Provisioned**, which is the VPC Operator.

### Workflow management

Mizar uses [luigi](https://github.com/spotify/luigi) to schedule and execute
parallel workflows. The operator runs a central scheduler that execute the
workflows.

### VPC Object Create Workflow

#### Triggers:
1. User creates a VPC
1. VPC Operator creates a default VPC

![VPC](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/create_vpc_workflow.puml)

1. The VPC Operator sees that a VPC has been created with status, **Init**.
2. The VPC Operator creates a Divider Object and persists its state to the API
   Server.
3. The Droplet Operator sees that a Divider has been created with status,
   **Init**.
4. The Droplet Operator picks a droplet to place the Divider on..
5. The Droplet Operator calls tells the Bouncer Operator that it has placed the
   Divider.
6. The Bouncer Operator Updates all Bouncers with the new Divider. (Note: there
   are currently no Bouncers.)
7. The Bouncer Operator updates the Divider object with all Bouncers. (Note:
   there are currently no Bouncers.)
8. The Bouncer Operator updates the status of the Divider to **Provisioned** and
   persists its state to the API Server.
9. The Divider Operator sees that the Divider Object is now Provisioned.
10. The Divider Operator updates its state store with the newly provisioned
    Divider Object.
11. The VPC Operator sees that the Divider has been provisioned.
12. The VPC Operator updates the state of the VPC to **Provisioned** and
    persists its state to the API Server.

### Network Object Create Workflow

#### Triggers:
1. User creates a network
1. Network operator creates a default network

![Net](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/create_network_workflow.puml)

1. The Network Operator sees that a Network Object has been created with status,
   **Init**.
2. The Network Operator creates a Bouncer Object with state **Init** and
   persists its state to the API Server.
3. The Droplet Operator sees that a new Bouncer has been created.
4. The Droplet Operator picks a Droplet to place the Bouncer on.
5. The Droplet Operator tells the Endpoint Operator that a Bouncer has been
   placed.
6. The Endpoint Operator updates the newly created Bouncer with all Endpoints in
   the Network. (Note: There are currently no Endpoints)
7. The Endpoint Operator tells the Divider Operator that the Bouncer is
   "Endpoint-Ready"
8. The Divider Operator updates the Bouncer with all Dividers in the VPC.
9. The Divider Operator updates all Dividers with the new Bouncer.
10. The Divider Operator updates the status of the Bouncer Object to
    **Provisioned** and persists its state to the API Server.
11. The Bouncer Operator sees that the Bouncer has been provisioned.
12. The Bouncer Operator updates its own state store with the newly provisioned
    Bouncer.
13. The Endpoint Operator sees that the Bouncer status is now Provisioned.
14. The Endpoint Operator updates all Endpoints with the new Bouncer (Note:
    There are currently no Endpoints)
15. The Network Operator sees that the Bouncer is Provisioned.
16. The Network Operator updates the status of the Network Object to
    **Provisioned** and persists its state to the API Server.


### Endpoint Object Create Workflow

#### Triggers:
1. User creates a POD.
1. User creates a Mizar endpoint. Note: It is still possible to explicitly
   create a Mizar endpoint, but this is not a typical usage within a Kubernetes
   cluster. We don't have qa mechanism to prevent a user from creating a Mizar
   endpoint that is not attached to a POD.

![Endpoint](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/create_endpoint_workflow.puml)

1. The Network Operator sees that an Endpoint Object with state **Init** has
   been created.
2. The Network Operator allocates an ip address, gw, etc for the newly created
   Endpoint.
3. The Network Operator tells the Bouncer Operator that an Endpoint has been
   created.
4. The Bouncer Operator updates all Bouncers with the newly created Endpoint.
5. The Endpoint Operator updates the newly created Endpoint with all Bouncers in
   the Network.
6. The Bouncer Operator tells the CNI Service that the Endpoint has been
   provisioned.
7. The CNI Services writes to a file all of the Endpoint information.
8. The Bouncer Operator updates the status of the Endpoint to **Provisioned**
   and persists its state to the API Server.
9. The Endpoint Operator sees that the Endpoint's state is now provisioned.
10. The Endpoint Operator updates its own state store with the newly provisioned
    Endpoint.

### Scaled Endpoint Object Create Workflow

#### Triggers:
1. User creates a service.

![Scaled_Endpoint](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/create_scaled_endpoint_workflow.puml)

1. The Endpoint Operator is notified that a Scaled Endpoint has been created
2. The Endpoint Operator allocates an IP, mac, etc, for the new Scaled Endpoint Object
3. The Endpoint Operator creates the Scaled Endpoint Object

### Scaled Endpoint Object Update Workflow

#### Triggers:
1. Backend added or removed from scaled endpoint.

![Scaled_Endpoint](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/update_scaled_endpoint_workflow.puml)

1. The Scaled Endpoint object is updated with Endpoint Objects as its backends
2. The Endpoint Operator updates its cache with this change about the Scaled Endpoint Object
3. The Endpoint Operator calls back to the Bouncer Operator that the Scaled Endpoint has been updated with backends
4. The Bouncer Operator updates all Bouncers about the new Scaled Endpoint
5. The Bouncer Operator updates the Scaled Endpoint with all Bouncers in the Network

### Divider Object Create Workflow (Mizar Specific)

#### Triggers:
1. The VPC operator creates a divider. Initially when the VPC is created or
   during a divider scale out.

![Divider](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/create_divider_workflow.puml)

1. The VPC Operator creates a new Divider with state **Init** and persists it to
   the API Server.
2. The Droplet Operator sees that a Divider has been created with status,
   **Init**.
3. The Droplet Operator picks a droplet to place the Divider on..
4. The Droplet Operator calls tells the Bouncer Operator that it has placed the
   Divider.
5. The Bouncer Operator Updates all Bouncers with the new Divider.
6. The Bouncer Operator updates the Divider object with all Bouncers.
7. The Bouncer Operator updates the status of the Divider to **Provisioned** and
   persists its state to the API Server.
8. The Divider Operator sees that the Divider Object is now Provisioned.
9. The Divider Operator updates its state store with the newly provisioned
   Divider Object.

### Bouncer Object Create Workflow (Mizar Specific)

#### Triggers:
1. The network oeprator creates a bouncers. Initially when the Network is
   created or during a bouncer scale out.

![Bouncer](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/create_bouncer_workflow.puml)

1. The Network Operator creates a new Bouncer Object with state **Init** and
   persists it to the API Server.
2. The Droplet Operator sees that a new Bouncer has been created.
3. The Droplet Operator picks a Droplet to place the Bouncer on.
4. The Droplet Operator tells the Endpoint Operator that a Bouncer has been
   placed.
5. The Endpoint Operator updates the newly created Bouncer with all Endpoints in
   the Network. (Note: There are currently no Endpoints)
6. The Endpoint Operator tells the Divider Operator that the Bouncer is
   "Endpoint-Ready"
7. The Divider Operator updates the Bouncer with all Dividers in the VPC.
8. The Divider Operator updates all Dividers with the new Bouncer.
9. The Divider Operator updates the status of the Bouncer Object to
   **Provisioned** and persists its state to the API Server.
10. The Bouncer Operator sees that the Bouncer has been provisioned.
11. The Bouncer Operator updates its own state store with the newly provisioned
    Bouncer.
12. The Endpoint Operator sees that the Bouncer status is now Provisioned.
13. The Endpoint Operator updates all Endpoints with the new Bouncer (Note:
    There are currently no Endpoints)

### Droplet Object Create Workflow

#### Triggers:
1. The transit daemon creates the droplet object during bootstrapping


![Droplet](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/create_droplet_workflow.puml)

1. The CNI Services creates A Droplet Object with state **Init** for each Node
   and persists them to the API Server.
2. The Droplet Operator sees that a new Droplet has been created.
3. The Droplet Operator updates its state store cache with the Droplet.
4. The Droplet Operator updates the status of the Droplet to **Provisioned** and
   persists its state to the API Server.
5. The Droplet Operator sees that the Droplet is now Provisioned.
6. The Droplet Operator updater its state store with the Droplet.


### VPC Object Delete Workflow

#### Triggers:
1. User deletes a VPC

![VPC](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/delete_vpc_workflow.puml)

1. The VPC Operator sees the delete request for the VPC Object.
2. The VPC Operator will not delete the VPC unless all of the specified VPC's children Networks have been deleted.
3. The Network Operator calls back to the Divider Operator after all Networks have been deleted.
4. The Divider Operator deletes all Dividers in the VPC.
5. The Divider Operator removes all Dividers in the VPC from its cache.
6. The Divider Operator calls back to the VPC Operator after all Dividers have been deleted.
7. The VPC Operator Deletes the VPC Object.
8. The VPC Operator remoes the VPC object from its cache

### Network Object Delete Workflow

#### Triggers:
1. User deletes a Network

![Network](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/delete_network_workflow.puml)

1. The Network Operator sees a Network delete request
2. The Network Operator will not delete the Network unless all of the specified Network's children Endpoints have been deleted.
3. The Network Operator calls back to the Divider Operator after all Endpoints have been deleted.
4. The Divider Operator deletes all Divider information from all Bouncers.
5. The Divide Operator deletes all Bouncer information from the Dividers
6. The Divider calls back to the Bouncer Operator after all Bouncers have been deprovisioned.
7. The Bouncer Operator deletes all Bouncer Objects in the Network.
8. The Bouncer Operator removes all Bouncer Objects in the Network from its cache.
9. The Bouncer Operator calls back to the Network Operator that all Bouncers in the Network have been deleted.
10. The Network Operator deletes the Network Object.
11. The Network Operator removes the Network object from its cache.

### Endpoint Object Delete Workflow

#### Triggers:
1. User deletes the POD atttaching the endpoint

![Endpoint](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/delete_endpoint_workflow.puml)

1. The CNI Services sees the Endpoint Delete request.
2. The CNI service deletes the Endpoint Object.
3. The Network Operator sees the Endpoint Delete request.
4. The Network operator deallocates the Endpoints information (IP, MAC, etc).
5. The Network Operator calls back to the Bouncer Operator after the Endpoint has been deallocated.
6. The Bouncer Operator deletes the Endpoint information from all Bouncers.
7. The Bouncer Operator deletes all Bouncer information from the Endpoint.
8. The Bouncer Operator calls back to the Endpoint Operator.
9. The Endpoint Operator deletes the Endpoint Object from its cache.

### Scaled Endpoint Object Delete Workflow

#### Triggers:
1. User deletes the service.

![Scaled_Endpoint](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/delete_scaled_endpoint_workflow.puml)

1. The Endpoints Operator sees the Scaled Endpoint Delete request.
2. The Endpoint operator deallocates the Scaled Endpoints information (IP, MAC, etc).
3. The Endpoints Operator calls back to the Bouncer Operator after the Scaled Endpoint has been deallocated.
4. The Bouncer Operator deletes the Scaled Endpoint information from all Bouncers.
5. The Bouncer Operator deletes all Bouncer information from the Scaled Endpoint.
6. The Bouncer Operator calls back to the Endpoint Operator.
7. The Endpoint Operator deletes the Scaled Endpoint Object.
8. The Endpoint Operator deletes the Scaled Endpoint Object from its cache.

### Divider Object Delete Workflow

#### Triggers:
1. User deletes the VPC of the divider
1. The VPC operator scales down the number of dividers

![Divider](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/delete_divider_workflow.puml)

1. The Divider Operator sees the Divider delete request.
2. The Divider Operator calls back to the Bouncer Operator
3. The Bouncer Operator deletes all Bouncer information from the Divider.
4. The Bouncer Operator delets all Divider information from the Bouncers.
5. The Bouncer Operator calls back to the Divider Operator after the Divider has been deprovisioned.
6. The Divider Operator deletes the Divider Object.
7. The Divider Operator deletes the Divider Object from its cache.

### Bouncer Object Delete Workflow

#### Triggers:
1. User deletes the Network of the bouncer
1. The network operator scales down the number of bouncers


![Bouncer](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/futurewei-cloud/mizar/dev-next/docs/design/puml/delete_bouncer_workflow.puml)

1. The Bouncer Operator sees the delete request for the Bouncer.
2. The Bouncer Operator calls back to the Endpoint Operator.
3. The Endpoint Operator deletes all Bouncer information from the Endpoint.
4. The Endpoint Operator deletes all Endpoint information from the Bouncer.
5. The Endpoint Operator calls back to the Divider Operator.
6. The Divider Operator deletes the Bouncer information from all Dividers.
7. The Divider Operator deletes all Divider information from the Bouncer.
8. The Divider Operator calls back to the Bouncer Operator.
9. The Bouncer Operator deletes the Bouncer Object.
10. The Bouncer Operator deletes the Bouncer Object from its cache.