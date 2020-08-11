package main

import (
	"fmt"

	"k8s.io/klog"
	//vpccontroller "mizar.com/crds-operator-proxy/crds/vpcs/controller"
          bouncercontroller "mizar.com/crds-operator-proxy/crds/bouncers/controller"
)

func main() {
/*
	//vpcs
	vpcproxy := vpccontroller.NewController()
	vpcproxy.CreateCRD()
	if err := vpcproxy.CreateObject(); err != nil {
		klog.Infoln(err)
	}

	fmt.Print("vpc proxy starts")
	vpcproxy.Run()
*/
	//bouncers
	bouncerproxy := bouncercontroller.NewController()
	bouncerproxy.CreateCRD()
	if err := bouncerproxy.CreateObject(); err != nil {
		klog.Infoln(err)
	}
	fmt.Print("bouncer proxy starts")
	bouncerproxy.Run()
}

