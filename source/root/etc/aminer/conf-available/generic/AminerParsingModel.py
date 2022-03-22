"""This module defines a parser for the aminer."""

from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.JsonModelElement import JsonModelElement
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement


def get_model():
    """Return the model."""
    name_alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    alphabet = "!'#$%&\"()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[] °§ß–\n".encode()
    alphabet_with_newline = alphabet + b"\n"
    filename_alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ._-/"

    path = VariableByteDataModelElement("path", filename_alphabet)
    apostrophe = FixedDataModelElement("apostrophe", b"'")
    repeated_path = RepeatedElementDataModelElement("repeated", SequenceModelElement("sequence", [
            apostrophe,
            path,
            apostrophe,
            OptionalMatchModelElement("optional", FixedDataModelElement("comma", b","))
        ]))
    rule = SequenceModelElement("rule", [
        FixedDataModelElement("open_bracket", b"("),
        repeated_path,
        FixedWordlistDataModelElement("close_bracket", [b")->(", b")<-("]),
        repeated_path,
        FixedDataModelElement("close_bracket", b")")
    ])
    expected = SequenceModelElement("expected", [
        DecimalIntegerValueModelElement("actual"),
        FixedDataModelElement("slash", b"/"),
        DecimalIntegerValueModelElement("expected")
    ])
    observed = SequenceModelElement("observed", [
        DecimalIntegerValueModelElement("actual"),
        FixedDataModelElement("slash", b"/"),
        DecimalIntegerValueModelElement("expected")
    ])
    has_outlier_bins_flag = FixedWordlistDataModelElement("has_outlier_bins_flag", [b"true", b"false"])

    model = JsonModelElement("aminer", {
        "_AnalysisComponent": {
            "AnalysisComponentIdentifier": FirstMatchModelElement("first", [
                DecimalIntegerValueModelElement("component_id"),
                FixedDataModelElement("null", b"null")
            ]),
            "AnalysisComponentType": VariableByteDataModelElement("component_type", name_alphabet),
            "AnalysisComponentName": VariableByteDataModelElement("component_name", alphabet),
            "Message": VariableByteDataModelElement("message", alphabet),
            "_PersistenceFileName": VariableByteDataModelElement("persistence_file_name", filename_alphabet),
            "_TrainingMode": FixedWordlistDataModelElement("training_mode", [b"true", b"false"]),
            "_AffectedLogAtomPaths": [VariableByteDataModelElement("affected_log_atom_paths", alphabet)],
            "_AffectedLogAtomValues": [VariableByteDataModelElement("affected_log_atom_value", alphabet)],
            "_Metadata": {
                "TimeFirstOccurrence": DecimalFloatValueModelElement("time_first_occurrence"),
                "TimeLastOccurrence": DecimalFloatValueModelElement("time_last_occurrence"),
                "NumberOfOccurrences": DecimalIntegerValueModelElement("number_of_occurrences")
            },
            "_ParsedLogAtom": {"ALLOW_ALL_KEYS": VariableByteDataModelElement("allow_all_keys", alphabet)},
            "_FeatureList": [{
                "Rule": {
                    "type": VariableByteDataModelElement("type", name_alphabet),
                    "path": path,
                    "_value": VariableByteDataModelElement("value", alphabet),
                    "match_action": VariableByteDataModelElement("match_action", filename_alphabet),
                    "log_total": DecimalIntegerValueModelElement("log_total"),
                    "log_success": DecimalIntegerValueModelElement("log_success")
                },
                "Index": DecimalIntegerValueModelElement("index"),
                "CreationTime": DecimalFloatValueModelElement("creation_time"),
                "LastTriggerTime": DecimalFloatValueModelElement("last_trigger_time"),
                "TriggerCount": DecimalIntegerValueModelElement("trigger_count")
            }],
            "_AnalysisStatus": VariableByteDataModelElement("analysis_status", alphabet),
            "_TotalRecords": DecimalIntegerValueModelElement("total_records"),
            "_HistogramData": [{
                "TotalElements": DecimalIntegerValueModelElement("total_elements"),
                "BinnedElements": DecimalIntegerValueModelElement("binned_elements"),
                "HasOutlierBinsFlag": has_outlier_bins_flag,
                "Bins": {"ALLOW_ALL_KEYS": DecimalIntegerValueModelElement("bin")},
                "BinDefinition": {
                    "Type": FixedWordlistDataModelElement("type", [b"ModuloTimeBinDefinition", b"LinearNumericBinDefinition"]),
                    "LowerLimit": DecimalIntegerValueModelElement("lower_limit"),
                    "BinSize": DecimalIntegerValueModelElement("bin_size"),
                    "BinCount": DecimalIntegerValueModelElement("bin_count"),
                    "OutlierBinsFlag": has_outlier_bins_flag,
                    "BinNames": [
                        SequenceModelElement("bin_names", [
                            FirstMatchModelElement("first", [
                                SequenceModelElement("lower", [
                                    FixedDataModelElement("open_bracket", b"["),
                                    DecimalIntegerValueModelElement("value")
                                ]),
                                FixedDataModelElement("dots", b"...")
                            ]),
                            FixedDataModelElement("hyphen", b"-"),
                            FirstMatchModelElement("first", [
                                SequenceModelElement("upper", [
                                    DecimalIntegerValueModelElement("value"),
                                    FixedDataModelElement("close_bracket", b"]")
                                ]),
                                FixedDataModelElement("dots", b"...")
                            ]),
                        ])
                    ],
                    "ExpectedBinRatio": DecimalFloatValueModelElement("expected_bin_ratio"),
                    "_ModuloValue": DecimalIntegerValueModelElement("modulo_value"),
                    "_TimeUnit": DecimalIntegerValueModelElement("time_unit")
                },
                "PropertyPath": VariableByteDataModelElement("property_path", filename_alphabet),
            }],
            "_ReportInterval": DecimalIntegerValueModelElement("report_interval"),
            "_ResetAfterReportFlag": FixedWordlistDataModelElement("reset_after_report_flag", [b"true", b"false"]),
            "_MissingPaths": [VariableByteDataModelElement("missing_paths", alphabet)],
            "_AnomalyScores": [{
                "Path": path,
                "AnalysisData": {
                    "New": {
                        "N": DecimalIntegerValueModelElement("n"),
                        "Avg": DecimalFloatValueModelElement("avg"),
                        "Var": DecimalFloatValueModelElement("var")
                    },
                    "Old": {
                        "N": DecimalIntegerValueModelElement("n"),
                        "Avg": DecimalFloatValueModelElement("avg"),
                        "Var": DecimalFloatValueModelElement("var")
                    }
                }
            }],
            "_MinBinElements": DecimalIntegerValueModelElement("min_bin_elements"),
            "_MinBinTime": DecimalIntegerValueModelElement("min_bin_time"),
            "_DebugMode": FixedWordlistDataModelElement("debug_mode", [b"true", b"false"]),
            "_Rule": {
                "RuleId": VariableByteDataModelElement("id", filename_alphabet),
                "MinTimeDelta": DecimalIntegerValueModelElement("min_time_delta"),
                "MaxTimeDelta": DecimalIntegerValueModelElement("max_time_delta"),
                "MaxArtefactsAForSingleB": DecimalIntegerValueModelElement("max_artefacts_a_for_single_b"),
                "ArtefactMatchParameters": [
                    path
                ],
                "HistoryAEvents": "EMPTY_ARRAY",
                "HistoryBEvents": "EMPTY_ARRAY",
                "LastTimestampSeen": DecimalFloatValueModelElement("last_timestamp_seen"),
                "correlation_history": {
                    "MaxItems": DecimalIntegerValueModelElement("max_items"),
                    "History": [
                        VariableByteDataModelElement("value", alphabet)
                    ]
                }
            },
            "_CheckResult": [VariableByteDataModelElement("value", alphabet_with_newline)],
            "_NewestTimestamp": DecimalFloatValueModelElement("newest_timestamp")
        },
        "_TotalRecords": DecimalIntegerValueModelElement("total_records"),
        "_TypeInfo": "ALLOW_ALL",
        "_RuleInfo": {
            "Rule": rule,
            "Expected": expected,
            "Observed": observed
        },
        "_LogData": {
            "RawLogData": [VariableByteDataModelElement("raw_log_data", alphabet)],
            "Timestamps": [DecimalFloatValueModelElement("timestamp")],
            "DetectionTimestamp": DecimalFloatValueModelElement("detection_timestamp"),
            "LogLinesCount": DecimalIntegerValueModelElement("lines_count"),
            "_AnnotatedMatchElement": VariableByteDataModelElement("annotated_match_element", alphabet_with_newline),
        },
        "_StatusInfo": {"ALLOW_ALL_KEYS": {
            "CurrentProcessedLines": DecimalIntegerValueModelElement("current_processed_lines"),
            "TotalProcessedLines": DecimalIntegerValueModelElement("total_processed_lines")
        }},
        "_FromTime": DecimalFloatValueModelElement("from_time"),
        "_ToTime": DecimalFloatValueModelElement("to_time"),
        "_DebugLog": [OptionalMatchModelElement("optional", VariableByteDataModelElement("debug_log", alphabet))]
    }, "_")
    return model
