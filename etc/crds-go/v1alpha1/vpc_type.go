package v1alpha1

import meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"

type Vpc struct {
	meta_v1.TypeMeta   `json:",inline"`
	meta_v1.ObjectMeta `json:"metadata"`
	Spec               VpcSpec   `json:"spec"`
	Status             VpcStatus `json:"status,omitempty"`
}
type VpcSpec struct {
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
