// Package main implements a client .
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	pb "mizar.com/crds-operator-proxy/grpc/vpcs"

	"google.golang.org/grpc"
)

const (
	address = "localhost:50051"
)

func main() {
	// Set up a connection to the server.
	conn, err := grpc.Dial(address, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	c := pb.NewVpcsServiceClient(conn)

	// Contact the server and request crd services.
	var arg string
	if len(os.Args) > 1 {
		arg = os.Args[1]
		fmt.Printf("Request %s", arg)
	} else {
		fmt.Print("Request service name is missing. example format: main.go create")
	}
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	var errorMessage error
	switch arg {
	case "create":
		_, err := c.CreateVpc(ctx, &pb.Vpc{Ip: "10.0.0.1", Prefix: "10.0.0.0/24", Vni: "16777210", Dividers: "1", Status: "active", CreateTime: "2020-07-20", ProvisionDelay: "10"})
		errorMessage = err
	case "update":
		_, err := c.UpdateVpc(ctx, &pb.Vpc{Ip: "10.0.0.1", Prefix: "10.0.0.0/24", Vni: "16777210", Dividers: "2", Status: "active", CreateTime: "2020-07-20", ProvisionDelay: "20"})
		errorMessage = err
	case "read":
		r, err := c.ReadVpc(ctx, &pb.VpcId{Id: "10.0.0.1"})
		log.Printf("Returned: %s", r.GetJsonReturncode())
		errorMessage = err
	case "delete":
		_, err := c.DeleteVpc(ctx, &pb.VpcId{Id: "10.0.0.1"})
		errorMessage = err
	case "resume":
		_, err := c.ResumeVpc(ctx, &pb.VpcId{Id: "10.0.0.1"})
		errorMessage = err
	}

	if err != nil {
		log.Fatalf("could not greet: %v", errorMessage)
	}
	log.Printf("Returned Client")
}
