docker image build -t phudtran/kindnode:latest -f Dockerfile .

kind create cluster --name kind-mizar --config cluster.yaml --kubeconfig /var/mizar/build/test/mizarcni.config