package main

import (
	"os"
	"time"

	corev1 "k8s.io/api/core/v1"
	apiextensionsclientset "k8s.io/apiextensions-apiserver/pkg/client/clientset/clientset"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	"k8s.io/apimachinery/pkg/util/wait"
	"k8s.io/client-go/kubernetes"
	typedcorev1 "k8s.io/client-go/kubernetes/typed/core/v1"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/tools/record"
	"k8s.io/client-go/util/workqueue"
	"k8s.io/klog"

	vpcclienteset "mizar.futurewei.com/crds-operators/vpcs/v1/apis/clientset/versioned"
	vpcscheme "mizar.futurewei.com/crds-operators/vpcs/v1/apis/clientset/versioned/scheme"
	vpcinformers "mizar.futurewei.com/crds-operators/vpcs/v1/apis/informers/externalversions"
)

type Controller struct {
	kubeclientset          kubernetes.Interface
	apiextensionsclientset apiextensionsclientset.Interface
	vpcclientset           vpcclienteset.Interface
	informer               cache.SharedIndexInformer
	lister                 vpclisters.vpcLister
	recorder               record.EventRecorder
	workqueue              workqueue.RateLimitingInterface
}

func NewController() *Controller {
	kubeconfig := os.Getenv("KUBECONFIG")

	config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
	if err != nil {
		klog.Fatalf(err.Error())
	}

	kubeClient := kubernetes.NewForConfigOrDie(config)
	apiextensionsClient := apiextensionsclientset.NewForConfigOrDie(config)
	testClient := vpcclienteset.NewForConfigOrDie(config)

	informerFactory := vpcinformers.NewSharedInformerFactory(testClient, time.Minute*1)
	informer := informerFactory.Insujang().V1beta1().vpcs()

	utilruntime.Must(vpcv1beta1.AddToScheme(vpcscheme.Scheme))
	eventBroadcaster := record.NewBroadcaster()
	eventBroadcaster.StartLogging(klog.Infof)
	eventBroadcaster.StartRecordingToSink(&typedcorev1.EventSinkImpl{Interface: kubeClient.CoreV1().Events("")})
	recorder := eventBroadcaster.NewRecorder(vpcscheme.Scheme, corev1.EventSource{Component: "vpc-controller"})

	workqueue := workqueue.NewRateLimitingQueue(workqueue.DefaultControllerRateLimiter())

	c := &Controller{
		kubeclientset:          kubeClient,
		apiextensionsclientset: apiextensionsClient,
		vpcclientset:           testClient,
		informer:               informer.Informer(),
		lister:                 informer.Lister(),
		recorder:               recorder,
		workqueue:              workqueue,
	}

	informer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: c.objectAddedCallback,
		UpdateFunc: func(oldObject, newObject interface{}) {
			klog.Infof("Updated: %v", newObject)
		},
		DeleteFunc: func(object interface{}) {
			klog.Infof("Deleted: %v", object)
		},
	})
	informerFactory.Start(wait.NeverStop)

	return c
}
