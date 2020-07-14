package v1

import metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

// These const variables are used in our custom controller.
const (
	GroupName string = "mizar.futurewei.com"
	Kind      string = "Vpc"
	Version   string = "v1"
	Plural    string = "Vpcs"
	Singluar  string = "Vpc"
	ShortName string = "Vpc"
	Name      string = Plural + "." + GroupName
)

// TestResourceSpec specifies the 'spec' of TestResource CRD.
type TestResourceSpec struct {
	Command        string `json:"command"`
	CustomProperty string `json:"customProperty"`
}

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// TestResource describes a TestResource custom resource.
type TestResource struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   TestResourceSpec `json:"spec"`
	Status string           `json:"status"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// TestResourceList is a list of TestResource resources.
type TestResourceList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`

	Items []TestResource `json:"items"`
}
