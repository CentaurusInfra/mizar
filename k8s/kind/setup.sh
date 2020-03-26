docker image build -t fwnetworking/kindnode:latest -f Dockerfile .

kind create cluster --name kind-mizar --config cluster.yaml --kubeconfig /var/mizar/build/test/mizarcni.config