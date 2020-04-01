docker image build -t localhost:5000/kindnode:latest -f Dockerfile .

kind create cluster --name kind-mizar --config cluster.yaml --kubeconfig /var/mizar/build/test/mizarcni.config