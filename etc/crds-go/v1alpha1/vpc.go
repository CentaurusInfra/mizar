package v1alpha1

import (
	meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/rest"
)

func (c *VpcV1Alpha1Client) Vpcs(namespace string) VpcInterface {
	return &VpcClient{
		client: c.restClient,
		ns:     namespace,
	}
}

type VpcV1Alpha1Client struct {
	restClient rest.Interface
}

type VpcInterface interface {
	Create(obj *Vpc) (*Vpc, error)
	Update(obj *Vpc) (*Vpc, error)
	Delete(name string, options *meta_v1.DeleteOptions) error
	Get(name string) (*Vpc, error)
}

type VpcClient struct {
	client rest.Interface
	ns     string
}

func (c *VpcClient) Create(obj *Vpc) (*Vpc, error) {
	result := &Vpc{}
	err := c.client.Post().
		Namespace(c.ns).Resource("Vpc").
		Body(obj).Do().Into(result)
	return result, err
}

func (c *VpcClient) Update(obj *Vpc) (*Vpc, error) {
	result := &Vpc{}
	err := c.client.Put().
		Namespace(c.ns).Resource("Vpcs").
		Body(obj).Do().Into(result)
	return result, err
}

func (c *VpcClient) Delete(name string, options *meta_v1.DeleteOptions) error {
	return c.client.Delete().
		Namespace(c.ns).Resource("Vpcs").
		Name(name).Body(options).Do().
		Error()
}

func (c *VpcClient) Get(name string) (*Vpc, error) {
	result := &Vpc{}
	err := c.client.Get().
		Namespace(c.ns).Resource("Vpcs").
		Name(name).Do().Into(result)
	return result, err
}
