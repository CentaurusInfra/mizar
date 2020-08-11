/*
Copyright The Kubernetes Authors.

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

// Code generated by informer-gen. DO NOT EDIT.

package v1

import (
	time "time"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	runtime "k8s.io/apimachinery/pkg/runtime"
	watch "k8s.io/apimachinery/pkg/watch"
	cache "k8s.io/client-go/tools/cache"
	versioned "mizar.com/crds-operator-proxy/crds/bouncers/apis/generated/clientset/versioned"
	internalinterfaces "mizar.com/crds-operator-proxy/crds/bouncers/apis/generated/informers/externalversions/internalinterfaces"
	v1 "mizar.com/crds-operator-proxy/crds/bouncers/apis/generated/listers/apis/v1"
	apisv1 "mizar.com/crds-operator-proxy/crds/bouncers/apis/v1"
)

// BouncerInformer provides access to a shared informer and lister for
// Bouncers.
type BouncerInformer interface {
	Informer() cache.SharedIndexInformer
	Lister() v1.BouncerLister
}

type bouncerInformer struct {
	factory          internalinterfaces.SharedInformerFactory
	tweakListOptions internalinterfaces.TweakListOptionsFunc
	namespace        string
}

// NewBouncerInformer constructs a new informer for Bouncer type.
// Always prefer using an informer factory to get a shared informer instead of getting an independent
// one. This reduces memory footprint and number of connections to the server.
func NewBouncerInformer(client versioned.Interface, namespace string, resyncPeriod time.Duration, indexers cache.Indexers) cache.SharedIndexInformer {
	return NewFilteredBouncerInformer(client, namespace, resyncPeriod, indexers, nil)
}

// NewFilteredBouncerInformer constructs a new informer for Bouncer type.
// Always prefer using an informer factory to get a shared informer instead of getting an independent
// one. This reduces memory footprint and number of connections to the server.
func NewFilteredBouncerInformer(client versioned.Interface, namespace string, resyncPeriod time.Duration, indexers cache.Indexers, tweakListOptions internalinterfaces.TweakListOptionsFunc) cache.SharedIndexInformer {
	return cache.NewSharedIndexInformer(
		&cache.ListWatch{
			ListFunc: func(options metav1.ListOptions) (runtime.Object, error) {
				if tweakListOptions != nil {
					tweakListOptions(&options)
				}
				return client.MizarV1().Bouncers(namespace).List(options)
			},
			WatchFunc: func(options metav1.ListOptions) (watch.Interface, error) {
				if tweakListOptions != nil {
					tweakListOptions(&options)
				}
				return client.MizarV1().Bouncers(namespace).Watch(options)
			},
		},
		&apisv1.Bouncer{},
		resyncPeriod,
		indexers,
	)
}

func (f *bouncerInformer) defaultInformer(client versioned.Interface, resyncPeriod time.Duration) cache.SharedIndexInformer {
	return NewFilteredBouncerInformer(client, f.namespace, resyncPeriod, cache.Indexers{cache.NamespaceIndex: cache.MetaNamespaceIndexFunc}, f.tweakListOptions)
}

func (f *bouncerInformer) Informer() cache.SharedIndexInformer {
	return f.factory.InformerFor(&apisv1.Bouncer{}, f.defaultInformer)
}

func (f *bouncerInformer) Lister() v1.BouncerLister {
	return v1.NewBouncerLister(f.Informer().GetIndexer())
}
