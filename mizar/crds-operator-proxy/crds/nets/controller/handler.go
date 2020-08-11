package controller

import (
	"context"
	"fmt"
	"log"
	"time"

	"google.golang.org/grpc"

	corev1 "k8s.io/api/core/v1"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	"k8s.io/client-go/tools/cache"
	"k8s.io/klog"
	netv1 "mizar.com/crds-operator-proxy/crds/nets/apis/v1"
	pb "mizar.com/crds-operator-proxy/grpc/netss"
)

const (
	address1      = "localhost:50051"
	statusMessage = "HANDLED"
	CREATE        = 1
	UPDATE        = 2
	DELETE        = 3
	READ          = 4
	RESUME        = 5
)

// Run first sync client-go cache by calling cache.WaitforCacheSync,
// then block the main thread forever.
// Event handler will run in another Goroutine,
// generated in c.NewController() function.
func (c *Controller) Run() {
	defer utilruntime.HandleCrash()
	defer c.workqueue.ShutDown()

	klog.Infoln("Waiting cache to be synced.")
	// Handle timeout for syncing.
	timeout := time.NewTimer(time.Second * 30)
	timeoutCh := make(chan struct{})
	go func() {
		<-timeout.C
		timeoutCh <- struct{}{}
	}()
	if ok := cache.WaitForCacheSync(timeoutCh, c.informer.HasSynced); !ok {
		klog.Fatalln("Timeout expired during waiting for caches to sync.")
	}

	klog.Infoln("Starting custom controller.")
	select {}
}

func (c *Controller) objectAddedCallback(object interface{}) {
	resource := object.(*netv1.Net)
	klog.Infof("Added: %v", resource)
	// If the object is in the desired state, end callback.
	if resource.Status == statusMessage {
		return
	}

	// If the object is not handled yet, handle it by modifying its Status.
	copy := resource.DeepCopy()
	copy.Status = statusMessage
	_, err := c.vpcclientset.MizarV1().Nets(corev1.NamespaceDefault).Update(copy)
	if err != nil {
		klog.Errorf(err.Error())
		return
	}
	gRPCRequest(CREATE, object)

	c.recorder.Event(copy, corev1.EventTypeNormal, "ObjectHandled", "Object is handled by custom controller.")
}

func (c *Controller) objectUpdatedCallback(oldObject, newObject interface{}) {
	//klog.Infof("Updated: %v", object)
	resource := newObject.(*netv1.Net)
	klog.Infof("Updated: %v", resource)
	gRPCRequest(UPDATE, newObject)
	// If the object is in the desired state, end callback.
	if resource.Status == statusMessage {
		return
	}

	// If the object is not handled yet, handle it by modifying its Status.
	copy := resource.DeepCopy()
	copy.Status = statusMessage
	_, err := c.netclientset.MizarV1().Nets(corev1.NamespaceDefault).Update(copy)
	if err != nil {
		klog.Errorf(err.Error())
		return
	}

	c.recorder.Event(copy, corev1.EventTypeNormal, "ObjectHandled", "Object is handled by custom controller.")
}

func (c *Controller) objectDeletedCallback(object interface{}) {
	//klog.Infof("Deleted: %v", object)
	resource := object.(*netv1.Net)
	klog.Infof("Deleted: %v", resource)
	// If the object is in the desired state, end callback.
	if resource.Status == statusMessage {
		return
	}

	// If the object is not handled yet, handle it by modifying its Status.
	copy := resource.DeepCopy()
	copy.Status = statusMessage
	_, err := c.netclientset.MizarV1().Nets(corev1.NamespaceDefault).Update(copy)
	if err != nil {
		klog.Errorf(err.Error())
		return
	}
	gRPCRequest(DELETE, object)

	c.recorder.Event(copy, corev1.EventTypeNormal, "ObjectHandled", "Object is handled by custom controller.")
}

func gRPCRequest(command int, object interface{}) {
	// Set up a connection to the server.
	fmt.Println("command=%d", command)
	conn, err := grpc.Dial(address1, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	clientcon := pb.NewNetsServiceClient(conn)
	// Contact the server and request crd services.
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	switch command {
	case CREATE:
		_, err = clientcon.CreateNet(ctx, object)
	case UPDATE:
		_, err = clientcon.UpdateNet(ctx, object)
	case DELETE:
		_, err = clientcon.DeleteNet(ctx, object)
	case READ:
		var response string
		response, err = clientcon.ReadNet(ctx, object)
		log.Printf("Read Net: %s", response)
	case RESUME:
		_, err = clientcon.ResumeNet(ctx, object)
	default:
		log.Println("command is not correct")
	}
	//errorMessage = err
	if err != nil {
		log.Fatalf("could not create: %v", err)
	}
	log.Printf("Returned Client")
}
