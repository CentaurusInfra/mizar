package main

import (
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	vpcv1 "mizar.futurewei.com/crds-operators/vpcs/v1"
)

// CreateObject creates a TestResource object for the test purpose.
func (c *Controller) CreateObject() error {
	object := &vpcv1.Vpc{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "example-tr2",
			Namespace: corev1.NamespaceDefault,
		},
		Spec: vpcv1.VpcSpec{
			Command:        "echo Hello World!",
			CustomProperty: "asdasd=1234",
		},
	}

	_, err := c.vpcclientset.MizarV1().Vpcs(corev1.NamespaceDefault).Create(object)
	return err
}
