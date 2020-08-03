"""This module defines a generated parser model."""

from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import HexStringModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement

def get_model():

    """This model defines how to parse Suricata Event logs from the AIT-LDS."""

    conn = SequenceModelElement('conn', [
                FixedDataModelElement('src_ip_str', b'"src_ip":"'),
                FirstMatchModelElement('ip', [
                    SequenceModelElement('ipv4', [
                        IpAddressDataModelElement('src_ip'),
                        FixedDataModelElement('src_port_str', b'","src_port":'),
                        DecimalIntegerValueModelElement('src_port'),
                        FixedDataModelElement('dest_ip_str', b',"dest_ip":"'),
                        IpAddressDataModelElement('dest_ip'),
                        FixedDataModelElement('dest_port_str', b'","dest_port":'),
                        DecimalIntegerValueModelElement('dest_port'),
                        FixedDataModelElement('proto_str', b',"proto":"'),
                        DelimitedDataModelElement('proto', b'"'),
                        FixedDataModelElement('quote', b'"')
                        ]),
                    SequenceModelElement('ipv6', [
                        DelimitedDataModelElement('src_ip', b'"'),
                        FixedDataModelElement('dest_ip_str', b'","dest_ip":"'),
                        DelimitedDataModelElement('dest_ip', b'"'),
                        FixedDataModelElement('proto_str', b'","proto":"'),
                        DelimitedDataModelElement('proto', b'"'),
                        FixedDataModelElement('icmp_type_str', b'","icmp_type":'),
                        DecimalIntegerValueModelElement('icmp_type'),
                        FixedDataModelElement('icmp_code_str', b',"icmp_code":'),
                        DecimalIntegerValueModelElement('icmp_code'),
                        ]),
                    ])
        ])

    http = SequenceModelElement('http', [
                FixedDataModelElement('hostname_str', b',"http":{"hostname":"'),
                DelimitedDataModelElement('hostname', b'"'),
                FixedDataModelElement('url_str', b'","url":"'),
                DelimitedDataModelElement('url', b'"', escape=b'\\'),
                FixedDataModelElement('http_user_agent_str', b'","http_user_agent":"'),
                DelimitedDataModelElement('http_user_agent', b'"'),
                OptionalMatchModelElement('content_type',
                    SequenceModelElement('content_type', [
                        FixedDataModelElement('http_content_type_str', b'","http_content_type":"'),
                        DelimitedDataModelElement('http_content_type', b'"'),
                        ])),
                OptionalMatchModelElement('http_refer',
                    SequenceModelElement('http_refer', [
                        FixedDataModelElement('http_refer_str', b'","http_refer":"'),
                        DelimitedDataModelElement('http_refer', b'"'),
                        ])),
                FixedDataModelElement('http_method_str', b'","http_method":"'),
                DelimitedDataModelElement('http_method', b'"'),
                FixedDataModelElement('protocol_str', b'","protocol":"'),
                DelimitedDataModelElement('protocol', b'"'),
                FixedDataModelElement('quote_str', b'"'),
                OptionalMatchModelElement('status',
                    SequenceModelElement('status', [
                        FixedDataModelElement('status_str', b',"status":'),
                        DecimalIntegerValueModelElement('status'),
                        ])),
                OptionalMatchModelElement('redirect',
                    SequenceModelElement('redirect', [
                        FixedDataModelElement('redirect_str', b',"redirect":"'),
                        DelimitedDataModelElement('redirect', b'"'),
                        FixedDataModelElement('quote_str', b'"')
                        ])),
                FixedDataModelElement('length_str', b',"length":'),
                DecimalIntegerValueModelElement('length'),
                FixedDataModelElement('brack_str', b'}')
        ])

    model = SequenceModelElement('model', [
        FixedDataModelElement('time_str', b'{"timestamp":"'),
        DateTimeModelElement('time', b'%Y-%m-%dT%H:%M:%S.%f'),
        FixedDataModelElement('plus_sign', b'+'),
        DecimalIntegerValueModelElement('tz'),
        FixedDataModelElement('comma_str', b'",'),
        OptionalMatchModelElement('flow_id',
            SequenceModelElement('flow_id', [
                FixedDataModelElement('flow_id_str', b'"flow_id":'),
                DecimalIntegerValueModelElement('flow_id'),
                FixedDataModelElement('comma_str', b',')])),
        OptionalMatchModelElement('in_iface',
            SequenceModelElement('in_iface', [
                FixedDataModelElement('in_iface_str', b'"in_iface":"'),
                DelimitedDataModelElement('in_iface', b'"'),
                FixedDataModelElement('comma_str', b'",')])),
        FixedDataModelElement('event_type_str', b'"event_type":"'),
        FirstMatchModelElement('event_type', [
            SequenceModelElement('dns', [
                FixedDataModelElement('dns_str', b'dns",'),
                conn,
                SequenceModelElement('dns', [
                    FixedDataModelElement('type_str', b',"dns":{"type":"'),
                    DelimitedDataModelElement('type', b'"'),
                    FixedDataModelElement('id_str', b'","id":'),
                    DecimalIntegerValueModelElement('id'),
                    OptionalMatchModelElement('rcode',
                        SequenceModelElement('rcode', [
                            FixedDataModelElement('rcode_str', b',"rcode":"'),
                            DelimitedDataModelElement('rcode', b'"'),
                            FixedDataModelElement('quote_str', b'"')])),
                    FixedDataModelElement('rrname_str', b',"rrname":"'),
                    DelimitedDataModelElement('rrname', b'"'),
                    OptionalMatchModelElement('rrtype',
                        SequenceModelElement('rrtype', [
                            FixedDataModelElement('rrtype_str', b'","rrtype":"'),
                            DelimitedDataModelElement('rrtype', b'"')])),
                    FixedDataModelElement('quote', b'"'),
                    OptionalMatchModelElement('tx_id',
                        SequenceModelElement('tx_id', [
                            FixedDataModelElement('tx_id_str', b',"tx_id":'),
                            DecimalIntegerValueModelElement('tx_id')])),
                    OptionalMatchModelElement('ttl',
                        SequenceModelElement('ttl', [
                            FixedDataModelElement('ttl_str', b',"ttl":'),
                            DecimalIntegerValueModelElement('ttl')])),
                    OptionalMatchModelElement('rdata',
                        SequenceModelElement('rdata', [
                            FixedDataModelElement('rdata_str', b',"rdata":"'),
                            DelimitedDataModelElement('rdata', b'"'),
                            FixedDataModelElement('quote_str', b'"')])),
                    FixedDataModelElement('brack_str', b'}}')
                    ]),
                ]),
            SequenceModelElement('flow', [
                FixedDataModelElement('flow_str', b'flow",'),
                conn,
                OptionalMatchModelElement('app_proto',
                    SequenceModelElement('app_proto', [
                        FixedDataModelElement('app_proto_str', b',"app_proto":"'),
                        DelimitedDataModelElement('app_proto', b'"'),
                        FixedDataModelElement('quote_str', b'"')
                        ])
                    ),
                OptionalMatchModelElement('app_proto_tc',
                    SequenceModelElement('app_proto_tc', [
                        FixedDataModelElement('app_proto_tc_str', b',"app_proto_tc":"'),
                        DelimitedDataModelElement('app_proto_tc', b'"'),
                        FixedDataModelElement('quote_str', b'"')
                        ])
                    ),
                SequenceModelElement('flow', [
                    FixedDataModelElement('pkts_toserver_str', b',"flow":{"pkts_toserver":'),
                    DecimalIntegerValueModelElement('pkts_toserver'),
                    FixedDataModelElement('pkts_toclient_str', b',"pkts_toclient":'),
                    DecimalIntegerValueModelElement('pkts_toclient'),
                    FixedDataModelElement('bytes_toserver_str', b',"bytes_toserver":'),
                    DecimalIntegerValueModelElement('bytes_toserver'),
                    FixedDataModelElement('bytes_toclient_str', b',"bytes_toclient":'),
                    DecimalIntegerValueModelElement('bytes_toclient'),
                    FixedDataModelElement('start_str', b',"start":"'),
                    DelimitedDataModelElement('start', b'"'),
                    FixedDataModelElement('end_str', b'","end":"'),
                    DelimitedDataModelElement('end', b'"'),
                    FixedDataModelElement('age_str', b'","age":'),
                    DecimalIntegerValueModelElement('age'),
                    FixedDataModelElement('state_str', b',"state":"'),
                    DelimitedDataModelElement('state', b'"'),
                    FixedDataModelElement('reason_str', b'","reason":"'),
                    DelimitedDataModelElement('reason', b'"'),
                    FixedDataModelElement('alerted_str', b'","alerted":'),
                    FixedWordlistDataModelElement('alerted', [b'true', b'false']),
                    FixedDataModelElement('brack_str1', b'}'),
                    OptionalMatchModelElement('tcp',
                        SequenceModelElement('tcp', [
                            FixedDataModelElement('tcp_flags_str', b',"tcp":{"tcp_flags":"'),
                            HexStringModelElement('tcp_flags'),
                            FixedDataModelElement('tcp_flags_ts_str', b'","tcp_flags_ts":"'),
                            HexStringModelElement('tcp_flags_ts'),
                            FixedDataModelElement('tcp_flags_tc_str', b'","tcp_flags_tc":"'),
                            HexStringModelElement('tcp_flags_tc'),
                            OptionalMatchModelElement('flags',
                                SequenceModelElement('flags', [
                                    FixedDataModelElement('syn_str', b'","syn":'),
                                    FixedWordlistDataModelElement('syn', [b'true', b'false']),
                                    OptionalMatchModelElement('fin',
                                        SequenceModelElement('fin', [
                                            FixedDataModelElement('fin_str', b',"fin":'),
                                            FixedWordlistDataModelElement('fin', [b'true', b'false']),
                                            ])
                                        ),
                                    OptionalMatchModelElement('rst',
                                        SequenceModelElement('rst', [
                                            FixedDataModelElement('rst_str', b',"rst":'),
                                            FixedWordlistDataModelElement('rst', [b'true', b'false']),
                                            ])
                                        ),
                                    OptionalMatchModelElement('psh',
                                        SequenceModelElement('psh', [
                                            FixedDataModelElement('psh_str', b',"psh":'),
                                            FixedWordlistDataModelElement('psh', [b'true', b'false']),
                                            ])
                                        ),
                                    FixedDataModelElement('ack_str', b',"ack":'),
                                    FixedWordlistDataModelElement('ack', [b'true', b'false']),
                                    FixedDataModelElement('tcp_state_str', b',"state":"'),
                                    DelimitedDataModelElement('tcp_state', b'"'),
                                    ])
                                ),
                            FixedDataModelElement('tcp_brack_str', b'"}'),
                            ])
                        ),
                    FixedDataModelElement('brack_str2', b'}')
                    ]),
                ]),
            SequenceModelElement('http', [
                FixedDataModelElement('http_str', b'http",'),
                conn,
                FixedDataModelElement('tx_id_str', b',"tx_id":'),
                DecimalIntegerValueModelElement('tx_id'),
                http,
                FixedDataModelElement('brack_str', b'}')
                ]),
            SequenceModelElement('fileinfo', [
                FixedDataModelElement('fileinfo_str', b'fileinfo",'),
                conn,
                http,
                FixedDataModelElement('app_proto_str', b',"app_proto":"'),
                DelimitedDataModelElement('app_proto', b'"'),
                SequenceModelElement('fileinfo', [
                    FixedDataModelElement('fileinfo_str', b'","fileinfo":{'),
                    OptionalMatchModelElement('filename',
                        SequenceModelElement('filename', [
                            FixedDataModelElement('filename_str', b'"filename":"'),
                            DelimitedDataModelElement('filename', b'"'),
                            FixedDataModelElement('quote_str', b'",')
                        ])
                    ),
                    FixedDataModelElement('state_str', b'"state":"'),
                    DelimitedDataModelElement('state', b'"'),
                    FixedDataModelElement('stored_str', b'","stored":'),
                    FixedWordlistDataModelElement('stored', [b'true', b'false']),
                    FixedDataModelElement('size_str', b',"size":'),
                    DecimalIntegerValueModelElement('size'),
                    FixedDataModelElement('tx_id_str', b',"tx_id":'),
                    DecimalIntegerValueModelElement('tx_id'),
                    FixedDataModelElement('brack_str', b'}}')
                    ]),
                ]),
            SequenceModelElement('stats', [
                FixedDataModelElement('stats_str', b'stats",'),
                FixedDataModelElement('uptime_str', b'"stats":{"uptime":'),
                DecimalIntegerValueModelElement('uptime'),
                SequenceModelElement('capture', [
                    FixedDataModelElement('capture_str', b',"capture":{'),
                    FixedDataModelElement('kernel_packets_str', b'"kernel_packets":'),
                    DecimalIntegerValueModelElement('kernel_packets'),
                    FixedDataModelElement('kernel_drops_str', b',"kernel_drops":'),
                    DecimalIntegerValueModelElement('kernel_drops'),
                    FixedDataModelElement('brack_str', b'}')
                    ]),
                SequenceModelElement('decoder', [
                    FixedDataModelElement('pkts_str', b',"decoder":{"pkts":'),
                    DecimalIntegerValueModelElement('pkts'),
                    FixedDataModelElement('bytes_str', b',"bytes":'),
                    DecimalIntegerValueModelElement('bytes'),
                    FixedDataModelElement('invalid_str', b',"invalid":'),
                    DecimalIntegerValueModelElement('invalid'),
                    FixedDataModelElement('ipv4_str', b',"ipv4":'),
                    DecimalIntegerValueModelElement('ipv4'),
                    FixedDataModelElement('ipv6_str', b',"ipv6":'),
                    DecimalIntegerValueModelElement('ipv6'),
                    FixedDataModelElement('ethernet_str', b',"ethernet":'),
                    DecimalIntegerValueModelElement('ethernet'),
                    FixedDataModelElement('raw_str', b',"raw":'),
                    DecimalIntegerValueModelElement('raw'),
                    FixedDataModelElement('null_str', b',"null":'),
                    DecimalIntegerValueModelElement('null'),
                    FixedDataModelElement('sll_str', b',"sll":'),
                    DecimalIntegerValueModelElement('sll'),
                    FixedDataModelElement('tcp_str', b',"tcp":'),
                    DecimalIntegerValueModelElement('tcp'),
                    FixedDataModelElement('udp_str', b',"udp":'),
                    DecimalIntegerValueModelElement('udp'),
                    FixedDataModelElement('sctp_str', b',"sctp":'),
                    DecimalIntegerValueModelElement('sctp'),
                    FixedDataModelElement('icmpv4_str', b',"icmpv4":'),
                    DecimalIntegerValueModelElement('icmpv4'),
                    FixedDataModelElement('icmpv6_str', b',"icmpv6":'),
                    DecimalIntegerValueModelElement('icmpv6'),
                    FixedDataModelElement('ppp_str', b',"ppp":'),
                    DecimalIntegerValueModelElement('ppp'),
                    FixedDataModelElement('pppoe_str', b',"pppoe":'),
                    DecimalIntegerValueModelElement('pppoe'),
                    FixedDataModelElement('gre_str', b',"gre":'),
                    DecimalIntegerValueModelElement('gre'),
                    FixedDataModelElement('vlan_str', b',"vlan":'),
                    DecimalIntegerValueModelElement('vlan'),
                    FixedDataModelElement('vlan_qinq_str', b',"vlan_qinq":'),
                    DecimalIntegerValueModelElement('vlan_qinq'),
                    FixedDataModelElement('teredo_str', b',"teredo":'),
                    DecimalIntegerValueModelElement('teredo'),
                    FixedDataModelElement('ipv4_in_ipv6_str', b',"ipv4_in_ipv6":'),
                    DecimalIntegerValueModelElement('ipv4_in_ipv6'),
                    FixedDataModelElement('ipv6_in_ipv6_str', b',"ipv6_in_ipv6":'),
                    DecimalIntegerValueModelElement('ipv6_in_ipv6'),
                    FixedDataModelElement('mpls_str', b',"mpls":'),
                    DecimalIntegerValueModelElement('mpls'),
                    FixedDataModelElement('avg_pkt_size_str', b',"avg_pkt_size":'),
                    DecimalIntegerValueModelElement('avg_pkt_size'),
                    FixedDataModelElement('max_pkt_size_str', b',"max_pkt_size":'),
                    DecimalIntegerValueModelElement('max_pkt_size'),
                    FixedDataModelElement('erspan_str', b',"erspan":'),
                    DecimalIntegerValueModelElement('erspan'),
                    SequenceModelElement('ipraw', [
                        FixedDataModelElement('invalid_ip_version_str', b',"ipraw":{"invalid_ip_version":'),
                        DecimalIntegerValueModelElement('invalid_ip_version'),
                        ]),
                    SequenceModelElement('ltnull', [
                        FixedDataModelElement('ipraw_pkt_too_small_str', b'},"ltnull":{"pkt_too_small":'),
                        DecimalIntegerValueModelElement('ipraw_pkt_too_small'),
                        FixedDataModelElement('unsupported_type', b',"unsupported_type":'),
                        DecimalIntegerValueModelElement('unsupported_type'),
                        ]),
                    SequenceModelElement('dce', [
                        FixedDataModelElement('dce_pkt_too_small_str', b'},"dce":{"pkt_too_small":'),
                        DecimalIntegerValueModelElement('dce_pkt_too_small'),
                        FixedDataModelElement('brack_str', b'}')
                    ])
                ]),
                SequenceModelElement('flow', [
                    FixedDataModelElement('memcap_str', b'},"flow":{"memcap":'),
                    DecimalIntegerValueModelElement('memcap'),
                    FixedDataModelElement('spare_str', b',"spare":'),
                    DecimalIntegerValueModelElement('spare'),
                    FixedDataModelElement('emerg_mode_entered_str', b',"emerg_mode_entered":'),
                    DecimalIntegerValueModelElement('emerg_mode_entered'),
                    FixedDataModelElement('emerg_mode_over_str', b',"emerg_mode_over":'),
                    DecimalIntegerValueModelElement('emerg_mode_over'),
                    FixedDataModelElement('tcp_reuse_str', b',"tcp_reuse":'),
                    DecimalIntegerValueModelElement('tcp_reuse'),
                    FixedDataModelElement('memuse_str', b',"memuse":'),
                    DecimalIntegerValueModelElement('memuse'),
                ]),
                SequenceModelElement('defrag', [
                    SequenceModelElement('ipv4', [
                        FixedDataModelElement('fragments_str', b'},"defrag":{"ipv4":{"fragments":'),
                        DecimalIntegerValueModelElement('fragments'),
                        FixedDataModelElement('reassembled_str', b',"reassembled":'),
                        DecimalIntegerValueModelElement('reassembled_str'),
                        FixedDataModelElement('timeouts_str', b',"timeouts":'),
                        DecimalIntegerValueModelElement('timeouts'),
                    ]),
                    SequenceModelElement('ipv6', [
                        FixedDataModelElement('fragments_str', b'},"ipv6":{"fragments":'),
                        DecimalIntegerValueModelElement('fragments'),
                        FixedDataModelElement('reassembled_str', b',"reassembled":'),
                        DecimalIntegerValueModelElement('reassembled_str'),
                        FixedDataModelElement('timeouts_str', b',"timeouts":'),
                        DecimalIntegerValueModelElement('timeouts'),
                    ]),
                    FixedDataModelElement('max_frag_hits_str', b'},"max_frag_hits":'),
                    DecimalIntegerValueModelElement('max_frag_hits'),
                ]),
                SequenceModelElement('tcp', [
                    FixedDataModelElement('sessions_str', b'},"tcp":{"sessions":'),
                    DecimalIntegerValueModelElement('sessions'),
                    FixedDataModelElement('ssn_memcap_drop_str', b',"ssn_memcap_drop":'),
                    DecimalIntegerValueModelElement('ssn_memcap_drop'),
                    FixedDataModelElement('pseudo_str', b',"pseudo":'),
                    DecimalIntegerValueModelElement('pseudo'),
                    FixedDataModelElement('pseudo_failed_str', b',"pseudo_failed":'),
                    DecimalIntegerValueModelElement('pseudo_failed'),
                    FixedDataModelElement('invalid_checksum_str', b',"invalid_checksum":'),
                    DecimalIntegerValueModelElement('invalid_checksum'),
                    FixedDataModelElement('no_flow_str', b',"no_flow":'),
                    DecimalIntegerValueModelElement('no_flow'),
                    FixedDataModelElement('syn_str', b',"syn":'),
                    DecimalIntegerValueModelElement('syn'),
                    FixedDataModelElement('synack_str', b',"synack":'),
                    DecimalIntegerValueModelElement('synack'),
                    FixedDataModelElement('rst_str', b',"rst":'),
                    DecimalIntegerValueModelElement('rst'),
                    FixedDataModelElement('segment_memcap_drop_str', b',"segment_memcap_drop":'),
                    DecimalIntegerValueModelElement('segment_memcap_drop'),
                    FixedDataModelElement('stream_depth_reached_str', b',"stream_depth_reached":'),
                    DecimalIntegerValueModelElement('stream_depth_reached'),
                    FixedDataModelElement('reassembly_gap_str', b',"reassembly_gap":'),
                    DecimalIntegerValueModelElement('reassembly_gap'),
                    FixedDataModelElement('memuse_str', b',"memuse":'),
                    DecimalIntegerValueModelElement('memuse'),
                    FixedDataModelElement('reassembly_memuse_str', b',"reassembly_memuse":'),
                    DecimalIntegerValueModelElement('reassembly_memuse'),
                    ]),
                SequenceModelElement('detect', [
                    FixedDataModelElement('alert_str', b'},"detect":{"alert":'),
                    DecimalIntegerValueModelElement('alert')
                    ]),
                SequenceModelElement('app_layer', [
                    SequenceModelElement('flow', [
                        FixedDataModelElement('http_str', b'},"app_layer":{"flow":{"http":'),
                        DecimalIntegerValueModelElement('http'),
                        FixedDataModelElement('ftp_str', b',"ftp":'),
                        DecimalIntegerValueModelElement('ftp'),
                        FixedDataModelElement('smtp_str', b',"smtp":'),
                        DecimalIntegerValueModelElement('smtp'),
                        FixedDataModelElement('tls_str', b',"tls":'),
                        DecimalIntegerValueModelElement('tls'),
                        FixedDataModelElement('ssh_str', b',"ssh":'),
                        DecimalIntegerValueModelElement('ssh'),
                        FixedDataModelElement('imap_str', b',"imap":'),
                        DecimalIntegerValueModelElement('imap'),
                        FixedDataModelElement('msn_str', b',"msn":'),
                        DecimalIntegerValueModelElement('msn'),
                        FixedDataModelElement('smb_str', b',"smb":'),
                        DecimalIntegerValueModelElement('smb'),
                        FixedDataModelElement('dcerpc_tcp_str', b',"dcerpc_tcp":'),
                        DecimalIntegerValueModelElement('dcerpc_tcp'),
                        FixedDataModelElement('dns_tcp_str', b',"dns_tcp":'),
                        DecimalIntegerValueModelElement('dns_tcp'),
                        FixedDataModelElement('failed_tcp_str', b',"failed_tcp":'),
                        DecimalIntegerValueModelElement('failed_tcp'),
                        FixedDataModelElement('dcerpc_udp_str', b',"dcerpc_udp":'),
                        DecimalIntegerValueModelElement('dcerpc_udp'),
                        FixedDataModelElement('dns_udp_str', b',"dns_udp":'),
                        DecimalIntegerValueModelElement('dns_udp'),
                        FixedDataModelElement('failed_udp_str', b',"failed_udp":'),
                        DecimalIntegerValueModelElement('failed_udp'),
                        ]),
                    SequenceModelElement('tx', [
                            FixedDataModelElement('http_str', b'},"tx":{"http":'),
                            DecimalIntegerValueModelElement('http'),
                            FixedDataModelElement('smtp_str', b',"smtp":'),
                            DecimalIntegerValueModelElement('smtp'),
                            FixedDataModelElement('tls_str', b',"tls":'),
                            DecimalIntegerValueModelElement('tls'),
                            FixedDataModelElement('dns_tcp_str', b',"dns_tcp":'),
                            DecimalIntegerValueModelElement('dns_tcp'),
                            FixedDataModelElement('dns_udp_str', b',"dns_udp":'),
                            DecimalIntegerValueModelElement('dns_udp'),
                        ])
                    ]),
                SequenceModelElement('flow_mgr', [
                    FixedDataModelElement('closed_pruned_str', b'}},"flow_mgr":{"closed_pruned":'),
                    DecimalIntegerValueModelElement('closed_pruned'),
                    FixedDataModelElement('new_pruned_str', b',"new_pruned":'),
                    DecimalIntegerValueModelElement('new_pruned'),
                    FixedDataModelElement('est_pruned_str', b',"est_pruned":'),
                    DecimalIntegerValueModelElement('est_pruned'),
                    FixedDataModelElement('bypassed_pruned_str', b',"bypassed_pruned":'),
                    DecimalIntegerValueModelElement('bypassed_pruned'),
                    FixedDataModelElement('flows_checked_str', b',"flows_checked":'),
                    DecimalIntegerValueModelElement('flows_checked'),
                    FixedDataModelElement('flows_notimeout_str', b',"flows_notimeout":'),
                    DecimalIntegerValueModelElement('flows_notimeout'),
                    FixedDataModelElement('flows_timeout_str', b',"flows_timeout":'),
                    DecimalIntegerValueModelElement('flows_timeout'),
                    FixedDataModelElement('flows_timeout_inuse_str', b',"flows_timeout_inuse":'),
                    DecimalIntegerValueModelElement('flows_timeout_inuse'),
                    FixedDataModelElement('flows_removed_str', b',"flows_removed":'),
                    DecimalIntegerValueModelElement('flows_removed'),
                    FixedDataModelElement('rows_checked_str', b',"rows_checked":'),
                    DecimalIntegerValueModelElement('rows_checked'),
                    FixedDataModelElement('rows_skipped_str', b',"rows_skipped":'),
                    DecimalIntegerValueModelElement('rows_skipped'),
                    FixedDataModelElement('rows_empty_str', b',"rows_empty":'),
                    DecimalIntegerValueModelElement('rows_empty'),
                    FixedDataModelElement('rows_busy_str', b',"rows_busy":'),
                    DecimalIntegerValueModelElement('rows_busy'),
                    FixedDataModelElement('rows_maxlen_str', b',"rows_maxlen":'),
                    DecimalIntegerValueModelElement('rows_maxlen'),
                    ]),
                SequenceModelElement('dns', [
                    FixedDataModelElement('memuse_str', b'},"dns":{"memuse":'),
                    DecimalIntegerValueModelElement('memuse'),
                    FixedDataModelElement('memcap_state_str', b',"memcap_state":'),
                    DecimalIntegerValueModelElement('memcap_state'),
                    FixedDataModelElement('memcap_global_str', b',"memcap_global":'),
                    DecimalIntegerValueModelElement('memcap_global'),
                    ]),
                SequenceModelElement('http', [
                    FixedDataModelElement('memuse_str', b'},"http":{"memuse":'),
                    DecimalIntegerValueModelElement('memuse'),
                    FixedDataModelElement('memcap_str', b',"memcap":'),
                    DecimalIntegerValueModelElement('memcap'),
                    ]),
                FixedDataModelElement('quote_str', b'}}}')
                ]),
            SequenceModelElement('tls', [
                FixedDataModelElement('tls_str', b'tls",'),
                conn,
                SequenceModelElement('tls', [
                    FixedDataModelElement('subject_str', b',"tls":{"subject":"'),
                    DelimitedDataModelElement('subject', b'"'),
                    FixedDataModelElement('issuerdn_str', b'","issuerdn":"'),
                    DelimitedDataModelElement('issuerdn', b'"'),
                    FixedDataModelElement('fingerprint_str', b'","fingerprint":"'),
                    DelimitedDataModelElement('fingerprint', b'"'),
                    OptionalMatchModelElement('sni',
                        SequenceModelElement('sni', [
                            FixedDataModelElement('sni_str', b'","sni":"'),
                            DelimitedDataModelElement('sni', b'"'),
                            ])
                        ),
                    FixedDataModelElement('version_str', b'","version":"'),
                    DelimitedDataModelElement('version', b'"'),
                    FixedDataModelElement('notbefore_str', b'","notbefore":"'),
                    DelimitedDataModelElement('notbefore', b'"'),
                    FixedDataModelElement('notafter_str', b'","notafter":"'),
                    DelimitedDataModelElement('notafter', b'"'),
                    ]),
                FixedDataModelElement('brack_str', b'"}}')
                ]),
            SequenceModelElement('alert', [
                FixedDataModelElement('alert_str', b'alert",'),
                conn,
                OptionalMatchModelElement('tx_id',
                    SequenceModelElement('tx_id', [
                        FixedDataModelElement('tx_id', b',"tx_id":'),
                        DecimalIntegerValueModelElement('tx_id'),
                        ])),
                SequenceModelElement('alert', [
                    FixedDataModelElement('action_str', b',"alert":{"action":"'),
                    DelimitedDataModelElement('action', b'"'),
                    FixedDataModelElement('gid_str', b'","gid":'),
                    DecimalIntegerValueModelElement('gid'),
                    FixedDataModelElement('signature_id_str', b',"signature_id":'),
                    DecimalIntegerValueModelElement('signature_id'),
                    FixedDataModelElement('rev_str', b',"rev":'),
                    DecimalIntegerValueModelElement('rev'),
                    FixedDataModelElement('signature_str', b',"signature":"'),
                    DelimitedDataModelElement('signature', b'"'),
                    FixedDataModelElement('category_str', b'","category":"'),
                    DelimitedDataModelElement('category', b'"'),
                    FixedDataModelElement('severity_str', b'","severity":'),
                    DecimalIntegerValueModelElement('severity'),
                    FixedDataModelElement('brack_str', b'}')
                    ]),
                http,
                FixedDataModelElement('brack_str', b'}')
                ]),
            ])
        ])

    return model
