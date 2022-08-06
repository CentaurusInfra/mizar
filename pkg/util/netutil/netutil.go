/*
Copyright 2021 The Mizar Authors.

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

package netutil

import (
	"fmt"
	"net"
	"path"
	"strconv"
	"strings"

	"centaurusinfra.io/mizar/pkg/util/executil"
	"github.com/containernetworking/plugins/pkg/ns"
	"github.com/vishvananda/netlink"
	"golang.org/x/sys/unix"
)

// moves the interface to the CNI netns, renames it, sets the IP address and gatewey.
func ActivateInterface(
	ifName string,
	netNSName string,
	vethName string,
	ipPrefix string,
	ipAddress string,
	gatewayIp string) (string, error) {

	link, err := netlink.LinkByName(vethName)
	if err != nil {
		return fmt.Sprintf("Failed to get interface '%s'", vethName), err
	}

	if link.Attrs().OperState == netlink.OperUp {
		return fmt.Sprintf("Interface '%s' already UP.", vethName), nil
	}

	netNS, err := ns.GetNS(netNSName)
	if err != nil {
		return fmt.Sprintf("Failed to open netns '%s'", netNSName), err
	}
	defer netNS.Close()

	_, netNSFileName := path.Split(netNSName)
	activateIfLog := strings.Builder{}

	activateIfLog.WriteString(fmt.Sprintf("[Move interface '%s/%d' to netns '%s']", vethName, link.Attrs().Index, netNSFileName))
	if netlink.LinkSetNsFd(link, int(netNS.Fd())); err != nil {
		return activateIfLog.String(), err
	}

	if err = netNS.Do(func(_ ns.NetNS) error {
		activateIfLog.WriteString(fmt.Sprintf(" + [Rename interface '%s' to '%s']", vethName, ifName))
		if netlink.LinkSetName(link, ifName); err != nil {
			return err
		}

		activateIfLog.WriteString(" + [Retrieve loopback interface]")
		loLink, err := netlink.LinkByName("lo")
		if err != nil {
			return err
		}

		activateIfLog.WriteString(" + [Set loopback interface UP]")
		if err = netlink.LinkSetUp(loLink); err != nil {
			return err
		}

		activateIfLog.WriteString(fmt.Sprintf(" + [Set interface '%s' UP]", ifName))
		if err = netlink.LinkSetUp(link); err != nil {
			return err
		}

		activateIfLog.WriteString(fmt.Sprintf(" + [Set ip addr '%s' on interface '%s']", ipAddress, ifName))
		ipPrefix, err := strconv.Atoi(ipPrefix)
		if err != nil {
			return err
		}
		ipConfig := &netlink.Addr{
			IPNet: &net.IPNet{
				IP:   net.ParseIP(ipAddress),
				Mask: net.CIDRMask(ipPrefix, 32),
			}}
		if err = netlink.AddrAdd(link, ipConfig); err != nil {
			return err
		}

		activateIfLog.WriteString(fmt.Sprintf(" + [Set gateway '%s' for interface '%s']", gatewayIp, ifName))
		gw := net.ParseIP(gatewayIp)
		defaultRoute := netlink.Route{
			Dst:      nil,
			Gw:       gw,
			Protocol: unix.RTPROT_STATIC,
		}
		if err = netlink.RouteAdd(&defaultRoute); err != nil {
			return err
		}

		return nil
	}); err != nil {
		return activateIfLog.String(), err
	}

	activateIfLog.WriteString(fmt.Sprintf(" + [Disable tso on interface '%s']", ifName))
	cmdTxt, result, err := executil.Execute("ip", "netns", "exec", netNSFileName, "ethtool", "-K", ifName, "tso", "off", "gso", "off", "ufo", "off")
	activateIfLog.WriteString(fmt.Sprintf(" + [Cmd: '%s -> Result: '%s']", cmdTxt, result))
	if err != nil {
		return activateIfLog.String(), err
	}

	cmdTxt, result, err = executil.Execute("ip", "netns", "exec", netNSFileName, "ethtool", "--offload", ifName, "rx", "off", "tx", "off")
	activateIfLog.WriteString(fmt.Sprintf(" + [Cmd: '%s' -> Result: '%s']", cmdTxt, result))
	if err != nil {
		return activateIfLog.String(), err
	}

	return activateIfLog.String(), nil
}

func DeleteNetNS(netNSName string) {
	netNS, _ := ns.GetNS(netNSName)
	if netNS != nil {
		netNS.Close()
	}
	_, netNSFileName := path.Split(netNSName)
	executil.Execute("ip", "netns", "delete", netNSFileName)
}

func ParseCIDR(s string) (net.IP, *net.IPNet, error) {
	if !strings.Contains(s, "/") {
		s = fmt.Sprintf("%s/%d", s, 32)
	}
	return net.ParseCIDR(s)
}

func ParseIP(s string) net.IP {
	return net.ParseIP(s)
}
