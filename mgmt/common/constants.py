
# Constants
group = 'mizar.com'
version = 'v1'




class CONSTANTS:
    TRAN_SUBSTRT_EP = 0
    TRAN_SIMPLE_EP = 1
    TRAN_SCALED_EP = 2
    ON_XDP_TX       = "ON_XDP_TX"
    ON_XDP_PASS     = "ON_XDP_PASS"
    ON_XDP_REDIRECT = "ON_XDP_REDIRECT"
    ON_XDP_DROP     = "ON_XDP_DROP"
    ON_XDP_SCALED_EP = "ON_XDP_SCALED_EP"

class OBJ_STATUS:
	ep_status_init = 'init'
	ep_status_allocated = 'alloc'
	ep_status_ready = 'ready'
	ep_status_provisioned = 'provisioned'

	net_status_init = 'init'
	net_status_allocated = 'alloc'
	net_status_ready = 'ready'
	net_status_provisioned = 'provisioned'

	vpc_status_init = 'init'
	vpc_status_allocated = 'alloc'
	vpc_status_ready = 'ready'
	vpc_status_provisioned = 'provisioned'

	droplet_status_init = 'init'
	droplet_status_allocated = 'alloc'
	droplet_status_ready = 'ready'
	droplet_status_provisioned = 'provisioned'

	bouncer_status_init = 'init'
	bouncer_status_allocated = 'alloc'
	bouncer_status_ready = 'ready'
	bouncer_status_provisioned = 'provisioned'

	divider_status_init = 'init'
	divider_status_allocated = 'alloc'
	bouncer_status_ready = 'ready'
	bouncer_status_provisioned = 'provisioned'

class OBJ_DEFAULTS:
	default_ep_vpc = 'vpc0'
	default_ep_net = 'net0'
	default_ep_type = 'simple'
	default_vpc_vni = '0'
	default_net_ip = '10.0.0.0'
	default_net_prefix = '16'
	default_n_bouncers = 1
	default_n_dividers = 1

	ep_type_simple = 'simple'
	ep_type_scaled = 'scaled'

class RESOURCES:
	endpoints = "endpoints"
	nets = "nets"
	vpcs = "vpcs"
	droplets = "droplets"
	bouncers = "bouncers"
	dividers = "dividers"

class LAMBDAS:
	ep_status_init = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.ep_status_init
	ep_status_allocated = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.ep_status_init
	ep_status_ready = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.ep_status_init
	ep_status_provisioned = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.ep_status_init

	net_status_init = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.net_status_init
	net_status_allocated = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.net_status_allocated
	net_status_ready = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.net_status_ready
	net_status_provisioned = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.net_status_provisioned

	vpc_status_init = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.vpc_status_init
	vpc_status_allocated = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.vpc_status_allocated
	vpc_status_ready = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.vpc_status_ready
	vpc_status_provisioned = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.vpc_status_provisioned

	droplet_status_init = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.droplet_status_init
	droplet_status_allocated = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.droplet_status_allocated
	droplet_status_ready = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.droplet_status_ready
	droplet_status_provisioned = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.droplet_status_provisioned

	bouncer_status_init = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.bouncer_status_init
	bouncer_status_allocated = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.bouncer_status_allocated
	bouncer_status_ready = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.bouncer_status_ready
	bouncer_status_provisioned = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.bouncer_status_provisioned

	divider_status_init = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.divider_status_init
	divider_status_allocated = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.divider_status_allocated
	bouncer_status_ready = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.bouncer_status_ready
	bouncer_status_provisioned = lambda body, **_: body.get('spec', {}).get('status', '') == OBJ_STATUS.bouncer_status_provisioned
