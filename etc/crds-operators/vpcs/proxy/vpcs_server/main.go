package main

import (
	"context"
	"log"
	"net"
	"fmt"
        pb "crds-operators/vpcs/proxy/vpcs"
	"google.golang.org/grpc"
)

const (
	port = ":50051"
)

// server is used to implement vpcs_proto.VpcsServer.
type server struct {
	pb.UnimplementedVpcsServiceServer
}

// services - CreateVpc
func (s *server) CreateVpc(ctx context.Context, in *pb.Vpc) (*pb.Empty, error) {
	log.Printf("Received Request - Create: %v", in.GetIp())
	return &pb.Empty{}, nil
}

// services - UpdateVpc
func (s *server) UpdateVpc(ctx context.Context, in *pb.Vpc) (*pb.Empty, error) {
	log.Printf("Received Request - Create: %v", in.GetIp())
	return &pb.Empty{}, nil
}

// services - ReadVpc
func (s *server) ReadVpc(ctx context.Context, in *pb.VpcIp) (*pb.VpcsResponse, error) {
	log.Printf("Received Request - Read: %v", in.GetIp())
        return &pb.VpcsResponse{JsonReturncode: "{Vpcs Response: " + in.GetIp()+"}"}, nil
}

// services - DeleteVpc
func (s *server) DeleteVpc(ctx context.Context, in *pb.VpcIp) (*pb.Empty, error) {
	log.Printf("Received Request - Delete: %v", in.GetIp())
	return &pb.Empty{}, nil
}

// services - ResumeVpc
func (s *server) ResumeVpc(ctx context.Context, in *pb.VpcIp) (*pb.Empty, error) {
	log.Printf("Received Request - Resume: %v", in.GetIp())
	return &pb.Empty{}, nil
}

func main() {
	fmt.Print("Server started, Port: "+port)
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer() 
	pb.RegisterVpcsServiceServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
