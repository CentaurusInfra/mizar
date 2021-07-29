/*
Copyright 2021 The Mizar Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package grpcclientutil

import (
	"context"
	"time"

	"google.golang.org/grpc"
	. "mizar.com/mizarcni/pkg/grpc"
	"mizar.com/mizarcni/pkg/object"
)

func ConsumeInterfaces(netVariables object.NetVariables) ([]*Interface, error) {
	client, conn, ctx, cancel, err := getInterfaceServiceClient()
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	defer cancel()

	clientResult, err := client.ConsumeInterfaces(ctx, GenerateCniParameters(netVariables))
	if err != nil {
		return nil, err
	}

	return clientResult.Interfaces, nil
}

func DeleteInterface(netVariables object.NetVariables) error {
	client, conn, ctx, cancel, err := getInterfaceServiceClient()
	if err != nil {
		return err
	}
	defer conn.Close()
	defer cancel()

	_, err = client.DeleteInterface(ctx, GenerateCniParameters(netVariables))
	if err != nil {
		return err
	}

	return nil
}

func getInterfaceServiceClient() (InterfaceServiceClient, *grpc.ClientConn, context.Context, context.CancelFunc, error) {
	conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		return nil, nil, nil, nil, err
	}
	client := NewInterfaceServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*3)
	return client, conn, ctx, cancel, nil
}

func GenerateCniParameters(netVariables object.NetVariables) *CniParameters {
	return &CniParameters{
		PodId: &PodId{
			K8SNamespace: netVariables.K8sPodNamespace,
			K8SPodName:   netVariables.K8sPodName,
			K8SPodTenant: netVariables.K8sPodTenant,
		},
		Netns:     netVariables.NetNS,
		Interface: netVariables.IfName,
	}
}
