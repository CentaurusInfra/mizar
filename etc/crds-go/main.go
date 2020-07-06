package main

import (
	"flag"
	"time"

	"v1alpha1"

	"github.com/golang/glog"
	apiextension "k8s.io/apiextensions-apiserver/pkg/client/clientset/clientset"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	clientcmdapi "k8s.io/client-go/tools/clientcmd/api"
)

var (
	// Set during build
	version  string
	proxyURL = flag.String("proxy", "", "usage: kubectl proxy is runnung")
)

func main() {

	flag.Parse()
	var err error

	var config *rest.Config
	if *proxyURL != "" {
		config, err = clientcmd.NewNonInteractiveDeferredLoadingClientConfig(
			&clientcmd.ClientConfigLoadingRules{},
			&clientcmd.ConfigOverrides{
				ClusterInfo: clientcmdapi.Cluster{
					Server: *proxyURL,
				},
			}).ClientConfig()
		if err != nil {
			glog.Fatalf("error creating client configuration: %v", err)
		}
	} else {
		if config, err = rest.InClusterConfig(); err != nil {
			glog.Fatalf("error creating client configuration: %v", err)
		}
	}

	kubeClient, err := apiextension.NewForConfig(config)
	if err != nil {
		glog.Fatalf("Failed to create client: %v", err)
	}
	// Create the CRD
	err = v1alpha1.CreateCRD(kubeClient)
	if err != nil {
		glog.Fatalf("Failed to create crd: %v", err)
	}

	// Wait for the CRD to be created before we use it.
	time.Sleep(5 * time.Second)

	// Create a new clientset which include our CRD schema
	crdclient, err := v1alpha1.NewClient(config)
	if err != nil {
		panic(err)
	}
	// Create a new vpcs object

}
