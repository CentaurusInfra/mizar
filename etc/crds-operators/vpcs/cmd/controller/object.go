package main

import (
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	vpcv1 "mizar.futurewei.com/crds-operators/vpcs/apis/v1"
)

// CreateObject creates a Vpc object.
func (c *Controller) CreateObject() error {
	object := &vpcv1.Vpc{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "vpc1",
			Namespace: corev1.NamespaceDefault,
		},
		Spec: vpcv1.VpcSpec{
			Command:        "echo Hello World!",
			CustomProperty: "asdasd=1234",
			Ip:             "10.0.0.1",
			Prefix:         "10.0.0.0/24",
			Vni:            "16777210",
			Dividers:       1,
			Status:         "active",
			CreateTime:     "2020-07-20",
			ProvisionDelay: "10",
		},
	}

	_, err := c.vpcclientset.MizarV1().Vpcs(corev1.NamespaceDefault).Create(object)
	return err
}
