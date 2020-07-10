package v1beta1

import meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"

// These const variables are used in our custom controller.
const (
	GroupName string = "mizar.com"
	Kind      string = "Vpc"
	Version   string = "v1"
	Plural    string = "vpcs"
	Singluar  string = "vpc"
	ShortName string = "vpcs"
	Name      string = Plural + "." + GroupName
)

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// Vpc describes a Vpc custom resource.
type Vpc struct {
	meta_v1.TypeMeta   `json:",inline"`
	meta_v1.ObjectMeta `json:"metadata,omitempty"`

	Spec   VpcSpec   `json:"spec"`
	Status VpcStatus `json:"status"`
}

// VpcSpec specifies the 'spec' of Vpc CRD.
type VpcSpec struct {
	Ip             string `json:"ip"`
	Prefix         string `json:"prefix"`
	Vni            string `json:"vni"`
	Dividers       int    `json:"dividers"`
	Status         string `json:"status"`
	CreateTime     string `json:"createtime"`
	ProvisionDelay string `json:"provisiondelay"`
}

type VpcStatus struct {
	State   string `json:"state,omitempty"`
	Message string `json:"message,omitempty"`
}

// VpcList is a list of VpcList resources.
type VpcList struct {
	meta_v1.TypeMeta `json:",inline"`
	meta_v1.ListMeta `json:"metadata"`
	Items            []Vpc `json:"items"`
}
