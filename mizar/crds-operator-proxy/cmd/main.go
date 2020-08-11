package main

import (
	"fmt"

	"k8s.io/klog"
	vpccontroller "mizar.com/crds-operator-proxy/crds/vpcs/controller"
	bouncercontroller "mizar.com/crds-operator-proxy/crds/bouncers/controller"
	dividercontroller "mizar.com/crds-operator-proxy/crds/dividers/controller"
	dropletcontroller "mizar.com/crds-operator-proxy/crds/droplets/controller"
	endpointcontroller "mizar.com/crds-operator-proxy/crds/endpoints/controller"
	netcontroller "mizar.com/crds-operator-proxy/crds/nets/controller"
)

func main() {
	
		//vpcs
		vpcproxy := vpccontroller.NewController()
		vpcproxy.CreateCRD()
		if err := vpcproxy.CreateObject(); err != nil {
			klog.Infoln(err)
		}

		fmt.Print("vpc proxy starts")
		vpcproxy.Run()
	
		//bouncers
		bouncerproxy := bouncercontroller.NewController()
		bouncerproxy.CreateCRD()
		if err := bouncerproxy.CreateObject(); err != nil {
			klog.Infoln(err)
		}
		fmt.Print("bouncer proxy starts")
		bouncerproxy.Run()
	
	//dividers
	dividerproxy := dividercontroller.NewController()
	dividerproxy.CreateCRD()
	if err := dividerproxy.CreateObject(); err != nil {
		klog.Infoln(err)
	}
	fmt.Print("divider proxy starts")
	dividerproxy.Run()
	
	//droplets
	dropletproxy := dropletcontroller.NewController()
	dropletproxy.CreateCRD()
	if err := dropletproxy.CreateObject(); err != nil {
		klog.Infoln(err)
	}
	fmt.Print("droplet proxy starts")
	dropletproxy.Run()
        
	//endpoints
	endpointproxy := endpointcontroller.NewController()
	endpointproxy.CreateCRD()
	if err := endpointproxy.CreateObject(); err != nil {
		klog.Infoln(err)
	}
	fmt.Print("endpoint proxy starts")
	endpointproxy.Run()
	
	//nets
	netproxy := netcontroller.NewController()
	netproxy.CreateCRD()
	if err := netproxy.CreateObject(); err != nil {
		klog.Infoln(err)
	}
	fmt.Print("net proxy starts")
	netproxy.Run()
	
}

