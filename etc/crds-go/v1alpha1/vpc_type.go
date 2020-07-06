package v1alpha1

import meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"

type Vpc struct {
	meta_v1.TypeMeta   `json:",inline"`
	meta_v1.ObjectMeta `json:"metadata"`
	Spec               VpcSpec   `json:"spec"`
	Status             VpcStatus `json:"status,omitempty"`
}

type VpcSpec struct {
	Ip             string `json:",ip"`
	Prefix         string `json:",prefix"`
	Vni            string `json:",vni"`
	Deviders       int    `json:",deviders"`
	Status         string `json:",status"`
	CreateTime     string `json:",createTime"`
	ProvisionDelay string `json:",provisiondelay"`
}

type VpcStatus struct {
	State   string `json:"state,omitempty"`
	Message string `json:"message,omitempty"`
}

type VpcList struct {
	meta_v1.TypeMeta `json:",inline"`
	meta_v1.ListMeta `json:"metadata"`
	Items            []Vpc `json:"items"`
}
