# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: wagon_001.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fwagon_001.proto\"\xc9\x03\n\x0fWagonDeviceData\x12\x11\n\tdevice_id\x18\x01 \x01(\t\x12\x0f\n\x07pack_id\x18\x02 \x01(\r\x12\x19\n\x11rw_car_fw_version\x18\x03 \x01(\x05\x12\x11\n\tmestypeid\x18\x04 \x01(\x05\x12\x0c\n\x04time\x18\x05 \x01(\x05\x12\x0b\n\x03lat\x18\x06 \x01(\x11\x12\x0b\n\x03lon\x18\x07 \x01(\x11\x12\x10\n\x08velocity\x18\x08 \x01(\x11\x12\x11\n\tdirection\x18\t \x01(\x11\x12\x13\n\x0btemperature\x18\n \x01(\x11\x12\x0f\n\x07\x62\x61tmain\x18\x0b \x01(\x05\x12\x0c\n\x04rssi\x18\x0c \x01(\x05\x12\x0f\n\x07\x61rea_id\x18\r \x01(\t\x12\x0f\n\x07g_range\x18\x10 \x01(\x05\x12\x0e\n\x06g_freq\x18\x11 \x01(\x05\x12\x0e\n\x06g_time\x18\x12 \x01(\x05\x12\x19\n\raccel_forward\x18\x13 \x03(\x11\x42\x02\x10\x01\x12\x1a\n\x0e\x61\x63\x63\x65l_vertical\x18\x14 \x03(\x11\x42\x02\x10\x01\x12\x1c\n\x10\x61\x63\x63\x65l_transverse\x18\x15 \x03(\x11\x42\x02\x10\x01\x12\x0c\n\x04imsi\x18\x16 \x01(\t\x12\x0e\n\x06\x62\x61tgw1\x18\x17 \x01(\x05\x12\x0e\n\x06tcargo\x18\x18 \x01(\x11\x12\x0e\n\x06pcargo\x18\x19 \x01(\x11\x12\x0e\n\x06vcargo\x18\x1a \x01(\x11\"\xee\x01\n\x12WagonDeviceComdown\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x15\n\rtime_interval\x18\x02 \x01(\x05\x12\x0f\n\x07g_range\x18\x03 \x01(\x05\x12\x11\n\tg_quality\x18\x04 \x01(\x05\x12\x13\n\x0bg_threshold\x18\x05 \x01(\x05\x12\x0f\n\x07\x64\x61t_qos\x18\x06 \x01(\x05\x12\x0f\n\x07\x63om_qos\x18\x07 \x01(\x05\x12\r\n\x05group\x18\x08 \x01(\t\x12\x11\n\tdevice_id\x18\t \x01(\t\x12\x0f\n\x07msg_del\x18\n \x01(\x05\x12\x0b\n\x03\x63om\x18\x0b \x01(\x05\x12\x12\n\ng_duration\x18\x0c \x01(\x05\"_\n\x10WagonDeviceComup\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x15\n\rcode_response\x18\x02 \x01(\x05\x12\r\n\x05\x65rror\x18\x03 \x01(\t\x12\x11\n\tdevice_id\x18\x04 \x01(\t\"!\n\x05Point\x12\x0b\n\x03lat\x18\x01 \x01(\x11\x12\x0b\n\x03lon\x18\x02 \x01(\x11\"\xe3\x01\n\x0eWagonAreasdown\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x0e\n\x06\x61\x63tion\x18\x02 \x01(\x05\x12\x0f\n\x07\x61rea_id\x18\x03 \x01(\x05\x12\x11\n\tarea_type\x18\x04 \x01(\x05\x12\x16\n\x06points\x18\x05 \x03(\x0b\x32\x06.Point\x12\x15\n\rtime_interval\x18\x06 \x01(\x05\x12\x0f\n\x07g_range\x18\x07 \x01(\x05\x12\x0e\n\x06radius\x18\x08 \x01(\x05\x12\x15\n\rarea_interval\x18\t \x01(\x05\x12\x11\n\tdevice_id\x18\n \x01(\t\x12\x0f\n\x07msg_del\x18\x0b \x01(\x05\"m\n\x0cWagonAreasup\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x15\n\rcode_response\x18\x02 \x01(\x05\x12\r\n\x05\x65rror\x18\x03 \x01(\t\x12\x10\n\x08\x61reas_id\x18\x04 \x03(\t\x12\x11\n\tdevice_id\x18\x05 \x01(\t\"\\\n\tWagonRfid\x12\x12\n\nnet_number\x18\x01 \x01(\x05\x12\x0b\n\x03\x65sr\x18\x02 \x01(\x05\x12\x0c\n\x04time\x18\x03 \x01(\x05\x12\x0f\n\x07hw_data\x18\x04 \x01(\x05\x12\x0f\n\x07lw_data\x18\x05 \x01(\x05\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'wagon_001_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _WAGONDEVICEDATA.fields_by_name['accel_forward']._options = None
  _WAGONDEVICEDATA.fields_by_name['accel_forward']._serialized_options = b'\020\001'
  _WAGONDEVICEDATA.fields_by_name['accel_vertical']._options = None
  _WAGONDEVICEDATA.fields_by_name['accel_vertical']._serialized_options = b'\020\001'
  _WAGONDEVICEDATA.fields_by_name['accel_transverse']._options = None
  _WAGONDEVICEDATA.fields_by_name['accel_transverse']._serialized_options = b'\020\001'
  _globals['_WAGONDEVICEDATA']._serialized_start=20
  _globals['_WAGONDEVICEDATA']._serialized_end=477
  _globals['_WAGONDEVICECOMDOWN']._serialized_start=480
  _globals['_WAGONDEVICECOMDOWN']._serialized_end=718
  _globals['_WAGONDEVICECOMUP']._serialized_start=720
  _globals['_WAGONDEVICECOMUP']._serialized_end=815
  _globals['_POINT']._serialized_start=817
  _globals['_POINT']._serialized_end=850
  _globals['_WAGONAREASDOWN']._serialized_start=853
  _globals['_WAGONAREASDOWN']._serialized_end=1080
  _globals['_WAGONAREASUP']._serialized_start=1082
  _globals['_WAGONAREASUP']._serialized_end=1191
  _globals['_WAGONRFID']._serialized_start=1193
  _globals['_WAGONRFID']._serialized_end=1285
# @@protoc_insertion_point(module_scope)
