
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

class EP_CONSTANTS:
	ep_status_init = 'init'
	ep_status_allocated = 'alloc'
	ep_status_ready = 'ready'
	ep_status_provisioned = 'provisioned'
	default_ep_vpc = 'vpc0'
	default_ep_net = 'net0'
	default_ep_type = 'simple'
	default_vpc_vni = 0

	ep_type_simple = 'simple'
	ep_type_scaled = 'scaled'
