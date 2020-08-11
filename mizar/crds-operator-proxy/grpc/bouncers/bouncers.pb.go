// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.23.0
// 	protoc        v3.12.1
// source: bouncers/bouncers.proto

package bouncers

import (
	proto "github.com/golang/protobuf/proto"
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

// This is a compile-time assertion that a sufficiently up-to-date version
// of the legacy proto package is being used.
const _ = proto.ProtoPackageIsVersion4

// requests
type Bouncer struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Vpc            string `protobuf:"bytes,1,opt,name=vpc,proto3" json:"vpc,omitempty"`
	Net            string `protobuf:"bytes,2,opt,name=net,proto3" json:"net,omitempty"`
	Ip             string `protobuf:"bytes,3,opt,name=Ip,proto3" json:"Ip,omitempty"`
	Mac            string `protobuf:"bytes,4,opt,name=Mac,proto3" json:"Mac,omitempty"`
	Droplet        string `protobuf:"bytes,5,opt,name=Droplet,proto3" json:"Droplet,omitempty"`
	Status         string `protobuf:"bytes,6,opt,name=Status,proto3" json:"Status,omitempty"`
	CreateTime     string `protobuf:"bytes,7,opt,name=CreateTime,proto3" json:"CreateTime,omitempty"`
	ProvisionDelay string `protobuf:"bytes,8,opt,name=ProvisionDelay,proto3" json:"ProvisionDelay,omitempty"`
}

func (x *Bouncer) Reset() {
	*x = Bouncer{}
	if protoimpl.UnsafeEnabled {
		mi := &file_bouncers_bouncers_proto_msgTypes[0]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *Bouncer) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*Bouncer) ProtoMessage() {}

func (x *Bouncer) ProtoReflect() protoreflect.Message {
	mi := &file_bouncers_bouncers_proto_msgTypes[0]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use Bouncer.ProtoReflect.Descriptor instead.
func (*Bouncer) Descriptor() ([]byte, []int) {
	return file_bouncers_bouncers_proto_rawDescGZIP(), []int{0}
}

func (x *Bouncer) GetVpc() string {
	if x != nil {
		return x.Vpc
	}
	return ""
}

func (x *Bouncer) GetNet() string {
	if x != nil {
		return x.Net
	}
	return ""
}

func (x *Bouncer) GetIp() string {
	if x != nil {
		return x.Ip
	}
	return ""
}

func (x *Bouncer) GetMac() string {
	if x != nil {
		return x.Mac
	}
	return ""
}

func (x *Bouncer) GetDroplet() string {
	if x != nil {
		return x.Droplet
	}
	return ""
}

func (x *Bouncer) GetStatus() string {
	if x != nil {
		return x.Status
	}
	return ""
}

func (x *Bouncer) GetCreateTime() string {
	if x != nil {
		return x.CreateTime
	}
	return ""
}

func (x *Bouncer) GetProvisionDelay() string {
	if x != nil {
		return x.ProvisionDelay
	}
	return ""
}

type BouncerId struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Id string `protobuf:"bytes,1,opt,name=Id,proto3" json:"Id,omitempty"`
}

func (x *BouncerId) Reset() {
	*x = BouncerId{}
	if protoimpl.UnsafeEnabled {
		mi := &file_bouncers_bouncers_proto_msgTypes[1]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *BouncerId) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*BouncerId) ProtoMessage() {}

func (x *BouncerId) ProtoReflect() protoreflect.Message {
	mi := &file_bouncers_bouncers_proto_msgTypes[1]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use BouncerId.ProtoReflect.Descriptor instead.
func (*BouncerId) Descriptor() ([]byte, []int) {
	return file_bouncers_bouncers_proto_rawDescGZIP(), []int{1}
}

func (x *BouncerId) GetId() string {
	if x != nil {
		return x.Id
	}
	return ""
}

//response
type Empty struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields
}

func (x *Empty) Reset() {
	*x = Empty{}
	if protoimpl.UnsafeEnabled {
		mi := &file_bouncers_bouncers_proto_msgTypes[2]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *Empty) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*Empty) ProtoMessage() {}

func (x *Empty) ProtoReflect() protoreflect.Message {
	mi := &file_bouncers_bouncers_proto_msgTypes[2]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use Empty.ProtoReflect.Descriptor instead.
func (*Empty) Descriptor() ([]byte, []int) {
	return file_bouncers_bouncers_proto_rawDescGZIP(), []int{2}
}

type BouncersResponse struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	JsonReturncode string `protobuf:"bytes,1,opt,name=json_returncode,json=jsonReturncode,proto3" json:"json_returncode,omitempty"`
}

func (x *BouncersResponse) Reset() {
	*x = BouncersResponse{}
	if protoimpl.UnsafeEnabled {
		mi := &file_bouncers_bouncers_proto_msgTypes[3]
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		ms.StoreMessageInfo(mi)
	}
}

func (x *BouncersResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*BouncersResponse) ProtoMessage() {}

func (x *BouncersResponse) ProtoReflect() protoreflect.Message {
	mi := &file_bouncers_bouncers_proto_msgTypes[3]
	if protoimpl.UnsafeEnabled && x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use BouncersResponse.ProtoReflect.Descriptor instead.
func (*BouncersResponse) Descriptor() ([]byte, []int) {
	return file_bouncers_bouncers_proto_rawDescGZIP(), []int{3}
}

func (x *BouncersResponse) GetJsonReturncode() string {
	if x != nil {
		return x.JsonReturncode
	}
	return ""
}

var File_bouncers_bouncers_proto protoreflect.FileDescriptor

var file_bouncers_bouncers_proto_rawDesc = []byte{
	0x0a, 0x17, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x2f, 0x62, 0x6f, 0x75, 0x6e, 0x63,
	0x65, 0x72, 0x73, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x12, 0x08, 0x62, 0x6f, 0x75, 0x6e, 0x63,
	0x65, 0x72, 0x73, 0x22, 0xc9, 0x01, 0x0a, 0x07, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x12,
	0x10, 0x0a, 0x03, 0x76, 0x70, 0x63, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x03, 0x76, 0x70,
	0x63, 0x12, 0x10, 0x0a, 0x03, 0x6e, 0x65, 0x74, 0x18, 0x02, 0x20, 0x01, 0x28, 0x09, 0x52, 0x03,
	0x6e, 0x65, 0x74, 0x12, 0x0e, 0x0a, 0x02, 0x49, 0x70, 0x18, 0x03, 0x20, 0x01, 0x28, 0x09, 0x52,
	0x02, 0x49, 0x70, 0x12, 0x10, 0x0a, 0x03, 0x4d, 0x61, 0x63, 0x18, 0x04, 0x20, 0x01, 0x28, 0x09,
	0x52, 0x03, 0x4d, 0x61, 0x63, 0x12, 0x18, 0x0a, 0x07, 0x44, 0x72, 0x6f, 0x70, 0x6c, 0x65, 0x74,
	0x18, 0x05, 0x20, 0x01, 0x28, 0x09, 0x52, 0x07, 0x44, 0x72, 0x6f, 0x70, 0x6c, 0x65, 0x74, 0x12,
	0x16, 0x0a, 0x06, 0x53, 0x74, 0x61, 0x74, 0x75, 0x73, 0x18, 0x06, 0x20, 0x01, 0x28, 0x09, 0x52,
	0x06, 0x53, 0x74, 0x61, 0x74, 0x75, 0x73, 0x12, 0x1e, 0x0a, 0x0a, 0x43, 0x72, 0x65, 0x61, 0x74,
	0x65, 0x54, 0x69, 0x6d, 0x65, 0x18, 0x07, 0x20, 0x01, 0x28, 0x09, 0x52, 0x0a, 0x43, 0x72, 0x65,
	0x61, 0x74, 0x65, 0x54, 0x69, 0x6d, 0x65, 0x12, 0x26, 0x0a, 0x0e, 0x50, 0x72, 0x6f, 0x76, 0x69,
	0x73, 0x69, 0x6f, 0x6e, 0x44, 0x65, 0x6c, 0x61, 0x79, 0x18, 0x08, 0x20, 0x01, 0x28, 0x09, 0x52,
	0x0e, 0x50, 0x72, 0x6f, 0x76, 0x69, 0x73, 0x69, 0x6f, 0x6e, 0x44, 0x65, 0x6c, 0x61, 0x79, 0x22,
	0x1b, 0x0a, 0x09, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x49, 0x64, 0x12, 0x0e, 0x0a, 0x02,
	0x49, 0x64, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x02, 0x49, 0x64, 0x22, 0x07, 0x0a, 0x05,
	0x45, 0x6d, 0x70, 0x74, 0x79, 0x22, 0x3b, 0x0a, 0x10, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72,
	0x73, 0x52, 0x65, 0x73, 0x70, 0x6f, 0x6e, 0x73, 0x65, 0x12, 0x27, 0x0a, 0x0f, 0x6a, 0x73, 0x6f,
	0x6e, 0x5f, 0x72, 0x65, 0x74, 0x75, 0x72, 0x6e, 0x63, 0x6f, 0x64, 0x65, 0x18, 0x01, 0x20, 0x01,
	0x28, 0x09, 0x52, 0x0e, 0x6a, 0x73, 0x6f, 0x6e, 0x52, 0x65, 0x74, 0x75, 0x72, 0x6e, 0x63, 0x6f,
	0x64, 0x65, 0x32, 0xb3, 0x02, 0x0a, 0x0f, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x53,
	0x65, 0x72, 0x76, 0x69, 0x63, 0x65, 0x12, 0x35, 0x0a, 0x0d, 0x43, 0x72, 0x65, 0x61, 0x74, 0x65,
	0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x12, 0x11, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65,
	0x72, 0x73, 0x2e, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x1a, 0x0f, 0x2e, 0x62, 0x6f, 0x75,
	0x6e, 0x63, 0x65, 0x72, 0x73, 0x2e, 0x45, 0x6d, 0x70, 0x74, 0x79, 0x22, 0x00, 0x12, 0x35, 0x0a,
	0x0d, 0x55, 0x70, 0x64, 0x61, 0x74, 0x65, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x12, 0x11,
	0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x2e, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65,
	0x72, 0x1a, 0x0f, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x2e, 0x45, 0x6d, 0x70,
	0x74, 0x79, 0x22, 0x00, 0x12, 0x40, 0x0a, 0x0b, 0x52, 0x65, 0x61, 0x64, 0x42, 0x6f, 0x75, 0x6e,
	0x63, 0x65, 0x72, 0x12, 0x13, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x2e, 0x42,
	0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x49, 0x64, 0x1a, 0x1a, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63,
	0x65, 0x72, 0x73, 0x2e, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x52, 0x65, 0x73, 0x70,
	0x6f, 0x6e, 0x73, 0x65, 0x22, 0x00, 0x12, 0x37, 0x0a, 0x0d, 0x44, 0x65, 0x6c, 0x65, 0x74, 0x65,
	0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x12, 0x13, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65,
	0x72, 0x73, 0x2e, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x49, 0x64, 0x1a, 0x0f, 0x2e, 0x62,
	0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x2e, 0x45, 0x6d, 0x70, 0x74, 0x79, 0x22, 0x00, 0x12,
	0x37, 0x0a, 0x0d, 0x52, 0x65, 0x73, 0x75, 0x6d, 0x65, 0x42, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72,
	0x12, 0x13, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x2e, 0x42, 0x6f, 0x75, 0x6e,
	0x63, 0x65, 0x72, 0x49, 0x64, 0x1a, 0x0f, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73,
	0x2e, 0x45, 0x6d, 0x70, 0x74, 0x79, 0x22, 0x00, 0x42, 0x5a, 0x0a, 0x1f, 0x69, 0x6f, 0x2e, 0x63,
	0x72, 0x64, 0x73, 0x2d, 0x6f, 0x70, 0x65, 0x72, 0x61, 0x74, 0x6f, 0x72, 0x73, 0x2e, 0x67, 0x72,
	0x70, 0x63, 0x2e, 0x62, 0x6f, 0x75, 0x6e, 0x63, 0x65, 0x72, 0x73, 0x42, 0x0d, 0x42, 0x6f, 0x75,
	0x6e, 0x63, 0x65, 0x72, 0x73, 0x50, 0x72, 0x6f, 0x74, 0x6f, 0x50, 0x01, 0x5a, 0x26, 0x6d, 0x69,
	0x7a, 0x61, 0x72, 0x2e, 0x63, 0x6f, 0x6d, 0x2f, 0x63, 0x72, 0x64, 0x73, 0x2d, 0x6f, 0x70, 0x65,
	0x72, 0x61, 0x74, 0x6f, 0x72, 0x73, 0x2f, 0x67, 0x72, 0x70, 0x63, 0x2f, 0x62, 0x6f, 0x75, 0x6e,
	0x63, 0x65, 0x72, 0x73, 0x62, 0x06, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x33,
}

var (
	file_bouncers_bouncers_proto_rawDescOnce sync.Once
	file_bouncers_bouncers_proto_rawDescData = file_bouncers_bouncers_proto_rawDesc
)

func file_bouncers_bouncers_proto_rawDescGZIP() []byte {
	file_bouncers_bouncers_proto_rawDescOnce.Do(func() {
		file_bouncers_bouncers_proto_rawDescData = protoimpl.X.CompressGZIP(file_bouncers_bouncers_proto_rawDescData)
	})
	return file_bouncers_bouncers_proto_rawDescData
}

var file_bouncers_bouncers_proto_msgTypes = make([]protoimpl.MessageInfo, 4)
var file_bouncers_bouncers_proto_goTypes = []interface{}{
	(*Bouncer)(nil),          // 0: bouncers.Bouncer
	(*BouncerId)(nil),        // 1: bouncers.BouncerId
	(*Empty)(nil),            // 2: bouncers.Empty
	(*BouncersResponse)(nil), // 3: bouncers.BouncersResponse
}
var file_bouncers_bouncers_proto_depIdxs = []int32{
	0, // 0: bouncers.BouncersService.CreateBouncer:input_type -> bouncers.Bouncer
	0, // 1: bouncers.BouncersService.UpdateBouncer:input_type -> bouncers.Bouncer
	1, // 2: bouncers.BouncersService.ReadBouncer:input_type -> bouncers.BouncerId
	1, // 3: bouncers.BouncersService.DeleteBouncer:input_type -> bouncers.BouncerId
	1, // 4: bouncers.BouncersService.ResumeBouncer:input_type -> bouncers.BouncerId
	2, // 5: bouncers.BouncersService.CreateBouncer:output_type -> bouncers.Empty
	2, // 6: bouncers.BouncersService.UpdateBouncer:output_type -> bouncers.Empty
	3, // 7: bouncers.BouncersService.ReadBouncer:output_type -> bouncers.BouncersResponse
	2, // 8: bouncers.BouncersService.DeleteBouncer:output_type -> bouncers.Empty
	2, // 9: bouncers.BouncersService.ResumeBouncer:output_type -> bouncers.Empty
	5, // [5:10] is the sub-list for method output_type
	0, // [0:5] is the sub-list for method input_type
	0, // [0:0] is the sub-list for extension type_name
	0, // [0:0] is the sub-list for extension extendee
	0, // [0:0] is the sub-list for field type_name
}

func init() { file_bouncers_bouncers_proto_init() }
func file_bouncers_bouncers_proto_init() {
	if File_bouncers_bouncers_proto != nil {
		return
	}
	if !protoimpl.UnsafeEnabled {
		file_bouncers_bouncers_proto_msgTypes[0].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*Bouncer); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_bouncers_bouncers_proto_msgTypes[1].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*BouncerId); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_bouncers_bouncers_proto_msgTypes[2].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*Empty); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_bouncers_bouncers_proto_msgTypes[3].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*BouncersResponse); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: file_bouncers_bouncers_proto_rawDesc,
			NumEnums:      0,
			NumMessages:   4,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_bouncers_bouncers_proto_goTypes,
		DependencyIndexes: file_bouncers_bouncers_proto_depIdxs,
		MessageInfos:      file_bouncers_bouncers_proto_msgTypes,
	}.Build()
	File_bouncers_bouncers_proto = out.File
	file_bouncers_bouncers_proto_rawDesc = nil
	file_bouncers_bouncers_proto_goTypes = nil
	file_bouncers_bouncers_proto_depIdxs = nil
}
